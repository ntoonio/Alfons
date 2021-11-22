import paho.mqtt.client as mqtt
import common as c
import components as comp
import time
import logging
import certifi
import ssl
from ssl import PROTOCOL_TLSv1_1

logger = logging.getLogger(__name__)

def on_connect(*args):
	logger.info("MQTT client connected.")

def on_disconnect(*args):
	logger.warn("Couldn't connect")

def publish(**kwargs):
	topic = kwargs.get("topic")
	payload = kwargs.get("payload", None)
	qos = kwargs.get("qos", 1)
	retain = kwargs.get("retain", False)

	logger.debug("Publishing '{}' to {} with qos set to {}. retain={}".format(payload, topic, qos, retain))

	return client.publish(topic, payload=payload, qos=qos, retain=retain)

def start(q):
	global client

	comp.components["automation"].registerAction("mqtt", publish)

	client = mqtt.Client("alfons-server-client-id", transport="tcp")
	client.username_pw_set("server", password=c.MQTT_SERVER_PASSWORD)

	#client.on_message = on_message # def on_message(client, userdata, message):
	client.on_connect = on_connect
	client.on_disconnect = on_disconnect

	if c.config["ssl"]["enabled"]:
		sslContext = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
		sslContext.load_verify_locations(cafile=certifi.where())
		client.tls_set_context(sslContext)


	# It's ok that this is insecure since it's only a local connection. The only reason it uses TLS is because that's what the
	# broker is using and it can't connect without it. It might, in the future if we need more local connections, be an
	# alternative to start a new broker listener without encryption and that won't be exposed to the internet.
	if c.config["ssl"]["enabled"]:
		client.tls_insecure_set(True)

	q.put(0)
	client.connect("127.0.0.1", c.config["mqtt"]["tcp_port"])

	client.loop_start()
