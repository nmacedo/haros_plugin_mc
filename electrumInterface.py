import os
from .arch.architecture import *
from .mc.result import *
from .mc.ast import *

class ElectrumInterface(object):
	def __init__(self,conf_name,nodes,topics,properties=None):
		self.architecture = Architecture(conf_name,nodes,topics,properties=properties)
		self.run_dir = os.getcwd()
		self.results = self.model_check()
	
	def model_check(self):
		with open('/plugin_mc/model.ele','w') as f:
			f.write(self.architecture.spec())	
		cmd = "java -cp /plugin_mc/electrum_pi.jar edu.mit.csail.sdg.alloy4whole.PluginInterface /plugin_mc/model.ele"
		os.system(cmd)
		d = self.run_dir + "/results.txt"
		parser = Parser(d)
		results = ResultCollection()
		results = parser.parse()
		return results

		

