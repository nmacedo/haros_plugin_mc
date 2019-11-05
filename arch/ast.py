
class Condition:
	def __init__(self,lhs,operator,rhs):
		self.lhs = lhs
		self.operator = operator
		self.rhs = rhs
	
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

	def spec(self):
		s = self.relation.join(map(lambda x: x.spec(), self.conditions))
		return s


class Observable:
	EXISTENCE = 1
	ABSENCE = 2
	RESPONSE = 3
	REQUIREMENT = 4
	def __init__(self,pattern,behaviour,trigger=None):
		
		self.pattern = pattern
		self.behaviour = behaviour #Event
		self.trigger = trigger 	   #Should appear 


	def spec(self): 
		if self.pattern == self.EXISTENCE:#globally some ==> always some
			behaviours_specs = []
			for e in self.behaviour:
				spec = ("(some m0: Node.outbox & " + "topic."+ e.topic.replace('/','_') +" | (" + e.spec() + "))")
				behaviours_specs.append(spec)
			s = "(" + " or ".join(behaviours_specs) + ")"
			return s

		if self.pattern == self.ABSENCE:  #globally no ==> always no
			behaviours_specs = []
			for e in self.behaviour:
				spec = "(no m0: Node.outbox & " + "topic."+e.topic.replace('/','_') +" | (" + e.spec() + "))"
				behaviours_specs.append(spec)
			s = "(" + " or ".join(behaviours_specs) + ")"
			return s

		if self.pattern == self.REQUIREMENT: #globally e1 requires e0 ==> always e1 implies before once e0
			trigger_specs = []
			for t in self.trigger:
				spec = "(some m0: Node.inbox & topic."+t.topic.replace('/','_')+ "| (" + t.spec() + "))"
				trigger_specs.append(spec)
			trigger_spec = "(" + " or ".join(trigger_specs) + ")"

			if len(self.behaviour) < 2:
				if self.behaviour[0].alias is not None:
					s = ("all m1: Node.outbox &  topic." +self.behaviour[0].topic.replace('/','_') +
						" | (" + self.behaviour[0].spec() + ")")
					s += (" \n\t\t\timplies before once (" + trigger_spec + ")")	
					return s
		
			behaviours_specs = []
			for e in self.behaviour:
				spec = ("(some m1: Node.outbox & " + "topic."+e.topic.replace('/','_') +
				" | (" + e.spec() + "))")
				behaviours_specs.append(spec)

			s = "(" + " or ".join(behaviours_specs) + ")"
			s += (" \n\t\t\timplies before once ("+trigger_spec+")")	 
			return s


		if self.pattern == self.RESPONSE:	# globally e0 causes e1 ==> always e1 implies eventually e2
			behaviour_specs = []
			for b in self.behaviour:
				spec = "(some m1: Node.outbox & topic."+b.topic.replace('/','_')+ "| (" + b.spec() + "))"
				behaviour_specs.append(spec)
			behaviour_spec = "(" + " or ".join(behaviour_specs) + ")"

			if len(self.trigger) < 2:
				if self.trigger[0].alias is not None:
					s = ("all m0: Node.inbox &  topic." +self.trigger[0].topic.replace('/','_') +
						" | (" + self.trigger[0].spec() + ")")
					s += (" \n\t\t\timplies eventually (" + behaviour_spec + ")")	
					return s
		
			triggers_specs = []
			for t in self.trigger:
				spec = ("(some m0: Node.inbox & " + "topic."+t.topic.replace('/','_') +
				" | (" + t.spec() + "))")
				triggers_specs.append(spec)
			s = "(" + " or ".join(triggers_specs) + ")"
			s += (" \n\t\t\timplies eventually ("+behaviour_spec+")")	 
			return s	


class Property:
	
	CHECK = 1
	AXIOM = 2

	def __init__(self,pc,t,observable,node=None):
		self.pc = pc
		self.observable = observable
		self.type = t
		self.node = node

	def spec(self):
		if self.type == self.CHECK:
			s = "check prop_" + str(self.pc) + "{\n\t"
			s += "always { " + self.observable.spec() + " }\n"
			s += "} "
			return s
		if self.type == self.AXIOM:
			s = "always { " + self.observable.spec() + " }\n\n"
			return s

