from disnake.ext.commands import Cog, Bot, slash_command, Param, guild_only
from disnake import Colour, Embed
from datetime import datetime, timedelta
from bot.misc import Config, check_id, check_name, check_bot_db, check_server_db
from time import time


class __MainFindCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(
        name="findbyid",
        description="Ищет игрока по ID",
    )
    @check_server_db()
    @guild_only()
    async def findbyid(
            self, ctx,
            player_id: int = Param(description='Айди игрока'),
            more_info: bool = Param(default=False, description='Нужно больше информации...')
    ):
        player = await check_id(ctx, player_id)
        if player:
            description = f"""
🆔 ID - `{player['id']}`
👑 Access - `{player['accesslevel']}`
🔼 Level - `{player['level']}`
💵 Money - `{player['money']}$`
💳 Donate - `{player['donate']}$`
🕓 Playing time - `{timedelta(hours=0, minutes=0, seconds=int(player['playing_time']))}`
"""
            if player['muted'] and int(player['muted']) - time() > 0: description += f"🔊 Mute - `{timedelta(hours=0, minutes=0, seconds=int(player['muted']) - time())}`\n"
            if player['banned'] and int(player['banned']) - time() > 0: description += f"🔐 Ban - `{timedelta(hours=0, minutes=0, seconds=int(player['banned']) - time())}`\n"
            if more_info:
                description += \
                    f"""
🕓 Register date - `{(datetime.fromtimestamp(int(player['reg_date'])) + timedelta(hours=Config.BOT_GMT)).strftime(f"%d.%m.%Y %I:%M:%S (GMT {'+' if Config.BOT_GMT > 0 else ''}{Config.BOT_GMT})") if player['reg_date'] != None else 'Нет данных'}`
🕓 Last enter - `{(datetime.fromtimestamp(int(player['last_enter_date'])) + timedelta(hours=Config.BOT_GMT)).strftime(f"%d.%m.%Y %I:%M:%S (GMT {'+' if Config.BOT_GMT > 0 else ''}{Config.BOT_GMT})") if player['last_enter_date'] != None else 'Нет данных'}`
🕓 Last date - `{(datetime.fromtimestamp(int(player['last_date'])) + timedelta(hours=Config.BOT_GMT)).strftime(f"%d.%m.%Y %I:%M:%S (GMT {'+' if Config.BOT_GMT > 0 else ''}{Config.BOT_GMT})") if player['last_date'] != None else 'Нет данных'}`
📲 Phone - {player['phone'] if player['phone'] else '`Нет данных`'}
🔑 Register serial - `{player['reg_serial']}`
🔑 Last serial - `{player['last_serial']}`
🔑 Register IP - `{player['reg_ip']}`
🔑 Last IP - `{player['last_ip']}`
"""

            embed = Embed(
                title=f"👥{Config.BOT_SEPARATOR}{player['nickname']}",
                description=f"**{description}**",
                color=Colour.lighter_gray(),
                timestamp=datetime.now(),
            )

            await ctx.send(embed=embed)

    @slash_command(
        name="findbyname",
        description="Ищет игрока по имени",
    )
    @check_server_db()
    @guild_only()
    async def findbyname(
            self, ctx,
            player_nickname: str = Param(description='Ник игрока')
    ):
        players = await check_name(ctx, player_nickname)
        if players:
            players_string = ''.join(f"""
* {player['nickname']}
🆔 ID - `{player['id']}`
👑 Access - `{player['accesslevel']}`
🕓 Playing time - `{timedelta(hours=0, minutes=0, seconds=int(player['playing_time']))}`
📆 Last quit - `{(datetime.fromtimestamp(int(player['last_date'])) + timedelta(hours=Config.BOT_GMT)).strftime(f"%d.%m.%Y %I:%M:%S (GMT {'+' if Config.BOT_GMT > 0 else ''}{Config.BOT_GMT})") if player['last_date'] != None else 'Нет данных'}`
""" for player in players)

            embed = Embed(
                title=f"👥{Config.BOT_SEPARATOR}{len(players)} игроков",
                description=f"**{players_string}**",
                color=Colour.lighter_gray(),
                timestamp=datetime.now(),
            )

            await ctx.send(embed=embed)


def register_find_cogs(bot: Bot) -> None:
    bot.add_cog(__MainFindCog(bot))
