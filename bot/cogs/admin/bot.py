from disnake.ext.commands import Cog, Bot, slash_command, Param, CheckFailure, check, guild_only
from disnake import Colour, Embed, Attachment
from datetime import datetime, timedelta
from bot.misc import Config, check_id, check_name, send_warning, send_success, send_error
from bot.ssh import console
from bot.database import database_bot, database_mta
from time import time
from aiohttp import ClientSession
from bot.server_monitoring import server
from sys import exit


class __MainBotCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(
        name="bt_setnickname",
        description="Устанавливает ник боту",
    )
    @guild_only()
    async def bt_setnickname(
            self, ctx,
            nickname: str = Param(description='Новый ник бота')
    ):
        await self.bot.user.edit(username=nickname)
        await send_success(ctx, f"**Новый ник - `{nickname}`**")


    @slash_command(
        name="bt_setavatar",
        description="Устанавливает аватар боту",
    )
    @guild_only()
    async def bt_setavatar(
            self, ctx,
            file: Attachment = Param(description='Новый аватар бота')
    ):
        await ctx.response.defer()
        async with ClientSession() as session:
            async with session.get(file.url) as resp:
                await self.bot.user.edit(avatar=await resp.read())
        await send_success(ctx, f"**Новый аватар установлен**", image=file.url)


    @slash_command(
        name="bt_testerror",
        description="Проверка обработки ошибок. Деление на ноль",
    )
    @guild_only()
    async def bt_testerror(self, ctx):
        await ctx.send(0/0)


    @slash_command(
        name="bt_kill",
        description="Отключить бота",
    )
    @guild_only()
    async def bt_kill(self, ctx):
        await ctx.send("**Пока 😥**")
        exit(1)
    
    
    @slash_command(
        name="bt_status",
        description="Показывает статус бота",
    )

    @guild_only()
    async def bt_status(
            self, ctx
    ) -> None:
        embed = Embed(
            title=f"💻{Config.BOT_SEPARATOR}Статус",
            description=f"",
            color=Colour.dark_green(),
            timestamp=datetime.now(),
        )
        embed.add_field(
            f'💾 БД сервера',
            value='**`🟢 Подключено`**' if database_mta.get_status() else '**`🔴 Отключено`**'
        )
        embed.add_field(
            f'💾 БД бота',
            value='**`🟢 Подключено`**' if database_bot.get_status() else '**`🔴 Отключено`**'
        )
        embed.add_field(
            f'📡 SSH',
            value='**`🟢 Подключено`**' if console.get_status() else '**`🔴 Отключено`**'
        )
        embed.add_field(
            f'🖥 Сервер',
            value='**`🟢 Подключено`**' if server.reconnect() else '**`🔴 Отключено`**'
        )

        await ctx.send(embed=embed)
    
    
    @slash_command(
        name="bt_getserverpresp",
        description="Показать ответ от сервера",
    )
    @guild_only()
    async def bt_getserverpresp(
            self, ctx
    ) -> None:
        if not server.reconnect():
            await send_error(ctx, f"**Сервер не онлайн**")
            return
        
        params = ('game', 'port', 'name', 'gamemode', 'map', 'version', 'somewhat', 'players', 'maxplayers')
        server_info = "\n".join([f"{attr}: {getattr(server.server, attr)}" for attr in params])
        
        await send_success(ctx, f'''
**RAW**
```
{server.server.response}
```
**PARSED**
```
{server_info}
```     ''')

def register_bot_cogs(bot: Bot) -> None:
    bot.add_cog(__MainBotCog(bot))
