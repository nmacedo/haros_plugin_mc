from interval import *
from ast import *

class Value:
	def __init__(self,message_type):
		self.message_type = message_type
		self.signature = message_type.replace('/','_')

	def spec(self):
		declaration = ("abstract sig " + self.signature +
				" extends Value {}\n\n")
		return declaration

# Numbers
class Num(Value): 
	def __init__(self,message_type,signature):
		self.message_type = message_type
		self.signature = message_type.replace('/','_')
		self.concrete_values = dict()	#dict{'electrum_value_name': Interval}
	
	# (Sub_Signature_Name, Interval) -> Void	
	def add_extension(self,sub_name,interval_obj):
		if sub_name not in self.concrete_values.keys():
			self.concrete_values.update({sub_name:interval_obj})
	
	def isliteral(self,sub_name):			#TODO
		if sub_name in self.concrete_values.keys():
			interval = self.concrete_values[sub_name]
			if interval.inf == interval.sup:
				return True
		return False

	def __independence_list(self,signature):
		independence_list = []
		value = self.concrete_values[signature]
		for key in self.concrete_values.keys():
			if len(self.concrete_values[key] & value) == 0:
				independence_list.append(key)
		return independence_list

	def __full_inclusion_list(self,signature):
		inclusion_list = []
		value = self.concrete_values[signature]
		for key in self.concrete_values.keys():
			if value in self.concrete_values[key] and signature != key:
				inclusion_list.append(key)
		return inclusion_list

	def __is_singleton(self,signature):
		value = self.concrete_values[signature]
		return (len(value) == 1) and (value[0].inf == value[0].sup)

	def spec(self):
		s = ("abstract sig " + self.signature +
				" extends Value {}\n\n")
		independence_aux = ""
		inclusion_aux = ""
		singleton_aux = ""
		
		# Concrete Values
		for signature in self.concrete_values.keys():
			s += "sig " + signature + " in " + self.signature + " {}\n\n"

		# Full independence fact
		for signature in self.concrete_values.keys():
			independence_list = self.__independence_list(signature)
			if independence_list != []:
				independence_aux += ("\t no " + signature + " & (" + 
									' + '.join(independence_list) + ")\n")
		if len(independence_aux)>0:
			s += ("fact Independence {\n" + independence_aux + "}\n\n")
		#UNTESTED
		# Full inclusion fact
		for signature in self.concrete_values.keys():
			inclusions_list = self.__full_inclusion_list(signature)
			if inclusions_list != []:
				inclusion_aux += ("\t" + signature + " in (" + 
							' + '.join(inclusions_list) + ")\n")
		if len(inclusion_aux)>0:
			s += "fact Inclusions {\n" + inclusion_aux + "}\n\n"
		
		# Singletons fact
		for signature in self.concrete_values.keys():
			if self.__is_singleton(signature):
				singleton_aux +="\t lone " + signature + "\n"
		if len(singleton_aux)>0:
			s += "fact Singletons {\n" + singleton_aux + "}\n\n"
		return s


#Strings
class String(Value):
	def __init__(self,message_type,signature):
		self.message_type = message_type
		self.signature = message_type.replace('/','_')
		self.concrete_values = {}

	#(Sub_Signature_Name, String) -> Void
	def add_extension(self,sub_name,s):
		if sub_name not in self.concrete_values.keys():
			self.concrete_values.update({sub_name:s})

	def to_electrum(self):						
		s = ("abstract sig " + self.signature +
			" extends Value {}\n\n")
		values = concrete_values.keys()
		for signature in self.values:	
			spec += "lone sig " + signature + " extends " + self.signature + " {}\n\n"
		return spec



class Topic:
	def __init__(self,topic):
		self.signature = topic.rosname.full.replace('/','_')
		self.signature = self.signature.replace('?','UNKNOWN')
		self.name = topic
		self.value = topic.type.replace('/','_')
		self.message_type = topic.type
	
	def spec(self):
		declaration = ("one sig " + self.signature + " extends Topic{}\n")
		message_fact = ("fact " + self.signature + "_messages {\n" +
				"\tall m:topic." + self.signature + " | m.value in " + 
				self.value + "\n}\n\n")
		return (declaration + message_fact)


class Node:
	def __init__(self,node):
		self.signature = node.rosname.full.replace('/','_')
			
		subscribers = node.subscribers
		subscribers = map(lambda x: x.rosname.full.replace('/','_') , subscribers)
		subscribers = map(lambda x: x.replace('~',str(self.signature)) , subscribers)
		subscribers = filter(lambda x: not x.__contains__("?"), subscribers)
		self.subscribes = subscribers

		publishers = node.publishers
		publishers = map(lambda x: x.rosname.full.replace('/','_') , publishers)
		publishers = map(lambda x: x.replace('~',self.signature) , publishers)
		publishers = filter(lambda x: not x.__contains__("?"), publishers)
		self.advertises = publishers

		self.axioms = []

	def behaviour_facts(self):
		s = ("fact " + str(self.signature) + "_Behaviour {\n\n\t")
		for axiom in self.axioms:
			s +=(axiom.spec() + "\n\t")
		s += "\n}\n"
		return s
	def has_axioms(self):
		return (self.axioms != [])
	
	def add_axioms(self,p):
		self.axioms = self.axioms + p
	
	def spec(self):
		subscribes = "none" if (self.subscribes == []) else ' + '.join(self.subscribes)
		advertises = "none" if (self.advertises == []) else ' + '.join(self.advertises)
          	declaration = ("one sig " +
				self.signature + " extends Node{}{\n" +
				"\tsubscribes = " + subscribes +
				"\n\tadvertises = " + advertises + "\n}\n\n") 
		return declaration
