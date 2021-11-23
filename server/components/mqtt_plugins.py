from hbmqtt.plugins.authentication import BaseAuthPlugin
from hbmqtt.plugins.topic_checking import BaseTopicPlugin

class AlfonsHBMQTTAuthPlugin(BaseAuthPlugin):
	def __init__(self, context):
		super().__init__(context)

		self.authorizer = self.auth_config["authorizer"]

	async def authenticate(self, *args, **kwargs):
		session = kwargs.get("session", None)

		if session.username == None or session.password == None:
			self.context.logger.debug("Tried to authenticate with 'None' username or password [AlfonsHBMQTTAuthPlugin]")
			return False

		username = session.username.lower()
		password = session.password

		return self.authorizer(username, password)


class AlfonsHBMQTTTopicPlugin(BaseTopicPlugin):
	def __init__(self, context):
		super().__init__(context)

	async def topic_filtering(self, *args, **kwargs):
		self.context.logger.debug("Topic checking - *args={} **kwargs={}".format(str(args), str(kwargs)))
		return True
