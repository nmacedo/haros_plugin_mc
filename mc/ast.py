import re
# Ver como a cena dos valores esta a ser metida na estrutura, e pensar como se vai poder utilizar isto
class ResultCollection():
	def __init__(self):
		self.results = dict()
	
	def add(self,result_obj):
		self.results.update({result_obj.property_name:result_obj})

	def getResults(self):
		return self.results


# Hierarchical object
class ResultObject():
	def __init__(self):
		pass

class UnsatResult(ResultObject):
	def __init__(self,t,property_name,scope):
		self.property_type = t
		self.property_name = property_name
		self.scope = scope
	

class SatResult(ResultObject):
	def __init__(self,t,property_name,scope,instance_obj):
		self.property_type = t
		self.property_name = property_name
		self.scope = scope 					#Scope Object
		self.result = instance_obj
	

class Scope():
	def __init__(self,value,message,time):
		self.value_scope = value
		self.message_scope = message
		self.time_scope = time



class Instance():
	def __init__(self,states):
		self.states = states	#[State]	
	
	

class State():
	def __init__(self,inbox=[],outbox=[],values=[]):
		self.values = dict()	# dict{Message_id : value_name}
		self.inbox = []			# node_name -> Message_id
		self.outbox = []		# node_name -> Message_id
		self.set_values(values)		# Possible BUG here
		self.set_state(inbox,outbox)

	def remove_id(self,s):
		return re.sub(r"\$[0-9]+","",s)
	
	#[(Message_name$id, Value_name$id)] -> Void
	def set_values(self,values):
		for v in values:
			message_id = v[0]
			value_name = v[1]		# Tratar destes valores 
			self.values.update({message_id:value_name})

		
	# Should be refactored
	def set_state(self,inbox,outbox):
		new_inbox = []
		for v in inbox:
			node_name = self.remove_id(v[0])
			message_id = v[1]
			new_inbox.append((node_name,message_id))
		new_outbox = []
		for v in outbox:
			node_name = self.remove_id(v[0])
			message_id = v[1]
			new_outbox.append((node_name,message_id))
		self.inbox = new_inbox
		self.outbox = new_outbox