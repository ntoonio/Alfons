import common
import os
import json
import logging
import asyncio
from aiohttp import web
from aiohttp_index import IndexMiddleware
import ssl
import pkg_resources
import time

import database
import mqtt_client
import common as c

logger = logging.getLogger(__name__)

aiohttoAccessLogger = logging.getLogger("aiohttp.access")
aiohttoAccessLogger.setLevel(logging.WARN)

loadedData = {}

async def apiInfoHandle(request):
	data = {
		"ip": c.config["ip"],
		"domain": c.config["domain"],
		"web_port": c.config["web"]["port"],
		"ssl": c.config["ssl"]["enabled"],
		"mqtt": {
			"tcp_port": c.config["mqtt"]["tcp_port"],
			"ws_port": c.config["mqtt"]["ws_port"]
		}
	}

	if c.config["ssl"]["enabled"]:
		data["ssl_cert"] = loadedData["ssl_cert"]
		data["ssl_chain"] = loadedData["ssl_chain"]

	return web.json_response(data=data)

async def mqttPublishHandle(request):
	params = await request.json()

	requiredParams = ["topic", "payload", "username", "password"]

	for p in requiredParams:
		if not p in params:
			return web.json_response(data={"error": "Missing one of the parameters: " + ", ".join(requiredParams)}, status=406)

	username = params["username"]
	password = params["password"]

	if username.lower() == "server":
		return web.json_response(data={"error": "Username can't be 'server'"}, status=406)

	authEntryPoint = None
	for e in pkg_resources.iter_entry_points("hbmqtt.broker.plugins"):
		if e.name == "mqtt_plugin_alfons_auth":
			authEntryPoint = e
			break

	if authEntryPoint == None:
		return web.json_response(data={"error": "Authorization endpoint not found, something went wrong during the installation"}, status=503)

	# Imitate the broker calling the auth plugin

	class FakeContext():
		def __init__(self, conf, logger):
			self.config = conf
			self.logger = logger

	class FakeSession():
		def __init__(self, username, password):
			self.username = username
			self.password = password

	context = FakeContext({"auth": {"alfons-db": database.db, "server-password": None}}, logger) # Set server-password just in case to save us from 'key not found'
	session = FakeSession(username, password)

	authPluginObj = e.load()
	allowed = await authPluginObj(context).authenticate(session=session)

	if not allowed:
		return web.json_response(data={"error": "Not authenticated"}, status=401)

	t = params["topic"]
	p = params["payload"]
	q = params["qos"] if "qos" in params else 1
	r = params["ratain"] if "retain" in params else False

	messageInfo = mqtt_client.publish(topic=t, payload=p, qos=q, retain=r)
	messageInfo.wait_for_publish()

	if messageInfo.is_published():
		return web.json_response(data={"success": True, "msg": "Succesfully published to topic '{}'".format(t)}, status=201)
	else: # Can this happen?
		return web.json_response(data={"success": False, "msg": "The message wasn't published due to unknown reasons"}, status=500)

# Preload some data so the files won't have to be read for every page visit
def loadData():
	global loadedData

	if c.config["ssl"]["enabled"]:
		with open(c.config["ssl"]["cert_file"]) as f:
			loadedData["ssl_cert"] = f.read()

		with open(c.config["ssl"]["chain_file"]) as f:
			loadedData["ssl_chain"] = f.read()

def start(q):
	loadData()

	app = web.Application(middlewares=[IndexMiddleware()])

	# API endpoints
	app.router.add_get("/api/v1/info/", apiInfoHandle)
	app.router.add_put("/api/v1/mqtt_publish/", mqttPublishHandle)

	app.router.add_static("/", common.PATH + "components/web/")

	sslContext = None
	if c.config["ssl"]["enabled"] and c.config["web"]["inside_port"] == None:
		sslContext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, cafile=c.config["ssl"]["chain_file"])
		sslContext.load_cert_chain(c.config["ssl"]["cert_file"], c.config["ssl"]["key_file"])

	webPort = c.config["web"]["port"] if c.config["web"]["inside_port"] == None else c.config["web"]["inside_port"]

	logger.info("Starting web server on {}".format(webPort))
	asyncio.set_event_loop(asyncio.new_event_loop())
	server = asyncio.get_event_loop().create_server(app.make_handler(), host="0.0.0.0", port=webPort, ssl=sslContext)
	asyncio.get_event_loop().run_until_complete(server)

	q.put(0)

	asyncio.get_event_loop().run_forever()
