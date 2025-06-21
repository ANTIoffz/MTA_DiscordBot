from disnake.ext.commands import Cog, Bot, slash_command, Param, guild_only
from disnake import Colour, Embed
from datetime import datetime
from bot.database import database_bot, database_mta
from bot.misc import Config, check_id, change_player_field, check_bot_db, check_server_db, send_error, send_warning, send_success
from time import time


class __MainModerationCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(
        name="ban",
        description="Банит игрока",
    )
    @check_server_db()
    @guild_only()
    async def ban(
            self, ctx,
            player_id: int = Param(description='Айди игрока'),
            seconds: int = Param(description='Время бана (в секундах)'),
            reason: str = Param(description='Причина ')
    ) -> None:
        player = await check_id(ctx, player_id)
        if player:
            change_player_field(player_id, "banned", time() + seconds)
            await send_success(ctx, f"**Игрок `{player_id}` забанен на `{seconds}` сек (он должен перезайти)\nПричина: `{reason}`**")


    @slash_command(
        name="mute",
        description="Мутит игрока",
    )
    @check_server_db()
    @guild_only()
    async def mute(
            self, ctx,
            player_id: int = Param(description='Айди игрока'),
            seconds: int = Param(description='Время мута (в секундах)'),
            reason: str = Param(description='Причина')
    ) -> None:
        player = await check_id(ctx, player_id)
        if player:
            change_player_field(player_id, "muted", time() + seconds)
            await send_success(ctx, f"**Игрок `{player_id}` замьючен на `{seconds}` сек (он должен перезайти)\nПричина: `{reason}`**")


def register_moderation_cogs(bot: Bot) -> None:
    bot.add_cog(__MainModerationCog(bot))
