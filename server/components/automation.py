import os
import logging
import yaml
from common import PATH
import time

logger = logging.getLogger(__name__)

automations = {}
conditions = {}
actions = {}

def runExecutionTests():
	"Iterate all automations and test if any of them should be executed"

	for a in automations:
		if "conditions" in automations[a]:
			tRL = [] # triggerResultList
			for condition in automations[a]["conditions"]:
				if "condition" in condition:
					if condition["condition"] in conditions:
						tRL.append(testCondition(condition))
						tRL.append(condition.get("rel", "and"))

			tRL = tRL[:-1]

			while "and" in tRL:
				i = 0
				for j in tRL:
					if j == "and":
						tRL[i - 1] = tRL[i - 1] and tRL[i + 1]
						del tRL[i + 1]
						del tRL[i]
					i += 1

			if True in tRL:
				logging.debug("Executing automation '" + str(a) + "'")
				executeActions(a)

def _readAllAutomations():
	if not os.path.exists(PATH + "/automations"):
		os.mkdir(PATH + "/automations")

	for fileName in os.listdir(PATH + "/automations"):
		if (fileName.endswith(".yaml") or fileName.endswith(".yml")) and not fileName.startswith("_"):
			logger.info("Loading automatisation '" + fileName.replace(".yaml", "").replace(".yml", "") + "'")
			readAutomation(fileName)

def _readAutomation(fileName):
	logger.debug("Loading automation '{}'".format(fileName))

	with open(PATH + "/automations/" + fileName) as f:
		a = yaml.safe_load(f)

	name = fileName.split(".", 1)[0]

	if "trigger" in a["automation"] or "conditions" in a["automation"] and len(a["automation"]["conditions"]) > 0:
		automations[name] = a["automation"]

def registerCondition(condition, function):
	"Register a function to evaluate the condition with the given name"

	conditions[condition] = function

def testCondition(c):
	if c["condition"] in conditions:
		if conditions[c["condition"]](c):
			return True
	else:
		logger.warn("Found automation for condition '%s' but no such condition found" % c["condition"])

	return False

def registerAction(action, function):
	"Register a function to be executed for the specified action"

	actions[action] = function

def executeActions(target):
	"Execute the actions for the specified automation"

	for action in automations[target]["actions"]:
		try:
			actionName = action["action"]
			actions[actionName](**action)
		except:
			logger.error("Couldn't exec action '" + actionName + "' for target '" + target + "'")

def start(q):
	_readAllAutomations()

	q.put(0)

	while True:
		time.sleep(1 - (time.time() % 1))
		runExecutionTests()
