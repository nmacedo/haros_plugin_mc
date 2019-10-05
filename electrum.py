import os
import sys
import subprocess


class ElectrumInterface(object):
	def __init__(self,arch):
		self.architecture = arch
		self.setup_electrum()
		self.results = dict()
		self.model_check()

	def setup_electrum(self):		# setup.py stuff
		global_dir = "/home/parallels/ros/haros/haros_plugin_mc"
		run_time_dir = os.getcwd()
		cmd = "cp " + global_dir+ "/electrum.jar " + run_time_dir
		os.system(cmd)
	
	def model_check(self):
		with open('model.ele',"w") as f:
			f.write(self.architecture.spec())
		return