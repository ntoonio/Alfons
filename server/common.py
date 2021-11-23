import os
import string
import secrets
import components
import sys

DEBUG = True
PATH = os.path.dirname(os.path.abspath(sys.argv[0])) + "/"

config = {}

def generateId(length, onlyHex = False, noPunctation = True):
	return "".join(secrets.choice(string.digits + "abcdef" if onlyHex else string.ascii_letters + string.digits + ("" if noPunctation else string.punctuation)) for _ in range(length))

MQTT_SERVER_PASSWORD = generateId(20, False)

def getComponent(name):
	if name not in components.components:
		raise NameError("'{}' not found in components".format(name))
	return components.components[name]
