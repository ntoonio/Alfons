import logging
import components as comp
import json
import requests
import ssl
import datetime
import time
import common as c

SUN_API = "https://api.sunrise-sunset.org/json?lat=%s&lng=%s" % (c.config["location"]["lat"], c.config["location"]["long"])

# Set this to a state name to test that activation time to a few seconds ahead
# False to disable
SUN_DEBUG = False

logger = logging.getLogger(__name__)

logging.getLogger("urllib3.connectionpool").setLevel(100)

states = {
	"sunrise": None,
	"sunset": None,
	"solar_noon": None,
	"civil_twilight_begin": None,
	"civil_twilight_end": None,
	"nautical_twilight_begin": None,
	"nautical_twilight_end": None,
	"astronomical_twilight_begin": None,
	"astronomical_twilight_end": None
}

lastUpdate = 0

def evaluateCondition(condition):
	if lastUpdate == 0:
		logger.warn("The sun data has not been set")
		return False
	elif lastUpdate < time.time() - 86400:
		logger.warn("The sun data is too old")
		return False

	rawTime = states[condition["state"]]
	activateTime = rawTime + (int(condition["offset"] if "offset" in condition else 0) or 0)

	nowTime = int(time.time())

	if condition.get("time", "at") == "at" and nowTime == activateTime:
		return True
	elif condition.get("time") == "after" and nowTime > activateTime:
		return True
	elif condition.get("time") == "before" and nowTime < activateTime:
		return True

	return False

def fetchStates():
	global states, lastUpdate

	todayDate = datetime.datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d")

	contents = requests.get(SUN_API + "&date=" + todayDate).json()

	if contents["status"] != "OK":
		logger.warn("Sun API status is not 'OK' (1)")
		return False

	for k in ["day_length"]:
		contents["results"].pop(k, None)
	results = contents["results"]



	for state in results:
		strTime = "%s %s" % (todayDate, results[state])
		timeFormat = "%Y-%m-%d %I:%M:%S %p"
		timestamp = datetime.datetime.strptime(strTime, timeFormat).timestamp()
		results[state] = int(timestamp)

	states = results
	lastUpdate = time.time()

	return True

def start(q):
	comp.components["automation"].registerCondition("sun", evaluateCondition)

	fetchStates()

	q.put(0)

	if SUN_DEBUG != False:
		global lastUpdate

		now = int(time.time())

		states[SUN_DEBUG] = now + 7
		lastUpdate = now

		logger.info("- - - - SUN DEBUG - - - -")
		logger.info("Fetched fake state for %s (debugging)" % SUN_DEBUG)
		logger.info("Will exec at %s" % datetime.datetime.fromtimestamp(states[SUN_DEBUG]).strftime("%H:%M:%S"))
		logger.info("- - - - - - - - - - - - -")

		return

	while True:
		fetchStates()
		logger.info("Fetched state")

		now = datetime.datetime.now()
		passed = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

		# Calculate time to sleep until 10 seconds after midnight
		sleep = 86400 - passed + 10

		logger.info("Fetching state again in %d seconds" % sleep)

		time.sleep(sleep)
		fetchStates()
