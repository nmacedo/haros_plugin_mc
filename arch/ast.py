
class Condition:
	def __init__(self,lhs,operator,rhs):
		self.lhs = lhs
		self.operator = operator
		self.rhs = rhs
	# Test Method
	def debug_print(self):
		s = "Condition:\n\t"
		s += str(self.lhs) + " " + self.operator + " " + str(self.rhs) 
		return s
	
	def spec(self):
		if self.lhs == "m0" or self.lhs == "m1":
			if self.rhs == "m0" or self.rhs == "m1":
				s= self.lhs + ".value " + self.operator + " " + self.rhs + ".value"
				return s
			else:
				if(self.operator == "="):
					self.operator = "in"
				if(self.operator == "!="):
					self.operator = "not in"
				s = self.lhs + ".value " + self.operator + " " + self.rhs
				return s


class Event:		
	PUBLISH = 1
	def __init__(self,action,topic,conditions,is_set,alias=None):
		self.action = action
		self.topic = topic
		self.conditions = conditions     #[Condition]
		self.alias = alias
		self.relation = " and " if is_set == False else " or "

	# Test Method
	def debug_print(self):
		s = "Event:\n\t"
		s += "Topic: " + self.topic + "\n\t"
		s += "Alias: " + str(self.alias) + "\n\t"
		for c in self.conditions:
			s += c.debug_print() + "\n\t"
		return s

	def spec(self):
		s = self.relation.join(map(lambda x: x.spec(), self.conditions))
		return s


class Observable:	#Trocar nomes de behaviour e Observable	
	EXISTENCE = 1
	ABSENCE = 2
	RESPONSE = 3
	REQUIREMENT = 4
	def __init__(self,pattern,behaviour,trigger=None):
		
		self.pattern = pattern
		self.behaviour = behaviour #Event
		self.trigger = trigger 	   #Should appear 

	# Test Method
	def debug_print(self):
		s = "Oservable:\n\t"
		s += "Pattern: " + str(self.pattern) + "\n\t"
		s += "Behaviour:"
		s += self.behaviour.debug_print()
		return s

	def spec(self): 
		if self.pattern == self.EXISTENCE: #globally some ==> always eventually
			s = ("some (Node.outbox & topic."+self.behaviour.topic.replace('/','_')+")" +
				"implies (some m0: Node.outbox & " + "topic."+self.behaviour.topic.replace('/','_') +" | (" + self.behaviour.spec() + "))")
			return s
		if self.pattern == self.ABSENCE:
			s = "no m0: Node.outbox & " + "topic."+self.behaviour.topic.replace('/','_') +" | (" + self.behaviour.spec() + ")"
			return s
		if self.pattern == self.RESPONSE:
			if self.trigger is not None:
				if self.trigger.alias is None:
					s = ("(some m0: Node.inbox & " + "topic."+self.trigger.topic.replace('/','_') +
						" | (" + self.trigger.spec() + "))")
					s += (" \n\t\t\timplies eventually (some m1 : Node.outbox &  topic."+self.behaviour.topic.replace('/','_') +
						" | (" + self.behaviour.spec() + "))")
					return s
				else:
					# There is an Alias
					# 'all' pattern must be writen 
					s = ("all m0: Node.inbox & topic." +self.trigger.topic.replace('/','_') +
						" | (" + self.trigger.spec() + ")")
					s += (" \n\t\t\timplies eventually (some m1: Node.outbox & topic."+self.behaviour.topic.replace('/','_') +
						 " | (" + self.behaviour.spec() + "))")
					return s
		# Extended to receive trigger event chains
		if self.pattern == self.REQUIREMENT:
			if self.trigger is not None:
				trigger_spec = ""
				
				if isinstance(self.trigger,list):
					trigger_specs = []
					for t in self.trigger:
						spec = "(some m0: Node.inbox & topic."+t.topic.replace('/','_')+ "| (" + t.spec() + "))"
						trigger_specs.append(spec)
					trigger_spec = " or ".join(trigger_specs)
				else:
					trigger_spec = "(some m0: Node.inbox & topic."+self.trigger.topic.replace('/','_')+ "| (" + self.trigger.spec() + "))"

				if self.behaviour.alias is None:
					s = ("(some m1: Node.outbox & " + "topic."+self.behaviour.topic.replace('/','_') +
						" | (" + self.behaviour.spec() + "))")
					s += (" \n\t\t\timplies before once ("+trigger_spec+")")	 
					return s
				else:
					# There is an Alias
					# 'all' pattern must be writen 
					s = ("all m1: Node.outbox &  topic." +self.behaviour.topic.replace('/','_') +
						" | (" + self.behaviour.spec() + ")")
					s += (" \n\t\t\timplies before once (" + trigger_spec + ")")	
					return s
			

class Property:
	
	CHECK = 1
	AXIOM = 2

	def __init__(self,pc,t,observable,node=None):
		self.pc = pc
		self.observable = observable
		self.type = t
		self.node = node
 		
	def debug_print(self):
		s = "Property: \n\t"
		s += "Type: " + str(self.type) + "\n\t"
		s += self.observable.debug_print()
		return s

	def spec(self):
		if self.type == self.CHECK:
			s = "check prop_" + str(self.pc) + "{\n\t"
			s += "always { " + self.observable.spec() + " }\n"
			s += "} "
			return s
		if self.type == self.AXIOM:
			s = "always { " + self.observable.spec() + " }\n\n"
			return s

