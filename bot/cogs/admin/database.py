from disnake.ext.commands import Cog, Bot, slash_command, Param, guild_only
from disnake import Colour, Embed, File
from datetime import datetime, timedelta
from bot.misc import Config, check_id, check_name, check_bot_db, check_server_db, send_success, send_error
from bot.database import database_bot, database_mta
from bot.misc import change_player_field
from textwrap import wrap
from time import time
from os import remove
from json import dump, dumps


class __MainDatabaseCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot


    @slash_command(
        name="server_db_connect",
        description="Подключить БД сервера",
    )
    @guild_only()
    async def server_db_connect(self, ctx):
        database_mta.connect()
        if database_mta.get_status():
            await send_success(ctx, fields=[["💾 База данных", "**`🟢 Подключена`**"]])


    @slash_command(
        name="server_db_close",
        description="Отключить БД сервера",
    )
    @guild_only()
    async def server_db_close(self, ctx):
        if not database_mta.get_status():
            await send_error(ctx, "**Уже закрыто**")
            return
            
        database_mta.connection.close()
        await send_success(ctx, fields=[["💾 База данных", "**`🔴 Отключена`**"]])
            


    @slash_command(
        name="server_db_sql",
        description="Выполнить SQL запрос",
    )
    @check_server_db()
    @guild_only()
    async def server_db_sql(
            self, ctx,
            sql: str = Param(description="SQL запрос"),
            fetch: str = Param(default=False, description="Fetch", choices=["fetchall", "fetchone"])
    ):
        result = database_mta.cursor.execute(sql)
        if fetch == 'fetchall':
            result = database_mta.cursor.fetchall()
        if fetch == 'fetchone':
            result = database_mta.cursor.fetchone()
        if len(str(dumps(result, indent=4))) < 4000:
            await send_success(ctx, f"```json\n{dumps(result, indent=4)}```")
            return
            
        filename = f'{time()}.json'
        with open(filename, 'w', encoding='utf-8') as file:
            dump(result, file, indent=4)
         
        await ctx.send(f'**✅{Config.BOT_SEPARATOR}Успешно**', file=File(filename))
        remove(filename)
        

    @slash_command(
        name="server_db_change_userdata",
        description="Изменить отдельные значения в базе данных",
    )
    @check_server_db()
    @guild_only()
    async def server_db_change_userdata(
            self, ctx, *,
            player_id: int = Param(description='Айди игрока'),
            field: str = Param(description='Название поля в БД'),
            value: str = Param(description='Значение, на которое хотите его изменить', autocomplete=["DEFAULT", "NULL"])
    ):
        if not database_mta.get_status():
            await send_error(ctx, f"**Сначала подключите базу данных**")
            return
            
        player = await check_id(ctx, player_id)
        if player:
            result = change_player_field(player_id, field, value)
            if result:
                await send_success(ctx, f"`{result}`")
            else:
                await send_error(ctx, f"**База данных вернула пустой результат**")



    @slash_command(
        name="server_db_fields",
        description="Показать поля базы данных",
    )
    @check_server_db()
    @guild_only()
    async def server_db_fields(
            self, ctx,
            player_id: int = Param(default=None, description='Айди игрока')
    ):
        if not database_mta.get_status():
            await send_error(ctx, f"**Сначала подключите базу данных**")
            return
            
        if not player_id:
            fields = wrap("\n".join(
                [f"* {name}" for name in database_mta.get_fields('nrp_players')]), 3900, replace_whitespace=False
            )
        else:
            database_mta.cursor.execute("SELECT * FROM `nrp_players` WHERE `id` = %s", (player_id,))
            player_data = database_mta.cursor.fetchone()
            fields = wrap("\n".join(
                ['* {}\n * `{}`'.format(
                    str(title).replace("`", "'"),
                    str(value).replace("`", "'"))
                    for title, value in player_data.items()
                ]), 3900, replace_whitespace=False
            )
        for number, result in enumerate(fields):
            embed = Embed(
                title=f"📃{Config.BOT_SEPARATOR}Поля ({number + 1} / {len(fields)})",
                description=f"**{result}**",
                color=Colour.darker_gray(),
                timestamp=datetime.now(),
            )
            await ctx.send(embed=embed)
            


    @slash_command(
        name="bt_db_connect",
        description="Подключает базу данных бота",
    )
    @guild_only()
    async def bt_db_connect(self, ctx):
        database_bot.connect()
        await send_success(ctx, fields=[['💾 БД бота', '`🟢 Подключена`']])


    @slash_command(
        name="bt_db_close",
        description="Отключается от базы данных бота",
    )
    @guild_only()
    async def bt_db_close(self, ctx):
        if not database_bot.get_status():
            await send_error(ctx, "**Уже закрыто**")
            return
            
        database_bot.connection.close()
        await send_success(ctx, fields=[['💾 БД бота', '`🔴 Отключено`']])



    @slash_command(
        name="bt_db_sql",
        description="Выполнить SQL запрос",
    )
    @check_bot_db()
    @guild_only()
    async def bt_db_sql(
            self, ctx,
            sql: str = Param(description="SQL запрос"),
            fetch: str = Param(default=False, description="Fetch", choices=["fetchall", "fetchone"])
    ):
        result = database_bot.cursor.execute(sql)
        if fetch == 'fetchall':
            result = database_bot.cursor.fetchall()
        if fetch == 'fetchone':
            result = database_bot.cursor.fetchone()
        if len(str(dumps(result, indent=4))) < 4000:
            await send_success(ctx, f"```json\n{dumps(result, indent=4)}```")
            return
            
        filename = f'{time()}.json'
        with open(filename, 'w', encoding='utf-8') as file:
            dump(result, file, indent=4)
         
        await ctx.send(f'**✅{Config.BOT_SEPARATOR}Успешно**', file=File(filename))
        remove(filename)
        
        
def register_database_cogs(bot: Bot) -> None:
    bot.add_cog(__MainDatabaseCog(bot))
