
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
	
	def __init__(self,action,topic,conditions,alias=None):
		self.action = action
		self.topic = topic
		self.conditions = conditions     #[Condition]
		self.alias = alias

	# Test Method
	def debug_print(self):
		s = "Event:\n\t"
		s += "Topic: " + self.topic + "\n\t"
		s += "Alias: " + str(self.alias) + "\n\t"
		for c in self.conditions:
			s += c.debug_print() + "\n\t"
		return s

	def spec(self):
		s = " or ".join(map(lambda x: x.spec(), self.conditions))
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
		if self.pattern == self.EXISTENCE:
			s = "some m0: " + "topic."+self.behaviour.topic.replace('/','_') +" | (" + self.behaviour.spec() + ")"
			return s
		if self.pattern == self.ABSENCE:
			s = "no m0: " + "topic."+self.behaviour.topic.replace('/','_') +" | (" + self.behaviour.spec() + ")"
			return s
		if self.pattern == self.RESPONSE:
			if self.trigger is not None:
				if self.trigger.alias is None:
					s = ("(some m0:" + "topic."+self.trigger.topic.replace('/','_') +
						" | (" + self.trigger.spec() + "))")
					s += (" \n\t\t\timplies eventually (some m1 : topic."+self.behaviour.topic.replace('/','_') +
						" | (" + self.behaviour.spec() + "))")
					return s
				else:
					# There is an Alias
					# 'all' pattern must be writen 
					s = ("all m0: topic." +self.trigger.topic.replace('/','_') +
						" | (" + self.trigger.spec() + ")")
					s += (" \n\t\t\timplies eventually (some m1: topic."+self.behaviour.topic.replace('/','_') +
						 " | (" + self.behaviour.spec() + ")")
					return s
		if self.pattern == self.REQUIREMENT:
			if self.trigger is not None:
				if self.behaviour.alias is None:
					s = ("(some m1:" + "topic."+self.behaviour.topic.replace('/','_') +
						" | (" + self.behaviour.spec() + "))")
					s += (" \n\t\t\timplies previous once (some m0 : topic."+self.trigger.topic.replace('/','_') +
						" | (" + self.trigger.spec() + "))")
					return s
				else:
					# There is an Alias
					# 'all' pattern must be writen 
					s = ("all m1: topic." +self.behaviour.topic.replace('/','_') +
						" | (" + self.behaviour.spec() + ")")
					s += (" \n\t\t\timplies previous once (some m0: topic."+self.trigger.topic.replace('/','_') +
						 " | (" + self.trigger.spec() + ")")
					return s
					



		


class Property:
	
	CHECK = 1
	AXIOM = 2

	def __init__(self,pc,t,observable,node=None):
		if t==self.AXIOM and node is None:
			raise Exception('Axiom Cannot Be Global')
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
			s += "}\n\n"
			return s





  


