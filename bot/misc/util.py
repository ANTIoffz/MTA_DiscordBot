from .config import Config
from bot.database import database_bot, database_mta
from itertools import chain
from disnake import Embed, Colour, ui, ModalInteraction, TextInputStyle, ButtonStyle, NotFound, File
from disnake.ext.commands import Cog, Bot, slash_command, Param, check, CheckFailure, check
from datetime import datetime
from pytz import timezone
from bot.server_monitoring import server
import asyncio
import os
import json
import re


# async def is_main_guild(ctx):
#     if ctx.guild.id in Config.BOT_MAIN_SERVERS_IDS:
#         return True
#     try:
#         await ctx.send(Config.TEXT_IF_NOT_IN_BOT_GUILD)
#     except Exception as exc:
#         print(exc)
#     return False

def find_promo(
        ckey: str
):
    database_mta.cursor.execute(f"SELECT * FROM `nrp_promocodes` WHERE ckey = %s", (ckey,))
    promo = database_mta.cursor.fetchone()
    if promo:
        return promo
    return None


def find_id(
        player_id: int
):
    database_mta.cursor.execute(f"SELECT * FROM `nrp_players` WHERE id = %s", (player_id,))
    player = database_mta.cursor.fetchone()
    if player:
        return player
    return None


def find_name(
        player_nickname: str
):
    database_mta.cursor.execute("SELECT * FROM `nrp_players` WHERE nickname LIKE LOWER(%s)", (f"%{player_nickname}%",))
    player = database_mta.cursor.fetchall()
    if player:
        return player
    return None


def change_player_field(
        player_id: int,
        field: str,
        value
):
    result = database_mta.cursor.execute("UPDATE `nrp_players` SET {} = %s WHERE id = %s".format(field), (value, player_id))
    return result


async def create_promo_db(
        data: dict
) -> None:
    print("INSERT INTO `nrp_promocodes`({}) VALUES({})".format(', '.join(map(str, data.keys())),
                                                            ', '.join(map(str, data.values()))))
    database_mta.cursor.execute(
        "INSERT INTO `nrp_promocodes`({}) VALUES({})".format(', '.join(map(str, data.keys())),
                                                            ', '.join(map(str, data.values())))
    )


async def check_id(
        ctx,
        player_id: int
) -> dict:
    player = find_id(player_id)
    if not player:
        await send_error(ctx, f"**Айди `{player_id}` не найден**")
    else:
        return player


async def check_name(
        ctx,
        player_nickname: str
) -> dict:
    player = find_name(player_nickname)
    if not player:
        await send_error(ctx, f"**Игроки с ником `{player_nickname}` не найдены**")
    else:
        return player


async def get_last_account_id():
    database_mta.cursor.execute(f"SELECT MAX(`id`) FROM `nrp_players`")
    last_id = database_mta.cursor.fetchone()['MAX(`id`)']
    return last_id
    

async def create_bot_account(
        discord_id: int,
        client_id: str,
        ip: str
) -> None:
    database_bot.cursor.execute("INSERT INTO accounts(discord_id, client_id, ip) VALUES (%s, %s, %s)",
                                    (discord_id, client_id, ip)
                                )


async def create_game_account(
        data: dict
) -> int:
    database_mta.cursor.execute(
        "INSERT INTO `nrp_players`({}) VALUES({})".format(', '.join(map(str, data.keys())),
                                                            ', '.join(map(str, data.values())))
    )
    database_mta.cursor.execute(
        "SELECT LAST_INSERT_ID()"
    )
    player_id = int(database_mta.cursor.fetchone()['LAST_INSERT_ID()'])
    return player_id


async def bind_account(
        discord_id: int,
        player_id: int
) -> None:
    database_bot.cursor.execute("SELECT game_ids FROM accounts WHERE discord_id = %s", (discord_id,))
    current_ids = json.loads(database_bot.cursor.fetchone()['game_ids'])
    current_ids.append(player_id)
    #print(f"{current_ids=}")
    database_bot.cursor.execute(f"UPDATE accounts SET game_ids = '{current_ids}' WHERE discord_id = %s", (discord_id))


