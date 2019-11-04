import os
from interval import *
from ast import *
from resources import *

          
class Architecture:

	GLOBAL = 1 			#NOT IN USE
	CHECK = 1 			#NOT IN USE
	AXIOM = 2			#NOT IN USE
	EXISTENCE = 1		#NOT IN USE
	ABSENCE = 2			#NOT IN USE
	RESPONSE = 3		#NOT IN USE
	REQUIREMENT = 4		#NOT IN USE
	REFERENCE = -1		#NOT IN USE

	ros_model = ("abstract sig Node {\n" +
			"\tsubscribes: set Topic,\n" +
			"\tadvertises: set Topic,\n" +
			"\tvar inbox : set Message,\n" +
			"\tvar outbox : set Message\n" +
			"}\n\n" +
			"abstract sig Topic {}\n\n" +
			"sig Message {\n" +
			"\ttopic : one Topic,\n" +	
			"\tvalue : one  Value\n" +
			"}\n\n" +
			"abstract sig Value {}\n\n" +
			"fact Messages {\n\n" +
			"\tall n : Node | always {\n"			
			"\t\tn.inbox.topic in n.subscribes\n" +
			"\t\tn.outbox.topic in n.advertises\n" +
			"\t}\n" +
			"\tall m : Message, t: m.topic | always {\n" + 
			"\t\tm in Node.outbox implies (all n : subscribes.(m.topic) | eventually (m in n.inbox and m.topic = t))\n" +
			"\t}\n" +
			"\talways {\n" +
			"\t\tall m : Node.outbox | eventually m not in Node.outbox\n" +
			"\t}\n" 
			"\tall m : Message, t: m.topic | always{\n" +	
			"\t\tm in Node.inbox implies (some n : advertises.(m.topic) | before once (m in n.outbox and m.topic = t))\n" + 
			"\t}\n" +
			"\talways{\n" +
			"\t\tall n1: Node, m: n1.inbox |\n" + 
			"\t\t\tbefore once (some n0: advertises.(m.topic), m0: n0.outbox |  (m0 = m) and (m0.topic = m.topic))\n"+ 
			"\t}\n\n"+
			"}\n\n" +
			"fact init {\n" +
			"\tno (outbox + inbox)\n" +
			"}\n\n")

	def __init__(self,config_name,nodes,topics,properties=None,meta=None):
		# Structure
		self.config_name = config_name	# Configuration Name
		self.meta = self.ros_model if meta is None else meta
		self.__topics = dict()			# set Topic 
		self.__values = dict()			# set Value
		self.__nodes = dict()			# set Node
		self.__create_structure(nodes,topics)
		# Behaviour
		self.pc = 0									# Model Property Counter
		self.__fields = dict()						# Valid Field Name
		self.__prop_el_map = dict() 				# Prop_Name : Property
		self.__create_axioms(nodes)					
		self.__properties = self.__create_properties(properties,self.CHECK)
		# Computing Scopes
		self.value_scope = 4
		self.message_scope = 9
		self.time_scope = 10
		# Reducing Structure
		self.prune_structure()
	

	# ResourceCollection [Node], ResourceCollection [Topic] -> Void
	def __create_structure(self,nodes,topics):	
		# Extracting Topics and Root Values
		for t in topics:
			name = str(t.rosname.full)			
			if name.__contains__('?') is True:			#Ignore Unknown Topics
				continue
			else:
				topic_obj = Topic(t) 
				self.__topics.update({name: topic_obj})
			if t.type not in self.__values.keys():		#Update Root Values	
				value_obj = Value(t.type)
				self.__values.update({t.type:value_obj})
		# Extracting Nodes	
		for n in nodes:	
			name = str(n.rosname.full)			
			if name.__contains__('?') is True:			#Ignore Unknown Nodes
				continue			
			node_obj = Node(n)			
			self.__nodes.update({n.rosname.full : node_obj})











	#HplFieldReference, String -> Boolean + Exception
	def __validate_field(self,f,topic):
		if topic in self.__fields.keys():
			valid_field = self.__fields[topic]
			if f.token == valid_field.token:
				return True
			else:
				print("Unsupported Field Use")
				raise Exception('Unsupported Field Use.')
		else:
			self.__fields.update({topic:f})
			return True

	#Hpl_Value , String -> String + self.REFERENCE + Exception
	def __validate_value(self,hpl_value,topic):	
		is_set = False
		#References
		if hpl_value.is_reference:
			self.__validate_field(hpl_value,topic)
			return is_set, [self.REFERENCE]
		
		#Literals
		if hpl_value.is_literal:
			topic_obj = self.__topics[topic]
			message_type = topic_obj.message_type
			root_value_obj = self.__values[message_type]

			#Literal Numbers
			real_value = hpl_value.value
			if isinstance(real_value, (int,long,float)):
				if isinstance(root_value_obj,Num):
					sub_signature_name = root_value_obj.signature + "_" + str(int(real_value))
					root_value_obj.add_extension(sub_signature_name,
												interval(real_value))
					return is_set, [sub_signature_name]
				else:
					signature = root_value_obj.signature		
					new_root_value_obj = Num(signature,message_type)
					sub_signature_name = signature + "_" + str(int(real_value))
					new_root_value_obj.add_extension(sub_signature_name,
													interval(real_value))
					self.__values.update({message_type: new_root_value_obj})
					return is_set, [sub_signature_name]

			#Literal Booleans
			if isinstance(real_value, bool):
				print("Boolean Values Are Unsupported.")
				raise Exception ('Boolean Values Are Unsupported.')
		
			# UNTESTED PATH
			#Literal Strings
			if isinstance(real_value, str):
				real_value = str(hpl_value.value)		 ## String in String
				real_value = real_value.replace('\"','') ## String
				if isinstance(root_value_obj,String):
					sub_signature_name = root_value_obj.signature + "_" + real_value
					root_value_obj.add_extension(sub_signature_name,real_value)
					return is_set, [sub_signature_name]
				else:
					signature = root_value_obj.signature		
					new_root_value_obj = String(signature,message_type)
					sub_signature_name = signature + "_" + real_value
					new_root_value_obj.add_extension(sub_signature_name,real_value)
					self.__values.update({message_type: new_root_value_obj})
					return is_set, [sub_signature_name]

		# Range
		if hpl_value.is_range:
			topic_obj = self.__topics[topic]
			message_type = topic_obj.message_type
			root_value_obj = self.__values[message_type]
			

			lower = hpl_value.lower_bound
			upper = hpl_value.upper_bound
			
			if lower.is_reference or upper.is_reference:
				print("Unsupported Use of References.")
				raise Exception ('Unsupported Use of References.')
			lower_value = lower.value
			upper_value = upper.value
			if isinstance(root_value_obj,Num):
				sub_signature_name = (root_value_obj.signature + "_" + str(int(lower_value)) + "_" +
									str(int(upper_value)))
				root_value_obj.add_extension(sub_signature_name,
											interval([lower_value,upper_value]))
				return is_set, [sub_signature_name]
			else:
				signature = root_value_obj.signature
				new_root_value_obj = Num(signature,message_type)
				sub_signature_name = (root_value_obj.signature + "_" + str(int(lower_value)) + "_" +
									str(int(upper_value)))
				new_root_value_obj.add_extension(sub_signature_name,
												interval([lower_value,upper_value]))
				self.__values.update({message_type: new_root_value_obj})
				return is_set, [sub_signature_name]
			

		#Sets
		if hpl_value.is_set: 
			topic_obj = self.__topics[topic]
			message_type = topic_obj.message_type
			root_value_obj = self.__values[message_type]
			values = hpl_value.values
			nums = (filter(lambda x: isinstance(x.value,(int,long,float)), values) == values)
			if nums == True:
				sub_signature_names = []
				for v in values:
					real_value = v.value
					if isinstance(root_value_obj,Num):
						sub_signature_name = root_value_obj.signature + "_" + str(real_value)
						root_value_obj.add_extension(sub_signature_name,interval(real_value))
						sub_signature_names.append(sub_signature_name)
					else:
						signature = root_value_obj.signature		
						new_root_value_obj = Num(signature,message_type)
						sub_signature_name = signature + "_" + str(real_value)
						new_root_value_obj.add_extension(sub_signature_name,
														interval(real_value))
						self.__values.update({message_type: new_root_value_obj})
						sub_signature_names.append(sub_signature_name)

				return True, sub_signature_names

			elif strings:
				sub_signature_names = []
				for v in values:
					real_value = v.value
					if isinstance(root_value_obj,String):
						sub_signature_name = root_value_obj.signature + "_" + real_value
						root_value_obj.add_extension(sub_signature_name,real_value)
						sub_signature_names.append(sub_signature_name)
					else:
						signature = root_value_obj.signature		
						new_root_value_obj = String(signature,message_type)
						sub_signature_name = signature + "_" + real_value
						new_root_value_obj.add_extension(sub_signature_name,real_value)
						self.__values.update({message_type: new_root_value_obj})
						sub_signature_names.append(sub_signature_name)
				return True, sub_signature_names

			else:
				raise Exception('Set Type is Unsupported.')




	def __validate_operator(self,op):
		if op in ["!=","=","in","not in"]:
			return True
		else:
			print("Unsupported Operator Use.")
			raise Exception('Unsupported Operator Use.')

	

	# ecd -> HplEvent
	def __extract(self,ecd):	
		if len(ecd.chains) < 2:
			if len(ecd.chains[0].events) < 2:
				return ecd.chains[0].events[0]
		else:
			return None

	# Creating Observable_Existence
	def __create_Existence(self,event):
		hpl_event = self.__extract(event)
		if hpl_event is not None:
			# Simple Event
			action = hpl_event.event_type	# int
			topic = str(hpl_event.topic) 	# Token
			
			#Validate Message_Filters and Create Conditions:
			hpl_field_conditions = hpl_event.msg_filter.conditions
			conditions = []
			for c in hpl_field_conditions:
				self.__validate_field(c.field,topic)
				self.__validate_operator(c.operator)
				is_set, vl = self.__validate_value(c.value,topic)
				for v in vl:
					new_condition = Condition("m0",c.operator,v)
					conditions.append(new_condition)

			#Create Event:
			event = Event(action,topic,conditions,is_set)
			#Create Observable:
			t = self.EXISTENCE
			observable = Observable(t,event)
			return observable




	def __create_Absence(self,event):
		hpl_event = self.__extract(event)
		if hpl_event is not None:
			# Simple Event
			action = hpl_event.event_type
			topic = str(hpl_event.topic) 	# Token
			
			#Validate Message_Filters and Create Conditions:
			hpl_field_conditions = hpl_event.msg_filter.conditions
			conditions = []
			for c in hpl_field_conditions:
				self.__validate_field(c.field,topic) 
				self.__validate_operator(c.operator)
				is_set, vl = self.__validate_value(c.value,topic)
				for v in vl:
					new_condition = Condition("m0",c.operator,v)
					conditions.append(new_condition)

			#Create Event:
			is_set = not is_set		# Because the Absence formula needs to be negated
			event = Event(action,topic,conditions,is_set)
			#Create Observable:
			t = self.ABSENCE
			observable = Observable(t,event)
			return observable

	def __create_Cause(self,event0,event1):
		hpl_event0 = self.__extract(event0)	# Trigger
		hpl_event1 = self.__extract(event1)	# Behaviour

		if hpl_event0 is not None and hpl_event1 is not None:
			# Trigger
			action = hpl_event0.event_type
			topic = str(hpl_event0.topic)
			hpl0_field_conditions = hpl_event0.msg_filter.conditions
			conditions = []
			for c in hpl0_field_conditions:
				self.__validate_field(c.field,topic)
				self.__validate_operator(c.operator)
				is_set, vl = self.__validate_value(c.value,topic)
				for v in vl:
					new_condition = Condition("m0",c.operator,v)
					conditions.append(new_condition)
			event0 = Event(action,topic,conditions,is_set,alias=hpl_event0.alias)

			#Behaviour
			action = hpl_event1.event_type
			topic = str(hpl_event1.topic)
			hpl1_field_conditions = hpl_event1.msg_filter.conditions
			conditions1 = []
			for c in hpl1_field_conditions:
				self.__validate_field(c.field,topic)
				self.__validate_operator(c.operator)
				is_set, vl = self.__validate_value(c.value,topic) 

				for v in vl:
					if v == self.REFERENCE:
						new_condition = Condition("m1",c.operator,"m0")
					else:
						new_condition = Condition("m1",c.operator,v)
					conditions1.append(new_condition)
			
			event1 = Event(action,topic,conditions1,is_set)

			#Create Observable
			t = self.RESPONSE
			observable = Observable(t,event1,trigger=event0)
			return observable


	def __extract_triggers(self,ecd):

		if len(ecd.chains) == 2:
			first_event = ecd.chains[0].events[0]
			second_event = ecd.chains[1].events[0]
			events = [first_event,second_event]
			return events
		elif len(ecd.chains) == 1:
			events = [ecd.chains[0].events[0]]
			return events
		else:
			return None

	# Refactoring
	def __create_Require(self,event0,event1):
		hpl_event0 = self.__extract(event0) #Behaviour

		triggers = self.__extract_triggers(event1)

		if hpl_event0 is not None and triggers is not None:
			#Behaviour
			action = hpl_event0.event_type
			topic = str(hpl_event0.topic)
			hpl0_field_conditions = hpl_event0.msg_filter.conditions
			conditions = []
			for c in hpl0_field_conditions:
				self.__validate_field(c.field,topic)
				self.__validate_operator(c.operator)
				is_set, vl = self.__validate_value(c.value,topic)
				for v in vl:
					new_condition = Condition("m1",c.operator,v)
					conditions.append(new_condition)
			
			event1 = Event(action,topic,conditions,is_set,alias=hpl_event0.alias)

			trigger_events = []
			count = 1
			for t in triggers:
				count = count + 1
				hpl_event1 = t

			#Trigger
				action = hpl_event1.event_type
				topic = str(hpl_event1.topic)
				hpl1_field_conditions = hpl_event1.msg_filter.conditions
				conditions1=[]
				for c in hpl1_field_conditions:
					self.__validate_field(c.field,topic)
					self.__validate_operator(c.operator)
					is_set, vl = self.__validate_value(c.value,topic)
					for v in vl:
						if v==self.REFERENCE:
							new_condition = Condition("m0",c.operator,"m1")
						else:
							new_condition = Condition("m0",c.operator,v)
						conditions1.append(new_condition)
			
				event0 = Event(action,topic,conditions1,is_set)
				trigger_events.append(event0)

			#Create Observable
			t = self.REQUIREMENT
			observable = Observable(t,event1,trigger=trigger_events)
			return observable


	# HplProperty -> Property + Exception		
	def __conversion(self,p,t=None):
		scope_type = p.scope.scope_type
		if scope_type == self.GLOBAL:
			if t==self.CHECK or t==self.AXIOM:		
				o = p.observable 
				pattern = o.pattern		
				if pattern == self.EXISTENCE:
					event = o.behaviour
					observable = self.__create_Existence(event)
					pr = Property(self.pc,t,observable)
					# Mapping Electrum Property Name to HplProperty 
					p_name = "prop_" + str(self.pc)
					self.__prop_el_map.update({p_name:p})

					if t == self.CHECK:
						self.pc = self.pc + 1
					return pr				
				if pattern == self.ABSENCE: 	  
					event = o.behaviour
					observable = self.__create_Absence(event)
					pr = Property(self.pc,t,observable)
					# Mapping Electrum Property Name to HplProperty 
					p_name = "prop_" + str(self.pc)
					self.__prop_el_map.update({p_name:p})
					if t == self.CHECK:
						self.pc = self.pc + 1
					return pr

				if pattern == self.RESPONSE:	#Event Causes Event
					event1 = o.behaviour
					event0 = o.trigger	
					observable = self.__create_Cause(event0,event1)	
					pr = Property(self.pc,t,observable)
					# Mapping Electrum Property Name to HplProperty 
					p_name = "prop_" + str(self.pc)
					self.__prop_el_map.update({p_name:p})
					if t == self.CHECK:
						self.pc = self.pc + 1
					return pr				
				if pattern == self.REQUIREMENT: #Event Requires Event
					event0 = o.behaviour
					event1 = o.trigger
					observable = self.__create_Require(event0,event1)
					pr = Property(self.pc,t,observable)
					# Mapping Electrum Property Name to HplProperty 
					p_name = "prop_" + str(self.pc)
					self.__prop_el_map.update({p_name:p})
					if t == self.CHECK:
						self.pc = self.pc + 1
					return pr
			else: 
				print("Property Type Undeclared")
				raise Exception('Property Type Undeclared.') 				
		else:
			print("Unsupported Property")
			raise Exception('Unsupported Property.')
		



	# [HplProperty] -> [Property] + Exception
	def __create_properties(self,properties,t):
		if properties is None:
			return []
		else:
			return map ((lambda x : self.__conversion(x,t)) , properties)

	# [HplProperty] -> Void
	def __create_axioms(self,nodes):
		for resource in nodes:
			node = resource.node
			properties = node.hpl_properties
			if properties != []:
				pl = self.__create_properties(properties,self.AXIOM)
				node_obj = self.__nodes[resource.rosname.full]
				node_obj.add_axioms(pl)

	








	def delete_topic(self,t):
		# Maintaining node coherency
		for k in self.__nodes.keys():
			node = self.__nodes[k]
			if t.signature in node.subscribes:
				node.subscribes.remove(t.signature)
			if t.signature in node.advertises:
				node.advertises.remove(t.signature)
		# Deleting Topic Object
		mt = t.name
		del self.__topics[mt]
		return

	def delete_value(self,v):
		self.__values.pop(v)

	def delete_node(self,k):
		self.__nodes.pop(k)


	def prune_structure(self):
		subscribers = []
		advertises = []
		for k in self.__nodes.keys():
			node = self.__nodes[k]
			subscribers = subscribers + node.subscribes
			advertises = advertises + node.advertises

		# Delete Dead Topics
		for k in self.__topics.keys():
			# Extra condition (if the topic is used in property or axiom, 'continue')
			topic = self.__topics[k]
			topic_name = topic.signature
			if (topic_name not in subscribers) or (topic_name not in advertises): 
				self.delete_topic(topic)

	
		# Delete Dead Values
		values = self.__values.keys()
		for k in self.__topics.keys():
			mt = self.__topics[k].message_type
			if mt in values:
				values.remove(mt)

		dead_values = values
		for v in dead_values:
			self.delete_value(v)
		# Delete Dead Nodes
		for k in self.__nodes.keys():
			node = self.__nodes[k]
			if node.subscribes == [] and node.advertises == []:
				self.delete_node(k)
		
		return
	




















	# Auxiliary Methods
	# Signature_Name -> Rosname
	def get_rosname(self,n):
		for k in self.__nodes.keys():
			if n == self.__nodes[k].signature:
				return k
		for k in self.__topics.keys():
			if n == self.__topics[k].signature:
				return k
		for k in self.__values.keys():
			if n == self.__values[k].signature:
				return k


	def get_bottom_range(self,root_v,l):
		if isinstance(root_v,Num):
			# is_num
			v = root_v.get_smallest_from(l)
			return v
		else:
			#is_string
			#s = l[0]
			#v = root_v.get_string_value(s)
			#TODO
			return None


	def get_field_by_value(self,root_v):
		print("1")
		m_t = root_v.message_type
		print("m_t: " +str(m_t))
		print("2")
		l_t =  self.__fields.keys()
		print("3")
		topic = ""
		for t in l_t:
			print("c_t: " + self.__topics[t].message_type)
			m_t_c = self.__topics[t].message_type 
			m_t_c = m_t_c.replace('/','_')
			if m_t_c == m_t:
				topic = t
				return self.__fields[topic]
		# Return field
		return "FOO"			# TODO			


	def get_root_value(self,st):
		print(str(st))
		print("will try to get root value")
		value_abs_name = st.strip()
		for k in self.__values:
			key_value = k.replace('/','_')
			if key_value == value_abs_name:
				print("has got the root value")
				return self.__values[k]

	def get_nodes(self):
		return self.__nodes
	#String -> HplProperty + None
	def get_hpl_prop(self,prop_name):
		prop_name = prop_name.strip()
		if prop_name in self.__prop_el_map.keys():
			p = self.__prop_el_map[prop_name]
			return p.__str__()
		else:
			return None


	def to_abstract_name(self,name):
		return name.replace('/','_')










	def spec(self):
		axioms = False
		module_name = "module " + self.config_name + "\n\n"
		spec = module_name + self.ros_model
		spec += "------- Values -------\n\n"
		for k in self.__values.keys():
			value_obj = self.__values[k]	
			spec += value_obj.spec()
		spec += "------- Topics -------\n\n"
		for k in self.__topics.keys():
			topic_obj = self.__topics[k]
			spec += topic_obj.spec()
		spec += "\n------- Nodes -------\n\n"
		for k in self.__nodes.keys():
			node_obj = self.__nodes[k]
			spec += node_obj.spec()
			if node_obj.has_axioms():
				axioms = True

		if axioms == True:
			spec += "\n------- Behaviour -------\n\n"
			for k in self.__nodes.keys():
				node_obj = self.__nodes[k]
				if node_obj.has_axioms():
					spec += node_obj.behaviour_facts()

		if self.__properties != []:
			spec += "\n------- Properties -------\n\n"
			for p in self.__properties:
				spec += (p.spec() + "for 4 but exactly " + 
						str(self.value_scope) + " Value, " + str(self.message_scope) + " Message, exactly " + 
						str(self.time_scope) +" Time\n\n")

		return spec


	# Testing Method
	def debug_properties(self):
		props = self.__properties
		count = 1
		for p in props:
			print("Property " + str(count) + " SPEC:")
			print(p.debug_print())
			++count