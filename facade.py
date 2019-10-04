import os
from architecture import *
from electrum import *

class facade(object):
	def __init__(self,name,nodes,topics,properties=None):
		self.configuration_name = name
		self.architecture = Architecture(nodes,topics,properties=properties)
		# Writting model in /tmp folder
		with open('/tmp/model.ele',"w") as f:
			f.write(self.arch_spec())


	def arch_spec(self):
		module_name = "module " + self.configuration_name + "\n\n"
		return (module_name + 
			self.architecture.spec())

	def mc(self):
		return