async def unbind_account(
        discord_id: int,
        player_id: int
) -> None:
    current_ids = await get_binded_accounts(discord_id)
    current_ids.remove(player_id)
    database_bot.cursor.execute(f"UPDATE accounts SET game_ids = '{current_ids}' WHERE discord_id = %s", (discord_id))


async def get_binded_accounts(discord_id):
    database_bot.cursor.execute("SELECT game_ids FROM accounts WHERE discord_id = %s", (discord_id,))
    binded_accounts = json.loads(database_bot.cursor.fetchone()['game_ids'])
    return binded_accounts


async def check_id_is_registered(
        player_id: int
):
    database_bot.cursor.execute(f"SELECT * FROM accounts")
    accounts = database_bot.cursor.fetchall()
    for account in accounts:
        if player_id in json.loads(account['game_ids']):
            return account
    return False


async def check_is_registered(discord_id: int):
    database_bot.cursor.execute("SELECT * FROM `accounts` WHERE discord_id = %s", (discord_id,))
    account = database_bot.cursor.fetchone()
    if account:
        return account
    return False


async def get_admin_discipline_account(discord_id: int):
    database_bot.cursor.execute("SELECT * FROM `admins` WHERE discord_id = %s", (discord_id,))
    data = database_bot.cursor.fetchone()
    if not data:
        database_bot.cursor.execute("INSERT INTO `admins` (discord_id) VALUES (%s)", (discord_id,))
        database_bot.cursor.execute("SELECT * FROM `admins` WHERE discord_id = %s", (discord_id,))
        data = database_bot.cursor.fetchone()
    return data


async def change_account(account_id, client_id):
    database_mta.cursor.execute("SELECT * FROM `nrp_players` WHERE client_id = %s", (client_id,))
    old_account = database_mta.cursor.fetchone()
    database_mta.cursor.execute("SELECT * FROM `nrp_players` WHERE id = %s", (account_id,))
    new_account = database_mta.cursor.fetchone()
    database_mta.cursor.execute("UPDATE `nrp_players` SET client_id = NULL WHERE client_id = %s", (client_id,))
    # database_mta.cursor.execute("UPDATE `nrp_players` SET reg_serial = NULL WHERE client_id = %s", (client_id,))
    database_mta.cursor.execute("UPDATE `nrp_players` SET client_id = %s WHERE id = %s", (client_id, account_id))
    return old_account, new_account


async def get_client_id(
        discord_id: int
):
    database_bot.cursor.execute("SELECT client_id FROM `accounts` WHERE discord_id = %s", (discord_id,))
    client_id = database_bot.cursor.fetchone()
    return client_id


class DatabaseNotConnected(CheckFailure):
    pass


def check_server_db():
    async def predicate(ctx):
        if not database_mta.get_status():
            raise DatabaseNotConnected('**Подключите базу данных сервера**')
        return True
    return check(predicate)


def check_bot_db():
    async def predicate(ctx):
        if not database_bot.get_status():
            raise DatabaseNotConnected('**Подключите базу данных бота**')
        return True
    return check(predicate)


async def send_success(
        ctx, 
        description: str = "", 
        image: str = None, 
        fields: list = None, 
        ephemeral: bool = False,
        file: str = None,
        view: ui.View = None
):
    embed = Embed(
        title=f"✅{Config.BOT_SEPARATOR}Успешно",
        description=description,
        color=Colour.dark_green(),
        timestamp=datetime.now(),
    )
    if image:
        embed.set_image(url=image)
    if file:
        embed.set_thumbnail(file=File(file))
    if fields:
        for field in fields:
            embed.add_field(field[0], field[1])
    if view:
        await ctx.send(embed=embed, ephemeral=ephemeral, view=view)
    else:
        await ctx.send(embed=embed, ephemeral=ephemeral)


