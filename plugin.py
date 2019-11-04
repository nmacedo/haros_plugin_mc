from mc_Interface import *

def configuration_analysis(iface, scope):
	if scope.nodes.__len__() <= 1:	# Node Configurations
		return 
	mc_iface = MC_Interface(scope.name, scope.nodes, scope.topics,properties=scope.hpl_properties)
	results = mc_iface.model_check()
	html = mc_iface.results_to_html(results)
	iface.report_violation("mc",html)
