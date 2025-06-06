from pytz import timezone
from disnake.ext.commands import Bot, Cog, slash_command
from disnake import Colour, Embed
from disnake.ext import tasks
from datetime import datetime
from bot.database import database_bot, database_mta
from bot.misc import Config, check_id, change_player_field, send_error, send_success
from bot.server_monitoring import server
import urllib.request
from aiohttp import ClientSession, ClientTimeout
from disnake.errors import DiscordServerError
import asyncio


class __MainStatusTaskCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self) -> None:
        if not self.status_task.is_running():
            self.status_task.start()


    @tasks.loop(seconds=10)
    async def status_task(self):
        try:
            channel = self.bot.get_channel(Config.BOT_STATUS_CHANNEL)
            last_message = await channel.history(limit=1).flatten()
            server_status = server.reconnect()

            try:
                async with ClientSession() as session:
                    async with session.get(Config.WEBSITE_URL, timeout=5) as resp:
                        website_status = resp.status
            except:
                website_status = False

            try:
                async with ClientSession() as session:
                    async with session.get(Config.FORUM_URL, timeout=5) as resp:
                        forum_status = resp.status
            except:
                forum_status = False
            
            try:
                has_password = bool(server.server.somewhat)
            except AttributeError:
                has_password = False
            except ValueError:
                has_password = False
            
            has_password = False
            
            embed = Embed(
                title=f"💻{Config.BOT_SEPARATOR}Статус",
                description=f"",
                color=(Colour.dark_green() if not has_password else Colour.orange()) if server_status else Colour.red(),
            )
            
            if Config.WEBSITE_URL:
                embed.add_field(
                    f'📱 Сайт',
                    value='**`🟢 Онлайн`**' if website_status == 200 else '**`🔴 Оффлайн`**'
                )
            
            if Config.FORUM_URL:
                embed.add_field(
                    f'📖 Форум',
                    value='**`🟢 Онлайн`**' if forum_status == 200 else '**`🔴 Оффлайн`**'
                )


            embed.add_field(
                f'🖥 Сервер',
                value=('**`🟢 Онлайн`**' if not has_password else '**`🟠 Debug`**') if server_status else '**`🔴 Оффлайн`**'
            )

            if server_status:
                try:
                    embed.add_field(
                        'Онлайн',
                        value=f'**`{server.server.players}` / `{server.server.maxplayers}`**'
                    )
                except AttributeError:
                    pass
                
            embed.add_field('Время МСК', value=f"**`{datetime.now(timezone('Europe/Moscow')).strftime('%H:%M:%S')}`**")

            if last_message and last_message[0].author == self.bot.user:
                await last_message[0].edit(embed=embed)
            else:
                await channel.send(embed=embed)

        except DiscordServerError:
            await asyncio.sleep(10)

        except AttributeError as e:
            print(f"[ERROR] Не удалось получить канал {Config.BOT_STATUS_CHANNEL}\n{e}")
            await asyncio.sleep(10)
    

def register_status_task_cogs(bot: Bot) -> None:
    bot.add_cog(__MainStatusTaskCog(bot))