async def send_warning(
        ctx,
        description: str = "",
        image: str = None,
        fields: list = None,
        ephemeral: bool = False,
        file: str = None,
        view: ui.View = None
):
    embed = Embed(
        title=f"⚠️{Config.BOT_SEPARATOR}Внимание",
        description=description,
        color=Colour.orange(),
        timestamp=datetime.now(),
    )
    if image:
        embed.set_image(url=image)
    if file:
        embed.set_thumbnail(file=File(file))
    if fields:
        for field in fields:
            embed.add_field(field[0], field[1])
    if view:
        await ctx.send(embed=embed, ephemeral=ephemeral, view=view)
    else:
        await ctx.send(embed=embed, ephemeral=ephemeral)


async def send_error(
        ctx, 
        description: str = "", 
        image: str = None, 
        fields: list = None,
        ephemeral: bool = False,
        file: str = None,
        view: ui.View = None
):
    embed = Embed(
        title=f"❌{Config.BOT_SEPARATOR}Ошибка",
        description=description,
        color=Colour.red(),
        timestamp=datetime.now(),
    )
    if image:
        embed.set_image(url=image)
    if file:
        embed.set_thumbnail(file=File(file))
    if fields:
        for field in fields:
            embed.add_field(field[0], field[1])
    if view:
        await ctx.send(embed=embed, ephemeral=ephemeral, view=view)
    else:
        await ctx.send(embed=embed, ephemeral=ephemeral)


async def user_has_role(ctx, roles: list):
    user_roles = ctx.author.roles
    for role in user_roles:
        if role.id in roles:
            return True
    return False


async def other_user_has_role(user_roles: list, roles: list):
    for role in user_roles:
        if role.id in roles:
            return True
    return False


async def check_main_guild(guild):
    print(f"Checking {guild.id}")
    if int(guild.id) not in Config.BOT_MAIN_SERVERS_IDS:
        print(f"Leave from {guild.id}")
        await guild.text_channels[0].send("Я не хочу работать в таких условиях :rage:")
        await guild.leave()
    return


class AreYouSureModal(ui.Modal):
    def __init__(self, 
            command: str, 
            agree_text: str = None,
            timeout: int = 300,
        ):
        self.command = command
        self.timeout = timeout
        if agree_text is None:
            self.agree_text = 'ДА'
        
        components = [
            ui.TextInput(
                label=f'Введите "{self.agree_text}"',
                custom_id="areyousure",
                style=TextInputStyle.short
            )
        ]
        super().__init__(
            title="Вы уверены?",
            timeout=self.timeout,
            components=components,
        )

    async def callback(self, ctx: ModalInteraction):
        if ctx.text_values['areyousure'] != self.agree_text:
            await send_error(ctx, "**Отмена**")
            return
        os.system(self.command)
        await send_success(ctx, "**Команда выполнена**")
            

            
async def send_areyousure_message(ctx, text: str, yes_id: str, no_id: str, timout: int = 60):
    await ctx.send(
            text,
            components=[
                ui.Button(label="Да", style=ButtonStyle.success, custom_id=yes_id),
                ui.Button(label="Нет", style=ButtonStyle.danger, custom_id=no_id),
            ],
        )
    await asyncio.sleep(timout)
    try:
        await ctx.delete_original_response()
    except NotFound:
        pass
        

async def get_tea_account(discord_id: int):
    database_bot.cursor.execute("SELECT * FROM `tea` WHERE discord_id = %s", (discord_id,))
    data = database_bot.cursor.fetchone()
    if not data:
        database_bot.cursor.execute("INSERT INTO `tea` (discord_id) VALUES (%s)", (discord_id,))
        database_bot.cursor.execute("SELECT * FROM `tea` WHERE discord_id = %s", (discord_id,))
        data = database_bot.cursor.fetchone()
    return data
