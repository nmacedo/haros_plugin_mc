from interval import *
from ast import *

# Abstract Interpretation of Message Types.
# ROOT Value (Message Type)
class Value:
	def __init__(self,message_type):
		self.message_type = message_type 				# ROS METAMODEL
		self.signature = message_type.replace('/','_')	# ROS ALLOY

	def spec(self):
		declaration = ("abstract sig " + self.signature +
				" extends Value {}\n\n")
		return declaration

# Numeric Values
class Num(Value): 
	def __init__(self,message_type,signature):
		self.message_type = message_type 			 	# ROS METAMODEL
		self.signature = message_type.replace('/','_')  # ROS ALLOY
		self.concrete_values = dict()					# Signature_Name : Interval()
	
	# (Signature_Name, Interval) -> Void	
	def add_extension(self,sub_name,interval_obj):
		if sub_name not in self.concrete_values.keys():
			self.concrete_values.update({sub_name:interval_obj})
	
	# Signature_Name -> Boolean
	def isliteral(self,sub_name):	
		if sub_name in self.concrete_values.keys():
			interval = self.concrete_values[sub_name]
			if interval.inf == interval.sup:
				return True
		return False

	# [Signature_Name] -> Interval()	
	def get_smallest_from(self,l):
		r = self.concrete_values[l[0]]
		for i in range(1,len(l)):
			if self.concrete_values[l[i]] in r:
				r = self.concrete_values[l[i]]
		return r

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
		self.message_type = message_type  			   # ROS METAMODEL
		self.signature = message_type.replace('/','_') # ROS ALLOY
		self.concrete_values = {}					   # Signature_Name : String

	# Signature_Name -> String
	def get_Value(self,s):
		if s.strip() in self.concrete_values.keys():
			return self.concrete_values[s.strip()]
		else:
			return "String Concrete Value not Found."

	#(Sub_Signature_Name, String) -> Void
	def add_extension(self,sub_name,s):
		if sub_name not in self.concrete_values.keys():
			self.concrete_values.update({sub_name:s})

	def spec(self):						
		s = ("abstract sig " + self.signature +
			" extends Value {}\n\n")
		values = concrete_values.keys()
		for signature in self.values:	
			spec += "lone sig " + signature + " extends " + self.signature + " {}\n\n"
		return spec




# Abstract Interpretation of a Topic RunTime Resource.
class Topic:
	def __init__(self,topic):
		# ROS METAMODEL
		self.name = topic.rosname.full  
		self.message_type = topic.type
		# ROS ALLOY
		self.signature = topic.rosname.full.replace('/','_')
		self.value = topic.type.replace('/','_')
	
	def spec(self):
		declaration = ("one sig " + self.signature + " extends Topic{}\n")
		message_fact = ("fact " + self.signature + "_messages {\n" +
				"\tall m:topic." + self.signature + " | m.value in " + 
				self.value + "\n}\n\n")
		return (declaration + message_fact)

# Abstract Interpretation of a Node RunTime Process.
class Node:
	def __init__(self,node):
		# ROS METAMODEL
		self.rosname = node.rosname.full
		# ROS ALLOY
		self.signature = node.rosname.full.replace('/','_')	
		self.subscribes = self.__clean_data(node.subscribers)
		self.advertises = self.__clean_data(node.publishers)
		self.axioms = []

	def __clean_data(self,l):
		l = map(lambda x: x.rosname.full.replace('/','_') , l)
		l = map(lambda x: x.replace('~',str(self.signature)) , l)
		l = filter(lambda x: not x.__contains__("?"), l)
		return l

	def has_axioms(self):
		return (self.axioms != [])
	
	def add_axioms(self,p):
		self.axioms = self.axioms + p
	
	def behaviour_facts(self):
		s = ("fact " + str(self.signature) + "_Behaviour {\n\n\t")
		for axiom in self.axioms:
			s +=(axiom.spec() + "\n\t")
		s += "\n}\n"
		return s

	def spec(self):
		subscribes = "none" if (self.subscribes == []) else ' + '.join(self.subscribes)
		advertises = "none" if (self.advertises == []) else ' + '.join(self.advertises)
          	declaration = ("one sig " +
				self.signature + " extends Node{}{\n" +
				"\tsubscribes = " + subscribes +
				"\n\tadvertises = " + advertises + "\n}\n\n") 
		return declaration
