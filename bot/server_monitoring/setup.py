from .mta import server_
from bot.misc import Config

# REGISTER MTA SERVER
server = server_(Config.SERVER_HOST, Config.SERVER_PORT)