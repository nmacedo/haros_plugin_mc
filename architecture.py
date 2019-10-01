import os

from interval import *
from ast import *
from resources import *

ros_model = ("abstract sig Node{\n" +
                           "\tsubscribes: set Topic,\n" +
                           "\tadvertises: set Topic,\n" +
                           "\tinbox: set Message,\n" +
                           "\toutbox: set Message\n" +
                           "}\n\n" +
                           "abstract sig Topic{}\n\n" +
                           "sig Message{\n" +
                           "\ttopic: one Topic,\n" +
                           "\tvalue: one Value\n"+
                           "}\n\n" +
                           "abstract sig Value{}\n\n")

class Architecture:
	
	GLOBAL = 1
	CHECK = 1
	AXIOM = 2
	EXISTENCE = 1
	ABSENCE = 2
	RESPONSE = 3
	REQUIREMENT = 4
	REFERENCE = -1

	def __init__(self,nodes,topics,properties=None):
		self.pc = 0
		self.__topics = dict()
		self.__values = dict()
		self.__nodes = dict()
		self.__fields = dict()	#dict(Topic:String)
		self.__create_structure(nodes,topics)
		self.__axioms = self.__create_axioms(nodes)		#TODO
		self.__properties = self.__create_properties(properties,self.CHECK)
		#self.prone()			# Prone Architecture  	#TODO
		


	#def prone(self):
		#pass	
	# Testing Method
	def debug_properties(self):
		props = self.__properties
		count = 1
		for p in props:
			print("Property " + str(count) + " SPEC:")
			print(p.debug_print())
			++count

	def __create_structure(self,nodes,topics):
		
		for t in topics:
			name = str(t.rosname.full)
			
			if name.__contains__('?') == True:			#Break Conditions
				continue

			topic_obj = Topic(t) 
			self.__topics.update({t.rosname.full: topic_obj})
			if t.type not in self.__values.keys():
				value_obj = Value(t.type)
				self.__values.update({t.type:value_obj})
		
		for n in nodes:	
			name = str(n.rosname.full)	
			
			if name.__contains__('?'):			#Break Conditions
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
		#References
		if hpl_value.is_reference:
			self.__validate_field(hpl_value,topic)
			return [self.REFERENCE]
		
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
					return [sub_signature_name]
				else:
					signature = root_value_obj.signature		
					new_root_value_obj = Num(signature,message_type)
					sub_signature_name = signature + "_" + str(int(real_value))
					new_root_value_obj.add_extension(sub_signature_name,
													interval(real_value))
					self.__values.update({message_type: new_root_value_obj})
					return [sub_signature_name]

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
					return [sub_signature_name]
				else:
					signature = root_value_obj.signature		
					new_root_value_obj = String(signature,message_type)
					sub_signature_name = signature + "_" + real_value
					new_root_value_obj.add_extension(sub_signature_name,real_value)
					self.__values.update({message_type: new_root_value_obj})
					return [sub_signature_name]

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
				return [sub_signature_name]
			else:
				signature = root_value_obj.signature
				new_root_value_obj = Num(signature,message_type)
				sub_signature_name = (root_value_obj.signature + "_" + str(int(lower_value)) + "_" +
									str(int(upper_value)))
				new_root_value_obj.add_extension(sub_signature_name,
												interval([lower_value,upper_value]))
				self.__values.update({message_type: new_root_value_obj})
				return [sub_signature_name]
			

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

				return sub_signature_names

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
				return sub_signature_names

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
				vl = self.__validate_value(c.value,topic)
				for v in vl:
					new_condition = Condition("m0",c.operator,v)
					conditions.append(new_condition)

			#Create Event:
			event = Event(action,topic,conditions)
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
				vl = self.__validate_value(c.value,topic)
				for v in vl:
					new_condition = Condition("m0",c.operator,v)
					conditions.append(new_condition)

			#Create Event:
			event = Event(action,topic,conditions)
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
				vl = self.__validate_value(c.value,topic)
				for v in vl:
					new_condition = Condition("m0",c.operator,v)
					conditions.append(new_condition)
			event0 = Event(action,topic,conditions,alias=hpl_event0.alias)

			#Behaviour
			action = hpl_event1.event_type
			topic = str(hpl_event1.topic)
			hpl1_field_conditions = hpl_event1.msg_filter.conditions
			conditions1 = []
			for c in hpl1_field_conditions:
				self.__validate_field(c.field,topic)
				self.__validate_operator(c.operator)
				vl = self.__validate_value(c.value,topic) 

				for v in vl:
					if v == self.REFERENCE:
						new_condition = Condition("m1",c.operator,"m0")
					else:
						new_condition = Condition("m1",c.operator,v)
					conditions1.append(new_condition)
			
			event1 = Event(action,topic,conditions1)

			#Create Observable
			t = self.RESPONSE
			observable = Observable(t,event1,trigger=event0)
			return observable

	def __create_Require(self,event0,event1):
		hpl_event0 = self.__extract(event0) #Behaviour
		hpl_event1 = self.__extract(event1) #Trigger

		if hpl_event0 is not None and hpl_event1 is not None:
			
			#Behaviour
			action = hpl_event0.event_type
			topic = str(hpl_event0.topic)
			hpl0_field_conditions = hpl_event0.msg_filter.conditions
			conditions = []
			for c in hpl0_field_conditions:
				self.__validate_field(c.field,topic)
				self.__validate_operator(c.operator)
				vl = self.__validate_value(c.value,topic)
				for v in vl:
					new_condition = Condition("m1",c.operator,v)
					conditions.append(new_condition)
			
			event1 = Event(action,topic,conditions,alias=hpl_event0.alias)

			#Trigger
			action = hpl_event1.event_type
			topic = str(hpl_event1.topic)
			hpl1_field_conditions = hpl_event1.msg_filter.conditions
			conditions1=[]
			for c in hpl1_field_conditions:
				self.__validate_field(c.field,topic)
				self.__validate_operator(c.operator)
				vl = self.__validate_value(c.value,topic)
				for v in vl:
					if v==self.REFERENCE:
						new_condition = Condition("m0",c.operator,"m1")
					else:
						new_condition = Condition("m0",c.operator,v)
					conditions1.append(new_condition)
			
			event0 = Event(action,topic,conditions1)

			#Create Observable
			t = self.REQUIREMENT
			observable = Observable(t,event1,trigger=event0)
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
					p = Property(self.pc,t,observable)
					if t == self.CHECK:
						self.pc = self.pc + 1
					return p				
				if pattern == self.ABSENCE: 	  
					event = o.behaviour
					observable = self.__create_Absence(event)
					p = Property(self.pc,t,observable)
					if t == self.CHECK:
						self.pc = self.pc + 1
					return p

				if pattern == self.RESPONSE:	#Event Causes Event
					event1 = o.behaviour
					event0 = o.trigger	
					observable = self.__create_Cause(event0,event1)	
					p = Property(self.pc,t,observable)
					if t == self.CHECK:
						self.pc = self.pc + 1
					return p				
				if pattern == self.REQUIREMENT: #Event Requires Event
					event0 = o.behaviour
					event1 = o.trigger
					observable = self.__create_Require(event0,event1)
					p = Property(self.pc,t,observable)
					if t == self.CHECK:
						self.pc = self.pc + 1
					return p
			else: 
				print("Property Type Undeclared")
				raise Exception('Property Type Undeclared.') 				
		else:
			print("Unsupported Property")
			raise Exception('Unsupported Property.')
		

	# [HplProperty] -> [Property] + Exception
	def __create_properties(self,properties,t):
		if properties is None:
			print("Properties are None...")
			return []
		else:
			return map ((lambda x : self.__conversion(x,t)) , properties)

	def __create_axioms(self,nodes):
		for resource in nodes:
			node = resource.node
			properties = node.hpl_properties
			if properties != []:
				pl = self.__create_properties(properties,self.AXIOM)
				node_obj = self.__nodes[resource.rosname.full]
				node_obj.add_axioms(pl)




	def spec(self):
		axioms = False
		spec = ros_model
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
				spec += p.spec()

		return spec