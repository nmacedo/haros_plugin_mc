from interval import *
from facade import *
import os
#### Imports for testing
from collections import namedtuple
from haros.hpl.hpl_ast import *

#####################
##################################
# Interface Methods 
def configuration_analysis(iface, scope):
	
	if scope.nodes.__len__() <= 1:	# Node Configurations
		return 
	
	interface = facade(scope.name, scope.nodes, scope.topics,properties=scope.hpl_properties)

 

