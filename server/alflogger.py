import logging
import datetime
from common import PATH

class CustomLoggerFormatter(logging.Formatter):
	def __init__(self, toFile = False):
		self._toFile = toFile

	def getColor(self, color):
		if self._toFile or color == "none":
			return ""
		if color == "green":
			return "\033[32m"
		elif color == "yellow":
			return "\033[93m"
		elif color == "red":
			return "\033[91m"
		elif color == "end":
			return "\033[0m"

	def indentStack(self, indent, excInfo, color = None):
		return "\n" + "\n".join([" " * indent + self.getColor(color) + "|" + self.getColor("end") + " " + x for x in (self.formatException(excInfo)).split("\n")])

	def format(self, record):
		t = datetime.datetime.fromtimestamp(record.created).strftime("%y%m%d %H:%M:%S")

		# Create a header that will start every log. Pad the level name so that the rest always start at the same position
		# 8 is the longest logging livel name, "CRITICAL"
		header = "{}{} {}| ".format(record.levelname, " " * (8 - len(record.levelname)), t)

		try:
			message = record.msg % record.args
		except:
			message = record.msg

		color = "red" if record.levelno >= 40 else "yellow" if record.levelno >= 30 else "green" if record.levelno >= 10 and record.levelno < 20 else "none"
		indentedStack = "" if record.exc_info == None else self.indentStack(len(header) - 2, record.exc_info, color)

		# Setup the out variable
		out = self.getColor(color) + header + message

		# If there's no indentedStack - there should be other helpfull information
		if indentedStack == "":
			# For errors and above, add file name and line number
			if record.levelno >= 40:
				out += " [{} Line: {}]".format(record.pathname, record.lineno)
			# For information and warnings, add the logger name
			elif record.levelno >= 20:
				out += " [{}]".format(record.name)

		# End the color
		out += self.getColor("end")
		# Add the indented stack trace
		out += indentedStack

		# Must be last
		# For critical and above...
		if record.levelno >= 50:
			divider = self.getColor(color) + ("=" * 80) + self.getColor("end")
			# ...surround the whole log with a divider
			out = divider + "\n" + out + "\n" + divider

		return out

# Setup the logger
fh = logging.FileHandler(PATH + "/Alfons.log")
ch = logging.StreamHandler()
fh.setFormatter(CustomLoggerFormatter(True))
ch.setFormatter(CustomLoggerFormatter())
fh.level = 10
ch.level = 20
logging.basicConfig(handlers=[fh, ch], level=0)
