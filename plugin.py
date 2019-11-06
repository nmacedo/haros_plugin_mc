from mc_Interface import *

def configuration_analysis(iface, scope):
	print("[MC] Running analysis...")
	if scope.nodes.__len__() <= 1:	# Node Configurations
		return 
	mc_iface = MC_Interface(scope.name, scope.nodes, scope.topics,properties=scope.hpl_properties)
	results = mc_iface.model_check()
	html = mc_iface.to_html(results)
	print("[MC] Reporting results...")
	iface.report_violation("mc",html)