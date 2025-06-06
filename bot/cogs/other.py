from pytz import timezone
from disnake.ext.commands import Bot, Cog, slash_command
from disnake import Colour, Embed
from disnake.ext import tasks, commands
from datetime import datetime
from bot.database import database_bot, database_mta
from bot.misc import Config, check_id, change_player_field, send_error, send_warning, send_success, check_main_guild
from bot.server_monitoring import server
import urllib.request


class __MainOtherCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
    

    @Cog.listener()
    async def on_ready(self) -> None:
        for guild in self.bot.guilds:
            await check_main_guild(guild)
        print('Я рэди эээ')


    @Cog.listener()
    async def on_guild_join(self, guild) -> None:
        await check_main_guild(guild)


    @Cog.listener()
    async def on_slash_command_error(
            self, ctx,
            error
    ):
        await send_error(ctx, error)


    @Cog.listener()
    async def on_slash_command(
            self, ctx
    ):
        if str(ctx.data.name).strip() not in Config.BOT_LOG_EXCEPTIONS:
            command_name = ctx.data.name
            raw_options = ctx.data.options
            options = ", ".join(f"{option['name']}: {option['value']}" for option in raw_options)
            text_command = f"/{command_name} {options}"

            log_channel = self.bot.get_channel(Config.BOT_LOG_CHANNEL)

            embed = Embed(
                title=f"❗{Config.BOT_SEPARATOR}Получена команда",
                description=f"**`{text_command}`**",
                color=Colour.dark_green(),
                timestamp=datetime.now(),
            )
            embed.add_field(name='Автор', value=ctx.author.mention)
            embed.add_field(name='Канал', value=f"<#{ctx.channel.id}>")

            await log_channel.send(embed=embed)
    
    

def register_other_cogs(bot: Bot) -> None:
    bot.add_cog(__MainOtherCog(bot))
