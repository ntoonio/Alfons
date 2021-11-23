import sqlite3
import threading
import common as c
import logging

logger = logging.getLogger(__name__)

class LockableSqliteConnection(object):
	def __init__(self, dburi):
		self.lock = threading.Lock()
		self.connection = sqlite3.connect(dburi, check_same_thread=False)
		self.cursor = self.connection.cursor()
	def __enter__(self):
		self.lock.acquire()
		self.cursor = self.connection.cursor()
		return self
	def __exit__(self, type, value, traceback):
		self.lock.release()
		self.connection.commit()
		if self.cursor is not None:
			self.cursor.close()
			self.cursor = None

def start(q):
	global db
	db = LockableSqliteConnection(c.config["data_path"] + "Alfons.db")

	q.put(0)
