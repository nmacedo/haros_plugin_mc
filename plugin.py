from interval import *
import os
#### Imports for testing
from collections import namedtuple
from haros.hpl.hpl_ast import *
from electrumInterface import *

#####################
##################################
# Interface Methods 
def configuration_analysis(iface, scope):
	
	if scope.nodes.__len__() <= 1:	# Node Configurations
		return 
	
	interface = ElectrumInterface(scope.name, scope.nodes, scope.topics,properties=scope.hpl_properties)