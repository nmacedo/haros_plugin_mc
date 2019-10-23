import os
from architecture import *
from electrum import *

class facade(object):
	def __init__(self,name,nodes,topics,properties=None):
		self.architecture = Architecture(name,nodes,topics,properties=properties)
		self.electrum_interface = ElectrumInterface(self.architecture)
		





