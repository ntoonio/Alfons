from amqtt.client import MQTTClient
import asyncio
import common as c
import components as comp
import time
import logging
import certifi
import ssl
from ssl import PROTOCOL_TLSv1_1

logger = logging.getLogger(__name__)

def publish(**kwargs):
	topic = kwargs.get("topic")
	payload = kwargs.get("payload", None)
	qos = kwargs.get("qos", 1)
	retain = kwargs.get("retain", False)

	logger.debug("Publishing '{}' to {} with qos set to {}. retain={}".format(payload, topic, qos, retain))

	return client.publish(topic, payload, qos=qos, retain=retain)

async def run():
	client = MQTTClient()

	# The broker won't have had time enough to start yet
	time.sleep(1)
	await client.connect("mqtt" + ("s" if c.config["ssl"]["enabled"] else "") + "://server" + c.MQTT_SERVER_PASSWORD + "@127.0.0.1:" + str(c.config["mqtt"]["tcp_port"]))
	logger.info("MQTT client connected.")

def start(q):
	global client

	comp.components["automation"].registerAction("mqtt", publish)

	q.put(0)

	asyncio.run(run())

