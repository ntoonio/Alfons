import logging
import components as comp
from datetime import datetime
import time

logger = logging.getLogger(__name__)

def evaluateCondition(condition):
	activateDateClock = condition["clock"] + " " + datetime.now().strftime("%d/%m/%Y")
	rawTime = int(datetime.timestamp(datetime.strptime(activateDateClock, "%H:%M %d/%m/%Y")))
	offset = int(condition["offset"] if "offset" in condition else 0)

	activateTime = rawTime + offset

	nowTime = int(time.time())

	if condition.get("time", "at") == "at" and nowTime == activateTime:
		return True
	elif condition.get("time") == "after" and nowTime > activateTime:
		return True
	elif condition.get("time") == "before" and nowTime < activateTime:
		return True

	return False

def start(q):
	comp.components["automation"].registerCondition("clock", evaluateCondition)

	q.put(0)
