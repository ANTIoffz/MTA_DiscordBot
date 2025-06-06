from pytz import timezone
from disnake.ext.commands import Bot, Cog, slash_command
from disnake import Colour, Embed
from disnake.ext import tasks
from datetime import datetime
from bot.database import database_bot, database_mta
from bot.misc import Config, check_id, change_player_field, get_last_account_id, find_id
from bot.server_monitoring import server
import urllib.request
from disnake.errors import DiscordServerError
import asyncio
from bot.ssh import console


class __MainRegisterLogCog(Cog):
    def __init__(self, bot: Bot):
        self.previous_last_id = None
        self.last_id = None
        self.bot = bot


    @Cog.listener()
    async def on_ready(self) -> None:
        if not self.check_new_accounts.is_running():
            self.check_new_accounts.start()


    @tasks.loop(seconds=10)
    async def check_new_accounts(self):
        self.last_id = await get_last_account_id()
        self.previous_last_id = self.last_id if self.previous_last_id is None else self.previous_last_id

        if self.last_id != self.previous_last_id:
            self.previous_last_id = self.last_id
            player = find_id(self.last_id)
            players_string = f"""* {player['nickname']}
🎂 - `{datetime.fromtimestamp(player['birthday']).strftime("%d.%m.%Y")}`
🆔 - `{player['id']}`
"""
            embed = Embed(
                title=f"👥{Config.BOT_SEPARATOR} Регистрация",
                description=f"**{players_string}**",
                color=Colour.lighter_gray(),
                timestamp=datetime.now(),
            )

            log_channel = self.bot.get_channel(Config.BOT_NEW_ACCOUNTS_LOG_CHANNEL)
            await log_channel.send(embed=embed)


def register_register_log_cogs(bot: Bot) -> None:
    bot.add_cog(__MainRegisterLogCog(bot))
