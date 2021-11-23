from passlib.hash import pbkdf2_sha256

import database
import common

def authorize(username, password):
	username = username.lower()

	if username.startswith("iot-"):
		if password == "iot":
			return True
		else:
			return False
	elif username == "server":
		if password == common.MQTT_SERVER_PASSWORD:
			return True
		else:
			return False

	with database.db as db:
		fetch = db.cursor.execute("SELECT password FROM users WHERE username = ?", [username]).fetchone()

		if fetch != None and len(fetch) == 1:

			if pbkdf2_sha256.verify(password, fetch[0]):
				return True
	return False
