import os
from .mc.analyzer import *

def configuration_analysis(iface, scope):
	# Node Configurations
	if scope.nodes.__len__() <= 1:	
		return
	# Architectural Configurations
	print("[MC] Running analysis...")
	analyzer = Analyzer(scope.name, scope.nodes, scope.topics,properties=scope.hpl_properties)
	print("[MC] Model-Checking Specification...")
	rl = analyzer.model_check()
	print("[MC] Reporting results...")
	for (hh,rt) in rl:
		res = set()
		for r in rt: # the returned set contains nodes and topics
			if type(r) == Topic:
				res.add(scope.topics.get(r.rosname))
			else:
				res.add(scope.nodes.get(r.rosname))
		iface.report_runtime_violation("mc",hh,res)
