import os
from .arch.architecture import *

from .mc.result import *
from .mc.ast import *
from interval import *
import re


class MC_Interface(object):
	def __init__(self,conf_name,nodes,topics,properties=None):
		self.architecture = Architecture(conf_name,nodes,topics,properties=properties)
		print(self.architecture.spec())
		self.run_dir = os.getcwd()
		self.results = None




	def paragraph(self,text):
		return ("<p>" + str(text) + "</p>")

	def hasNumbers(self,string):
		return any(char.isdigit() for char in string)

	def extract_root(self,v):
		l = re.split(r'(_[0-9]+)',v)
		print("value after split: " + str(l))
		return l[0]

	def which_value(self,m,s):
		print("has enter the which_value function")
		print("the m is :" + str(m))
		l = s.values[m]			# Values (root value and extensions)
		print("l is :" + str(l))
		root_value = ""
		for v in l:
			if not self.hasNumbers(v):
				root_value = v
				l.remove(v)		# inplace operator
		# MARTELADO
		if root_value =="" and l != []:
			root_value = self.extract_root(l[0])

		print("the root value is: " + str(root_value))
		root_value_obj = self.architecture.get_root_value(root_value)
		print("ROOT VALUE _ OBJ NAME : " + str(root_value_obj.message_type))
		
		# Need to get the smallest range value of l. and parse it to a string that will be returned
		smallest_range = self.architecture.get_bottom_range(root_value_obj, l)		#TODO
		print("will try to get the field")
		field = self.architecture.get_field_by_value(root_value_obj)			#TODO
		r = ""
		
		# Ou e um intervalo de interiros ou e uma string
		if isinstance(smallest_range,interval):
			if (smallest_range[0].inf == smallest_range[0].sup):
				r = str(field) + " = " + str(smallest_range[0].inf)
			else:
				r = str(field) + " in " + str(smallest_range[0].inf) + " to " + str(smallest_range[0].sup) 
			
		print("R String: " + r)

		return r

	def receive(self,node,pstate,astate):
		p_inbox = filter(lambda x : x[0].strip() == node.strip(), pstate.inbox)
		act_inbox = filter(lambda x : x[0].strip() == node.strip(), astate.inbox)
		p_i = []
		for p in p_inbox:
			p_i.append(p[1])	
		a_i = []
		for p in act_inbox:
			a_i.append(p[1])
		# Received messages
		received_messages = []
		for m in a_i:
			if m not in p_i:
				received_messages.append(m)

		received_values = map(lambda x: self.which_value(x,pstate), received_messages)
		return received_values


	def sends(self,node,pstate,astate):
		p_outbox = filter(lambda x : x[0].strip() == node.strip(), pstate.outbox)
		act_outbox = filter(lambda x : x[0].strip() == node.strip(), astate.outbox)
		p_o = []
		for p in p_outbox:
			p_o.append(p[1])
		a_o = []
		for p in act_outbox:
			a_o.append(p[1])
		# Sent messages
		sent_messages = []
		for m in p_o:
			if m not in a_o:
				sent_messages.append(m)
		
		#return sent_messages
		sent_values = map(lambda x: self.which_value(x,pstate), sent_messages)
		return sent_values

	# returns String html
	def transitions_html(self,node,received_list,sent_list):
		node_name = self.architecture.get_rosname(str(node).strip())	
		html = ""
		if received_list == [] and sent_list == []:
			return html
		for r in received_list:
			html += "<li> The " + str(node_name) + " receives a Message with { " + str(r) + " } </li>"
		for s in sent_list:
			html += "<li> The " + str(node_name) + " sends a Message with { " + str(s) + " }</li>"
		return html

	# State x State x N -> String html
	def state_to_html(self,pstate,astate,st_n):
		html = ""
		print("is in the state_to_html")
		nodes = self.architecture.get_nodes() 										# All the nodes.rosname.full
		print("ok1")
		nodes = nodes.keys()
		print("ok2")
		nodes_abst = map(lambda x : self.architecture.to_abstract_name(x), nodes)	# All the abstract nodes names
		for node in nodes_abst:
			print("ok3")
			received_messages = self.receive(node,pstate,astate) 					# [Message_id]
			print("ok4")
			sent_messages = self.sends(node,pstate,astate)							# [Message_id]
			print("ok5")
			html += self.transitions_html(node,received_messages,sent_messages)
		return html

	# Instance -> String html
	def instance_to_html(self,instance):
		print("is in the instance to html")
		html = ""
		html = "<ol>"
		states = instance.states
		for i in range(1,len(states)): # range change a ver se da mais o ultimo resultado
			previous_state = states[i-1]
			actual_state = states[i]
			html += self.state_to_html(previous_state,actual_state,i)
		html += "</ol>"
		return html

	def concrete_name(self,result):
		print("1")
		prop_name = result.property_name
		print("2")
		hpl_name = "'" + self.architecture.get_hpl_prop(str(prop_name)) + "'"
		print("3")
		html = "<h4> Property: " + str(hpl_name) + "</h4>"
		print("4")
		return html 

	def sat_html(self,result):
		html = "<br>"
		html += self.concrete_name(result)
		print("will go paragraph sat")
		html += self.paragraph("<strong> Counter-example: </strong>")
		print("ok in the instance to html")
		html += self.instance_to_html(result.result)
		print("1000")
		return html

	def unsat_html(self,result):
		print("will tey to get the unsat html")
		html = "<br>"
		html += self.concrete_name(result)
		print("will go paragraph unsat")
		html += self.paragraph("<strong> No counter-example </strong> has been found for the given scope.")
		return html

	def to_html(self,result):
		if isinstance(result,SatResult):
			print("will go sat")
			return self.sat_html(result)
		else:
			print("will go unsat")
			return self.unsat_html(result)

	# .mc.ast.ResultCollection -> htlm String
	def results_to_html(self,results):
		html_str = ""
		results = results.results.values()
		for v in results:
			html_str += self.to_html(v)
		return html_str
		
	# void -> .mc.ast.ResultCollection
	def model_check(self):
		with open('/plugin_mc/model.ele','w') as f:
			f.write(self.architecture.spec())	
		cmd = "java -cp /plugin_mc/electrum_pi.jar edu.mit.csail.sdg.alloy4whole.PluginInterface /plugin_mc/model.ele"
		os.system(cmd)
		d = self.run_dir + "/results.txt"
		parser = Parser(d)
		results = ResultCollection()
		results = parser.parse()
		self.results = results
		return results