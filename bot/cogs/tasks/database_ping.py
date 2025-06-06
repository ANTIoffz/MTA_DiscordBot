from pytz import timezone
from disnake.ext.commands import Bot, Cog, slash_command
from disnake import Colour, Embed
from disnake.ext import tasks
from datetime import datetime
from bot.database import database_bot, database_mta
from bot.misc import Config, check_id, change_player_field
from bot.server_monitoring import server
import urllib.request


class __MainPingDatabasesCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        if not self.ping_databases.is_running():
            self.ping_databases.start()

    @tasks.loop(seconds=60)
    async def ping_databases(self):
        if Config.DATABASE_AUTORECONNECT:
            database_mta.connection.ping(reconnect=True)
            database_bot.connection.ping(reconnect=True)


def register_ping_databases_cogs(bot: Bot) -> None:
    bot.add_cog(__MainPingDatabasesCog(bot))
