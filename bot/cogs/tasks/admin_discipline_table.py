from pytz import timezone
from disnake.ext.commands import Bot, Cog, slash_command
from disnake import Colour, Embed
from disnake.ext import tasks
from datetime import datetime
from bot.database import database_bot, database_mta
from bot.misc import Config, check_id, change_player_field
from bot.server_monitoring import server
import urllib.request
from disnake.errors import DiscordServerError
import asyncio
from bot.ssh import console


def step(text, spaces=7):
    return "  " * (spaces - len(str(text)))


class __MainAdminDisciplineTableCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        if not self.admin_discipline_table.is_running():
            self.admin_discipline_table.start()

    @tasks.loop(seconds=10)
    async def admin_discipline_table(self):
        try:
            channel = self.bot.get_channel(Config.BOT_ADMIN_DISCIPLINE_TABLE_CHANNEL)
            last_message = await channel.history(limit=1).flatten()
            bot_db_status = database_bot.get_status()
            
            if not bot_db_status:
                table = '**База данных отключена**'
            else:
                database_bot.cursor.execute("DELETE FROM `admins` WHERE reprimands = 0 AND warnings = 0")
                database_bot.cursor.execute("SELECT * FROM `admins`")
                data = database_bot.cursor.fetchall()

                table = ''.join(
                    f"* ‼️ `{user['reprimands']} / {Config.ADMIN_MAX_REPRIMANDS}`{step('{} / {}'.format(user['reprimands'], Config.ADMIN_MAX_REPRIMANDS))}|    `{user['warnings']} / {Config.ADMIN_MAX_WARNINGS}` ❗{step('{} / {}'.format(user['warnings'], Config.ADMIN_MAX_REPRIMANDS))}-    <@{user['discord_id']}>\n"
                    for user in data
                )
                
            embed = Embed(
                title=f"😈{Config.BOT_SEPARATOR}Злая таблица",
                description=f"**{table}**",
                color=Colour.dark_magenta() if bot_db_status else Colour.red(),
            )
                
            if last_message and last_message[0].author == self.bot.user:
                await last_message[0].edit(embed=embed)
            else:
                await channel.send(embed=embed)

        except DiscordServerError:
            await asyncio.sleep(10)

        except AttributeError as e:
            print(f"[ERROR] Не удалось получить канал {Config.BOT_ADMIN_DISCIPLINE_TABLE_CHANNEL}\n{e}")
            await asyncio.sleep(10)

def register_admin_discipline_table_cogs(bot: Bot) -> None:
    if Config.BOT_ADMIN_DISCIPLINE_TABLE_CHANNEL:
        bot.add_cog(__MainAdminDisciplineTableCog(bot))
