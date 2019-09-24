from interval import *
from facade import *
import os
#### Imports for testing
from collections import namedtuple
from haros_plugin_mc.hpl.hpl_ast import *
from haros_plugin_mc.hpl.parser import hpl_parser

#####################
##################################
# Interface Methods 
def configuration_analysis(iface, scope):
	#Testing
	
	# Change scope name to config
	# Properties will be found on config.hpl_properties (ja com o parser feito)
	if scope.name == "startup":
		print("startup configuration ignored.....")
		return	
	
	### Testing Properties
	prop1 = """globally: some /kinect2/qhd/camera_info {data = 2}"""
	prop2 = """globally: no /kinect2/qhd/camera_info {data = 1}"""
	prop3 = """globally: /supervisor/cmd_vel {linear.x = 2.0} causes /kinect2/qhd/camera_info {data = 1}"""
	prop4 = """globally: /supervisor/cmd_vel {linear.x = 2.0} as E causes /supervisor/cmd_vel {linear.x = $E.linear.x}""" 
	prop5 = """globally: /supervisor/cmd_vel {linear.x = 2.0} as E requires /supervisor/cmd_vel {linear.x = $E.linear.x}""" 
	prop6 = """globally: /kinect2/qhd/camera_info {data = 1} requires /supervisor/cmd_vel {linear.x = 2.0}"""
 	prop7 = """globally: /supervisor/cmd_vel {linear.x in 2.0 to 10.0} as E requires /supervisor/cmd_vel {linear.x = $E.linear.x}"""
 	prop8 = """globally: /supervisor/cmd_vel {linear.x in [21.0,3.0]} as E requires /supervisor/cmd_vel {linear.x = $E.linear.x}"""
 	hp = hpl_parser()
	ps = [hp.parse(prop1),hp.parse(prop2),hp.parse(prop3),hp.parse(prop4),hp.parse(prop5),hp.parse(prop6),hp.parse(prop7),hp.parse(prop8)]

	interface = facade(scope.name, scope.nodes, scope.topics,properties=ps)

 

