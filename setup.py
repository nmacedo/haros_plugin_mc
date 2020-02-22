import os

def install():
	environment_dir = "/.plugin_mc/"
	mode = 0o777
	os.mkdir(environment_dir, mode)
	cmd = "cp ./electrum/electrum_pi.jar /.plugin_mc/"
	os.system(cmd)
	cmd = "cp plugin.yaml /.plugin_mc/"
	os.system(cmd)
	cmd =  ""
	cmd = "cp ./electrum/meta.ele /.plugin_mc/"
	os.system(cmd)
	try:
		with open("/.plugin_mc/model.ele","w") as f:
			f.write("Empty Cache")
	except Exception as error:
		print(error)
	os.chmod("/.plugin_mc/model.ele", mode)
	

if __name__=="__main__":
	install()
