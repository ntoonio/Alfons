import common
import server
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
import authorization as a

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

	allowed = a.authorize(username, password)

	if not allowed:
		return web.json_response(data={"error": "Not authenticated"}, status=401)

	t = params["topic"]
	p = params["payload"]
	q = params["qos"] if "qos" in params else 1
	r = params["retain"] if "retain" in params else False

	messageInfo = await mqtt_client.publish(topic=t, payload=p, qos=q, retain=r)
		
	return web.json_response(data={"success": True, "msg": "Succesfully published to topic '{}'".format(t)}, status=201)

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

	app.router.add_static("/", common.PATH + "server/components/web/")

	sslContext = None
	if c.config["ssl"]["enabled"] and c.config["web"]["inside_port"] == None:
		sslContext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, cafile=c.config["ssl"]["chain_file"])
		sslContext.load_cert_chain(c.config["ssl"]["cert_file"], c.config["ssl"]["key_file"])

	webPort = c.config["web"]["port"] if c.config["web"]["inside_port"] == None else c.config["web"]["inside_port"]

	logger.info("Starting web server on {}".format(webPort))

	asyncio.set_event_loop(server.sharedEventLoop)
	s = server.sharedEventLoop.create_server(app.make_handler(), host="0.0.0.0", port=webPort, ssl=sslContext)
	server.sharedEventLoop.run_until_complete(s)

	q.put(0)

