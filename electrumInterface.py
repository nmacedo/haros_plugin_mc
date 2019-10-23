import os
from .arch.architecture import *


class ElectrumInterface(object):
	def __init__(self,conf_name,nodes,topics,properties=None):
		self.architecture = Architecture(conf_name,nodes,topics,properties=properties)
		self.setup()

	def setup(self):
		print("[plugin_mc] Setting up execution environment...")
