from disnake.ext.commands import Cog, Bot, slash_command, Param, guild_only
from disnake import Colour, Embed
from datetime import datetime, timedelta
from bot.misc import Config, check_id, check_name, send_warning, send_error, send_success
from bot.ssh import console
from time import time


class __MainSSHCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(
        name="ssh_connect",
        description="Включает SSH",
    )
    @guild_only()
    async def ssh_connect(
            self, ctx
    ):
        output = console.connect()
        if output:
            await send_success(ctx, f"```{output}```")
        else:
            await send_error(ctx, f"**Хост не отправил никаких данных**")


    @slash_command(
        name="ssh_close",
        description="Отключает SSH",
    )
    @guild_only()
    async def ssh_close(
            self, ctx
    ):
        if console.get_status():
            console.close()
            await send_success(ctx, fields=[['📡 SSH', '**`🔴 Отключено`**']])

        else:
            await send_error(ctx, '**Не подключено**')


    @slash_command(
        name="ssh_exec",
        description="Отправить команду по SSH",
    )
    @guild_only()
    async def ssh_exec(
            self, ctx,
            command: str = Param(description="Команда")
    ):  
        if not console.get_status():
            await send_error(ctx, '**Подключите SSH**')
            return
            
        output = console.exec_command(command)
        embed = Embed(
            title=f"",
            description=f"```{output}```",
            color=Colour.dark_green(),
            timestamp=datetime.now(),
        )
        await ctx.send(embed=embed)


def register_SSH_cogs(bot: Bot) -> None:
    if Config.SSH_IP and Config.SSH_PORT and Config.SSH_USER and Config.SSH_PASSWORD:
        bot.add_cog(__MainSSHCog(bot))
