import os

def install():
	environment_dir = "/plugin_mc/"
	mode = 0o777
	os.mkdir(environment_dir, mode)
	cmd = "cp ./electrum/electrum_pi.jar /plugin_mc/"
	os.system(cmd)


if __name__=="__main__":
	install()
