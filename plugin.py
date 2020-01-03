import os
from analyzer import *

def configuration_analysis(iface, scope):
	if scope.nodes.__len__() <= 1:	# Node Configurations
		return
	
	print("[MC] Running analysis...")
	analyzer = Analyzer(scope.name, scope.nodes, scope.topics,properties=scope.hpl_properties)
	print("[MC] Reporting results...")