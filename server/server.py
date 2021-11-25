import socket
import asyncio
import threading
import json
import os
import imp
import common as c
import components as comp
import logging
import alflogger
import yaml
import time
import requests
from queue import Queue
from copy import deepcopy

logger = logging.getLogger("Alfons")

def setupConfig():
	def _configMerge(base, head):
		base = deepcopy(base)
		for k in head:
			if not k in base: continue
			if type(base[k]) is dict:
				base[k] = _configMerge(base[k], head[k])
			else:
				base[k] = head[k]
		return base

	with open(c.PATH + "config/config.yaml.default") as f:
		baseConfig = yaml.safe_load(f)

	with open(c.PATH + "config/config.yaml") as f:
		headConfig = yaml.safe_load(f)

	c.config = _configMerge(baseConfig, headConfig)

	# If the data path doesn't start with a / it's a path relative to the project root
	if not c.config["data_path"].startswith("/"):
		c.config["data_path"] = c.PATH + c.config["data_path"]

	if c.config["ssl"]["cert_file"] != None:
		c.config["ssl"]["enabled"] = True

		for k in ["chain_file", "key_file", "trusted_file"]:
			if c.config["ssl"][k] == None:
				c.config["ssl"]["enabled"] = False
				break
	else:
		c.config["ssl"]["enabled"] = False

	if not "ip" in c.config or c.config["ip"] == None:
		# Find IP
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("8.8.8.8", 80))
		c.config["ip"] = s.getsockname()[0]
		s.close()

sharedEventLoop = None

def main():
	global sharedEventLoop
	logger.info("Starting Alfons!")

	sharedEventLoop = asyncio.get_event_loop()

	setupConfig()

	with open(c.PATH + "server/components/manifest.json") as manifestFile:
		componentsList = json.load(manifestFile)["load_order"]

		for component in componentsList:
			fileName = component + ".py"
			module = imp.load_source(fileName[:-3], c.PATH + "server/components/" + fileName)
			comp.components[fileName[:-3]] = module

	startCompQueue = Queue()

	for name in comp.components:
		def moduleThread(q, module, **kwargs):
			try:
				module.start(q, **kwargs)
			except Exception as e:
				if q.empty(): # The exception was raised before q.put(0) in module.start()
					q.put(e)
				else:
					logger.exception("Module '{}' crashed".format(name))

		if hasattr(comp.components[name], "start"):
			thread = threading.Thread(target=moduleThread, args=(startCompQueue, comp.components[name], ))
			thread.daemon = True
			thread.start()

			r = startCompQueue.get()

			if issubclass(type(r), Exception):
				logger.exception("Module '{}' crashed during startup. No new modules will be started".format(name), exc_info=r)
				break
			else:
				logger.info("Successfully set up component {}".format(name))
	
	sharedEventLoop.run_forever()

def start():
	try:
		main()

		# Pretty ugly but working solution
		l = threading.Lock()
		l.acquire()
		l.acquire()
	except KeyboardInterrupt:
		logging.info("Exiting...")
