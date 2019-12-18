import os
from mc_Interface import *

def configuration_analysis(iface, scope):
	if scope.nodes.__len__() <= 1:	# Node Configurations
		print("Node configuration.")
		return
	
	mc_iface = MC_Interface(scope.name, scope.nodes, scope.topics,properties=scope.hpl_properties)
	results = mc_iface.model_check()
	html_list = mc_iface.to_html(results)
	print("[MC] Reporting results...")
	for s in html_list:
		if s is None:
			continue
		else:
			iface.report_violation("mc",s)