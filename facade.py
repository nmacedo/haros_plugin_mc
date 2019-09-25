import os
from architecture import *


class facade(object):
	def __init__(self,name,nodes,topics,properties=None):
		self.configuration_name = name
		self.architecture = Architecture(nodes,topics,properties=properties)
		self.model = self.arch_spec()
		print(self.model)
	
	
	def arch_spec(self):
		module_name = "module " + self.configuration_name + "\n\n"
		return (module_name + 
			self.architecture.spec())




