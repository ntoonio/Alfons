from amqtt.client import MQTTClient
import asyncio
import common as c
import components as comp
import time
import logging
import certifi
import ssl
from ssl import PROTOCOL_TLSv1_1
import server

logger = logging.getLogger(__name__)

async def publish(**kwargs):
	topic = kwargs.get("topic")
	payload = kwargs.get("payload", "").encode("utf-8")
	qos = kwargs.get("qos", 1)
	retain = kwargs.get("retain", False)

	logger.debug("Publishing '{}' to {} with qos set to {}. retain={}".format(payload, topic, qos, retain))
	msg = await client.publish(topic, payload, qos=qos)

	return msg

async def run():
	global client
	client = MQTTClient()

	await client.connect("mqtt" + ("" if c.config["ssl"]["enabled"] else "") + "://server:" + c.MQTT_SERVER_PASSWORD + "@127.0.0.1:" + str(c.config["mqtt"]["tcp_port"]))
	logger.info("MQTT client connected.")

def start(q):
	comp.components["automation"].registerAction("mqtt", publish)

	server.sharedEventLoop.create_task(run())

	q.put(0)

