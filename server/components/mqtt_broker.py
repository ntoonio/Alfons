import asyncio
from hbmqtt.broker import Broker
from hbmqtt.plugins.authentication import BaseAuthPlugin
import logging

import common as c
import components as comp
import authorization as a

logging.getLogger("transitions.core").setLevel(100)

async def broker_coro():
	global broker

	brokerConfig = {
		"listeners": {
			"default": {
				"bind": "0.0.0.0:" + str(c.config["mqtt"]["tcp_port"]),
				"type": "tcp",
				"ssl": c.config["ssl"]["enabled"],
				"cafile": c.config["ssl"]["chain_file"],
				"certfile": c.config["ssl"]["cert_file"],
				"keyfile": c.config["ssl"]["key_file"]
			},
			"ws": {
				"bind": "0.0.0.0:" + str(c.config["mqtt"]["ws_port"]),
				"type": "ws",
				"ssl": c.config["ssl"]["enabled"],
				"cafile": c.config["ssl"]["chain_file"],
				"certfile": c.config["ssl"]["cert_file"],
				"keyfile": c.config["ssl"]["key_file"]
			}
		},
		"timeout-disconnect-delay": 2,
		"topic-check": {
			"enabled": True,
			"plugins": ["mqtt_plugin_alfons_topic"]
		},
		"auth": {
			"plugins": ["mqtt_plugin_alfons_auth"],
			"authorizer": a.authorize
		}
	}

	logging.getLogger("amqtt.broker.plugins.event_logger_plugin").setLevel(logging.WARNING)

	broker = Broker(brokerConfig, None)
	await broker.start()

def start(q):
	q.put(0)

	asyncio.new_event_loop().run_until_complete(broker_coro())

