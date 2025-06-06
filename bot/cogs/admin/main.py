from disnake.ext.commands import Cog, Bot, slash_command, Param, guild_only
from disnake import Colour, Embed, ui, ButtonStyle
from datetime import datetime
from bot.database import database_bot, database_mta
from bot.misc import Config, check_id, change_player_field, check_bot_db, check_server_db, send_error, send_success, \
    send_warning
from bot.server_monitoring import server
from bot.ssh import console
from time import time
import re

class __MainAdminCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(
        name="give_admin",
        description="Устанавливает уровень доступа",
    )
    @check_server_db()
    @guild_only()
    async def give_admin(
            self, ctx,
            player_id: int = Param(description='Айди игрока'),
            level: int = Param(description='Желаемый уровень')
    ) -> None:
        player = await check_id(ctx, player_id)
        if player:
            change_player_field(player_id, "accesslevel", level)
            await send_success(ctx, f"**Уровень прав игрока `{player['nickname']}({player_id})` изменён на `{level}`**")


    @slash_command(
        name="give_money",
        description="Выдаёт деньги",
    )
    @check_server_db()
    @guild_only()
    async def give_money(
            self, ctx,
            player_id: int = Param(description='Айди игрока'),
            amount: int = Param(description='Количество')
    ) -> None:
        player = await check_id(ctx, player_id)
        if player:
            change_player_field(player_id, "money", int(player['money']) + amount)
            await send_success(ctx, f"**Игроку `{player['nickname']}({player_id})` выдано `{amount}` $**")


    @slash_command(
        name="take_money",
        description="Забирает деньги",
    )
    @check_server_db()
    @guild_only()
    async def take_money(
            self, ctx,
            player_id: int = Param(description='Айди игрока'),
            amount: int = Param(description='Количество')
    ) -> None:
        player = await check_id(ctx, player_id)
        if player:
            change_player_field(player_id, "money", int(player['money']) - amount)
            await send_success(ctx, f"**У игрока `{player['nickname']}({player_id})` отобрано `{amount}` $**")


    @slash_command(
        name="set_money",
        description="Устанавливает деньги",
    )
    @check_server_db()
    @guild_only()
    async def set_money(
            self, ctx,
            player_id: int = Param(description='Айди игрока'),
            amount: int = Param(description='Количество')
    ) -> None:
        player = await check_id(ctx, player_id)
        if player:
            change_player_field(player_id, "money", amount)
            await send_success(ctx, f"**Игроку `{player['nickname']}({player_id})` установлено `{amount}` $**")


    @slash_command(
        name="give_rating",
        description="Выдаёт соц.рейтинг",
    )
    @check_server_db()
    @guild_only()
    async def give_rating(
            self, ctx,
            player_id: int = Param(description='Айди игрока'),
            amount: int = Param(description='Количество')
    ) -> None:
        player = await check_id(ctx, player_id)
        if player:
            change_player_field(player_id, "social_rating", int(player['social_rating']) + amount)
            await send_success(ctx, f"**Игроку `{player['nickname']}({player_id})` выдано `{amount}` соц.рейтинга**")


    @slash_command(
        name="take_rating",
        description="Забирает соц.рейтинг",
    )
    @check_server_db()
    @guild_only()
    async def take_rating(
            self, ctx,
            player_id: int = Param(description='Айди игрока'),
            amount: int = Param(description='Количество')
    ) -> None:
        player = await check_id(ctx, player_id)
        if player:
            change_player_field(player_id, "social_rating", int(player['social_rating']) - amount)
            await send_success(ctx, f"**У игрока `{player['nickname']}({player_id})` отобрано `{amount}` соц.рейтинга**")


    @slash_command(
        name="set_rating",
        description="Устанавливает соц.рейтинг",
    )
    @check_server_db()
    @guild_only()
    async def set_rating(
            self, ctx,
            player_id: int = Param(description='Айди игрока'),
            amount: int = Param(description='Количество')
    ) -> None:
        player = await check_id(ctx, player_id)
        if player:
            change_player_field(player_id, "social_rating", amount)
            await send_success(ctx, f"**Игроку `{player['nickname']}({player_id})` установлен `{amount}` соц.рейтинг**")


    @slash_command(
        name="give_donate",
        description="Выдаёт донат валюту",
    )
    @check_server_db()
    @guild_only()
    async def give_donate(
            self, ctx,
            player_id: int = Param(description='Айди игрока'),
            amount: int = Param(description='Количество')
    ) -> None:
        player = await check_id(ctx, player_id)
        if player:
            change_player_field(player_id, "donate", int(player['donate']) + amount)
            await send_success(ctx, f"**Игроку `{player['nickname']}({player_id})` выдано `{amount}` донат валюты**")


    @slash_command(
        name="take_donate",
        description="Забирает донат валюту",
    )
    @check_server_db()
    @guild_only()
    async def take_donate(
            self, ctx,
            player_id: int = Param(description='Айди игрока'),
            amount: int = Param(description='Количество')
    ) -> None:
        player = await check_id(ctx, player_id)
        if player:
            change_player_field(player_id, "donate", int(player['donate']) - amount)
            await send_success(ctx, f"**У игрока `{player['nickname']}({player_id})` отобрано `{amount}` донат валюты**")


    @slash_command(
        name="set_donate",
        description="Устанавливает донат валюту",
    )
    @check_server_db()
    @guild_only()
    async def set_donate(
            self, ctx,
            player_id: int = Param(description='Айди игрока'),
            amount: int = Param(description='Количество')
    ) -> None:
        player = await check_id(ctx, player_id)
        if player:
            change_player_field(player_id, "donate", amount)
            await send_success(ctx, f"**Игроку `{player['nickname']}({player_id})` установлено `{amount}` донат валюты**")


    @slash_command(
        name="set_level",
        description="Устанавливает уровень",
    )
    @check_server_db()
    @guild_only()
    async def set_level(
            self, ctx,
            player_id: int = Param(description='Айди игрока'),
            amount: int = Param(description='Количество')
    ) -> None:
        player = await check_id(ctx, player_id)
        if player:
            change_player_field(player_id, "level", amount)
            await send_success(ctx, f"**Игроку `{player['nickname']}({player_id})` установлен `{amount}` уровень**")


    @slash_command(
        name="set_nickname",
        description="Устанавливает ник",
    )
    @check_server_db()
    @guild_only()
    async def set_nickname(
            self, ctx,
            player_id: int = Param(description='Айди игрока'),
            nickname: str = Param(description='Новый ник')
    ) -> None:
        player = await check_id(ctx, player_id)
        if player:
            change_player_field(player_id, "nickname", nickname)
            await send_success(ctx, f"**Игроку `{player['nickname']}({player_id})` установлен ник `{nickname}`**")


    @slash_command(
        name="set_skin",
        description="Устанавливает скин",
    )
    @check_server_db()
    @guild_only()
    async def set_skin(
            self, ctx,
            player_id: int = Param(description='Айди игрока'),
            nickname: str = Param(description='Новый скин')
    ) -> None:
        player = await check_id(ctx, player_id)
        if player:
            change_player_field(player_id, "skin", nickname)
            await send_success(ctx, f"**Игроку `{player['nickname']}({player_id})` установлен ник `{nickname}`**")

    
    
def register_admin_cogs(bot: Bot) -> None:
    bot.add_cog(__MainAdminCog(bot))
