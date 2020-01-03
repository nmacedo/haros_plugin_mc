import os
from configuration import *
import yaml

class Analyzer(object):
	def __init__(self, c_name, nodes, topics, properties=None):
		module_name = "module " + str(c_name) + "\n\n"
		meta_model, scopes = self.load_configuration()
		self.configuration = Configuration(c_name, nodes, topics,scopes, properties=properties)
		self.specification = (module_name + 
							  meta_model + 
							  self.configuration.specification())

	def load_configuration(self):
		scopes = None
		meta_model = None
		with open("/plugin_mc/plugin.yaml") as f:
			data = f.read()
			l = yaml.load(data)
			scopes = l['scope']
		with open("/plugin_mc/meta.ele") as f:
			meta_model = f.read()
		return meta_model, scopes
