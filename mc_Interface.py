import os
from .arch.architecture import *
from .arch.resources import *
from .mc.result import *
from .mc.ast import *
from interval import *
import re
import yaml



class HTML(object):
	def __init__(self):
		return
	def paragraph(self,text):
		return ("<p>" + str(text) + "</p>")
	def item(self,text):
		return ("<li>" + str(text) + "</li>")
	def ol(self,lis):
		return ("<ol>" + str(lis) + "</ol>")
	def header(self,text,size):
		return "<h" + str(size) + ">" + str(text) + "</h" + str(size) + ">"



class MC_Interface(object):
	def __init__(self,conf_name,nodes,topics,properties=None):
		scopes = dict()
		with open("/plugin_mc/plugin.yaml") as f:
			data = f.read()
			l = yaml.load(data)
			scopes = l['scope']
		self.architecture = Architecture(conf_name,nodes,topics,scopes,properties=properties)
		self.run_dir = os.getcwd()
		self.results = None
		self.html = HTML()
		
	def __extract_root(self,v):
		l = re.split(r'(_[0-9]+)',v)
		return l[0]

	def __which_value(self,m,s):
		l = s.values[m]
		r = ""		
		root_value = self.__extract_root(l[0])
		if root_value in l:
			l.remove(root_value)
		root_value_obj = self.architecture.get_root_value(root_value)
		field = self.architecture.get_field_by_value(root_value_obj)
		if isinstance(root_value_obj,String):	# It's String
			string = root_value_obj.concrete_values[l[0]]
			r = str(field) + " = " + str(string)
		else:									# It's Numeric
			smallest_range = self.architecture.get_bottom_range(root_value_obj, l)				
			if isinstance(smallest_range,interval):
				if (smallest_range[0].inf == smallest_range[0].sup):
					r = str(field) + " = " + str(smallest_range[0].inf)
				else:
					r = str(field) + " in " + str(smallest_range[0].inf) + " to " + str(smallest_range[0].sup) 
		return r

	def __which_topic(self,m,s):
		l = s.topics[m]
		topic_name = self.architecture.get_rosname(str(l).strip())
		return topic_name

	def __receive(self,node,pstate,astate):
		p_inbox = filter(lambda x : x[0].strip() == node.strip(), pstate.inbox)
		act_inbox = filter(lambda x : x[0].strip() == node.strip(), astate.inbox)
		p_i = []
		for p in p_inbox:
			p_i.append(p[1])	
		a_i = []
		for p in act_inbox:
			a_i.append(p[1])
		received_messages = []
		for m in p_i:
			if m not in a_i:
				received_messages.append(m)
		received_values = map(lambda x: (self.__which_value(x,pstate),self.__which_topic(x,pstate)), received_messages)
		return received_values


	def __sends(self,node,pstate,astate):
		p_outbox = filter(lambda x : x[0].strip() == node.strip(), pstate.outbox)
		act_outbox = filter(lambda x : x[0].strip() == node.strip(), astate.outbox)
		p_o = []
		for p in p_outbox:
			p_o.append(p[1])
		a_o = []
		for p in act_outbox:
			a_o.append(p[1])
		sent_messages = []
		for m in p_o:
			if m not in a_o:
				sent_messages.append(m)
		sent_values = map(lambda x: (self.__which_value(x,pstate),self.__which_topic(x,pstate)), sent_messages)
		return sent_values


	def __transitions_html(self,node,received_list,sent_list):
		node_name = self.architecture.get_rosname(str(node).strip())	
		html = ""
		if received_list == [] and sent_list == []:
			return html
		for s in sent_list:
			html += self.html.item("The " + str(node_name) + " sends a Message { " + str(s[0]) + " } through the " + str(s[1]) + " Topic")
		for r in received_list:
			html +=	self.html.item("The " + str(node_name) + " receives a Message { " + str(r[0]) + " } through the " + str(r[1]) + " Topic")
		return html


	def __state_to_html(self,pstate,astate,st_n):
		html = ""
		nodes = self.architecture.get_nodes() 										
		nodes = nodes.keys()
		nodes_abst = map(lambda x : self.architecture.to_abstract_name(x), nodes)	
		for node in nodes_abst:
			received_messages = self.__receive(node,pstate,astate) 					
			sent_messages = self.__sends(node,pstate,astate)							
			html += self.__transitions_html(node,received_messages,sent_messages)
		return html

	def __instance_to_html(self,instance):
		html = ""
		states = instance.states

		for i in range(1,len(states)): 
			previous_state = states[i-1]
			actual_state = states[i]
			html += self.__state_to_html(previous_state,actual_state,i)
		
		#Linking the final state with the default initial state
		previous_state = states[len(states)-1]
		actual_state = states[0]
		html += self.__state_to_html(previous_state,actual_state,i)				

		html = self.html.ol(html)
		return html

	def __concrete_name(self,result):
		prop_name = result.property_name
		hpl_name = "'" + self.architecture.get_hpl_prop(str(prop_name)) + "'"
		html = self.html.header("Property: " + str(hpl_name), 4)
		# Scope
		#html += self.html.header("For: " + str(self.architecture.value_scope) + " Values, " +
		#			str(self.architecture.message_scope) + " Messages and " + 
		#			str(self.architecture.time_scope) + " Time",4) 
		return html 

	def __sat_html(self,result):
		html = "<br>"
		html += self.__concrete_name(result)
		html += self.html.paragraph("<strong> Counter-example: </strong>")
		html += self.__instance_to_html(result.result)
		return html


	def __unsat_html(self,result):
		html = "<br>"
		html += self.__concrete_name(result)
		html += self.html.paragraph("<strong> No counter-example </strong> has been found for the given scope.")
		return html

	def __html_aux(self,result):
		if isinstance(result,SatResult):
			return self.__sat_html(result)
		else:
			return None

	# Interface
	def to_html(self,results):
		html_str = ""
		results = results.results.values()
		result_list = []
		for v in results:
			result_list.append(self.__html_aux(v))
		return result_list
		
	def model_check(self):
		with open('/plugin_mc/model.ele','w') as f:
			f.write(self.architecture.spec())	
		cmd = "java -cp /plugin_mc/electrum_pi.jar edu.mit.csail.sdg.alloy4whole.PluginInterface /plugin_mc/model.ele"
		os.system(cmd)
		d = self.run_dir + "/results.txt"
		parser = Parser(d)
		self.results = parser.parse()
		return self.results