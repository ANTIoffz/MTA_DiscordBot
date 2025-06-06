from pytz import timezone
from disnake.ext.commands import Bot, Cog, slash_command
from disnake import Colour, Embed
from disnake.ext import tasks
from datetime import datetime
from bot.database import database_bot, database_mta
from bot.misc import Config, check_id, change_player_field
from bot.server_monitoring import server
import urllib.request
import asyncio
from disnake.errors import DiscordServerError
from transliterate import translit, get_available_language_codes
from transliterate.base import TranslitLanguagePack, registry
import re
import asyncio


class __MainPlayersTaskCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        if not self.players_task.is_running():
            self.players_task.start()


    @tasks.loop(seconds=10)
    async def players_task(self):
        try:
            channel = self.bot.get_channel(Config.BOT_PLAYERS_CHANNEL)
            last_message = await channel.history(limit=1).flatten()
            server_status = server.reconnect()

            if server_status:
                res = server.server.response.decode('utf-8')
                res = re.sub(r'[^a-zA-Z_?]', '', res, flags=re.UNICODE)
                res = res.split('?')[1:]
                players_list = f"\n".join(f"`{nickname.strip()}`" for nickname in res)
                embed = Embed(
                    title=f"👥 [{len(res)}]{Config.BOT_SEPARATOR}Игроки на сервере",
                    description=players_list if players_list else "**Нету   ¯\_(ツ)_/¯**",
                    color=Colour.dark_green(),
                    timestamp=datetime.now(),
                )
            else:
                embed = Embed(
                    title=f"❌{Config.BOT_SEPARATOR}Ошибка",
                    description=f"**Сервер не онлайн**",
                    color=Colour.red(),
                    timestamp=datetime.now(),
                )

            if last_message and last_message[0].author == self.bot.user:
                await last_message[0].edit(embed=embed)
            else:
                await channel.send(embed=embed)

        except DiscordServerError:
            await asyncio.sleep(10)

        except AttributeError as e:
            print(f"[ERROR] Не удалось получить канал {Config.BOT_PLAYERS_CHANNEL}\n{e}")
            await asyncio.sleep(10)

def register_players_task_cogs(bot: Bot) -> None:
    bot.add_cog(__MainPlayersTaskCog(bot))



