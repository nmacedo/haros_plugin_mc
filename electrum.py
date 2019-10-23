import os
import sys
import subprocess

class ElectrumInterface(object):
	def __init__(self,arch):
		self.architecture = arch
		self.results = dict()
