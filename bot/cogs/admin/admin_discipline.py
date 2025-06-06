from disnake.ext.commands import Bot, Cog, slash_command, Param, guild_only
from disnake import Colour, Embed, User, NotFound
from datetime import datetime
from bot.database import database_bot, database_mta
from bot.misc import Config, check_id, change_player_field, check_bot_db, check_server_db, check_is_registered, \
    get_admin_discipline_account, send_warning, \
    send_success, send_error
from time import time
from disnake.ext import tasks


class __MainAdminDisciplineCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot


    @Cog.listener()
    async def on_ready(self) -> None:
        if not self.admin_discipline_autoremove_warnings.is_running():
            self.admin_discipline_autoremove_warnings.start()
        if not self.admin_discipline_autoremove_reprimands.is_running():
            self.admin_discipline_autoremove_reprimands.start()


    async def give_admin_discipline_warning(
            self,
            discord_id: int,
            reason: str,
            author_id: int
    ):
        account = await get_admin_discipline_account(discord_id)

        database_bot.cursor.execute("UPDATE `admins` SET warnings = warnings + 1 WHERE discord_id = %s", (discord_id,))
        database_bot.cursor.execute("UPDATE `admins` SET last_warning_date = %s WHERE discord_id = %s",
                                    (time(), discord_id))
        
        if not Config.BOT_ADMIN_DISCIPLINE_LOG_CHANNEL:
            return
        
        log_channel = self.bot.get_channel(Config.BOT_ADMIN_DISCIPLINE_LOG_CHANNEL)
        embed = Embed(
            title=f"❗{Config.BOT_SEPARATOR}Предупреждение",
            description=f'''**## Выдано предупреждение
* Администратору <@{discord_id}>
* Причина - `{reason}`
* Кем - <@{author_id}>
* Всего предупреждений - `{account['warnings'] + 1}`
                        **''',
            color=Colour.orange(),
            timestamp=datetime.now(),
        )
        await log_channel.send(embed=embed)


    async def give_admin_discipline_reprimand(
            self,
            discord_id: int,
            reason: str,
            author_id: int
    ):
        account = await get_admin_discipline_account(discord_id)

        database_bot.cursor.execute("UPDATE `admins` SET reprimands = reprimands + 1 WHERE discord_id = %s",
                                    (discord_id,))
        database_bot.cursor.execute("UPDATE `admins` SET last_reprimand_date = %s WHERE discord_id = %s",
                                    (time(), discord_id))
        if not Config.BOT_ADMIN_DISCIPLINE_LOG_CHANNEL:
            return
         
        log_channel = self.bot.get_channel(Config.BOT_ADMIN_DISCIPLINE_LOG_CHANNEL)
        embed = Embed(
            title=f"‼️{Config.BOT_SEPARATOR}Выговор",
            description=f'''**## Выдан выговор
* Администратору <@{discord_id}>
* Причина - `{reason}`
* Кем - <@{author_id}>
* Всего выговоров - `{account['reprimands'] + 1}`
                        **''',
            color=Colour.dark_orange(),
            timestamp=datetime.now(),
        )
        await log_channel.send(embed=embed)


    async def take_admin_discipline_warning(
            self,
            discord_id: int,
            reason: str,
            author_id: int
    ):
        account = await get_admin_discipline_account(discord_id)

        database_bot.cursor.execute("UPDATE `admins` SET warnings = warnings - 1 WHERE discord_id = %s", (discord_id,))
        if not Config.BOT_ADMIN_DISCIPLINE_LOG_CHANNEL:
            return
            
        log_channel = self.bot.get_channel(Config.BOT_ADMIN_DISCIPLINE_LOG_CHANNEL)
        embed = Embed(
            title=f"❗{Config.BOT_SEPARATOR}Снято предупреждение",
            description=f'''**## Снято предупреждение
* Администратору <@{discord_id}>
* Причина - `{reason}`
* Кем - <@{author_id}>
* Всего предупреждений - `{account['warnings'] - 1}`
                    **''',
            color=Colour.green(),
            timestamp=datetime.now(),
        )
        await log_channel.send(embed=embed)


    async def take_admin_discipline_reprimand(
            self,
            discord_id: int,
            reason: str,
            author_id: int
    ):
        account = await get_admin_discipline_account(discord_id)

        database_bot.cursor.execute("UPDATE `admins` SET reprimands = reprimands - 1 WHERE discord_id = %s",
                                    (discord_id,))
        
        if not Config.BOT_ADMIN_DISCIPLINE_LOG_CHANNEL:
            return
            
        log_channel = self.bot.get_channel(Config.BOT_ADMIN_DISCIPLINE_LOG_CHANNEL)
        embed = Embed(
            title=f"‼️{Config.BOT_SEPARATOR}Снят выговор",
            description=f'''**## Снят выговор
* Администратору <@{discord_id}>
* Причина - `{reason}`
* Кем - <@{author_id}>
* Всего выговоров - `{account['reprimands'] - 1}`
                        **''',
            color=Colour.green(),
            timestamp=datetime.now(),
        )
        await log_channel.send(embed=embed)


    @slash_command(
        name="give_warning",
        description="Выдаёт предупреждение администратору",
    )
    @check_bot_db()
    @guild_only()
    async def give_warning(
            self, ctx,
            user: User = Param(description="Пинг человека"),
            reason: str = Param(description='Причина')
    ) -> None:
        account = await get_admin_discipline_account(user.id)
        await self.give_admin_discipline_warning(user.id, reason, ctx.author.id)

        await send_success(ctx, f"""**Выдано предупреждение администратору 
{user.mention}
По причине - `{reason}`
Всего `{account['warnings'] + 1} предупреждений`.
        **""")

        if account['warnings'] + 1 >= Config.ADMIN_MAX_WARNINGS:
            database_bot.cursor.execute("UPDATE `admins` SET warnings = 0 WHERE discord_id = %s", (user.id,))
            await self.give_admin_discipline_reprimand(user.id, "Макс. кол-во предупреждений", ctx.author.id)
            
            if account['reprimands'] + 1 >= Config.ADMIN_MAX_REPRIMANDS:
                await send_warning(ctx,f'''**У администратора {user.mention} уже `{account['reprimands'] + 1}` выговора/ов**''')
                               
        if account['reprimands'] >= Config.ADMIN_MAX_REPRIMANDS:
            await send_warning(ctx,f'''**У администратора {user.mention} уже `{account['reprimands']}` выговора/ов**''')


    @slash_command(
        name="give_reprimand",
        description="Выдаёт выговор администратору",
    )
    @check_bot_db()
    @guild_only()
    async def give_reprimand(
            self, ctx,
            user: User = Param(description="Пинг человека"),
            reason: str = Param(description='Причина')
    ) -> None:
        log_channel = self.bot.get_channel(Config.BOT_ADMIN_DISCIPLINE_LOG_CHANNEL)
        account = await get_admin_discipline_account(user.id)
        await self.give_admin_discipline_reprimand(user.id, reason, ctx.author.id)

        await send_success(ctx, f"""**Выдан выговор администратору
{user.mention}
По причине - `{reason}`
Всего `{account['reprimands'] + 1} выговоров`.
        **""")

        if account['reprimands'] + 1 >= Config.ADMIN_MAX_REPRIMANDS:
            await send_warning(ctx,f'''**У администратора {user.mention} уже `{account['reprimands'] + 1}` выговора/ов**''')


    @slash_command(
        name="take_warning",
        description="Забирает предупреждение у администратора",
    )
    @check_bot_db()
    @guild_only()
    async def take_warning(
            self, ctx,
            user: User = Param(description="Пинг человека"),
            reason: str = Param(description='Причина')
    ) -> None:
        account = await get_admin_discipline_account(user.id)
        if account['warnings'] <= 0:
            await send_error(ctx, f"""**У администратора {user.mention} нет предупреждений**""")
            return

        await self.take_admin_discipline_warning(user.id, reason, ctx.author.id)

        await send_success(ctx, f"""**Снято предупреждение администратору 
{user.mention}
По причине - `{reason}`
Всего `{account['warnings'] - 1} предупреждений`.
            **""")
        if account['reprimands'] - 1 >= Config.ADMIN_MAX_REPRIMANDS:
            await send_warning(ctx,f'''**У администратора {user.mention} уже `{account['reprimands'] - 1}` выговора/ов**''')


    @slash_command(
        name="take_reprimand",
        description="Забирает выговор у администратора",
    )
    @check_bot_db()
    @guild_only()
    async def take_reprimand(
            self, ctx,
            user: User = Param(description="Пинг человека"),
            reason: str = Param(description='Причина')
    ) -> None:
        log_channel = self.bot.get_channel(Config.BOT_ADMIN_DISCIPLINE_LOG_CHANNEL)
        account = await get_admin_discipline_account(user.id)
        if account['reprimands'] <= 0:
            await send_error(ctx, f"""**У администратора {user.mention} нет выговоров**""")
            return

        await self.take_admin_discipline_reprimand(user.id, reason, ctx.author.id)

        await send_success(ctx, f"""**Снят выговор администратору
{user.mention}
По причине - `{reason}`
Всего `{account['reprimands'] - 1} выговоров`.
            **""")

        if account['reprimands'] - 1 >= Config.ADMIN_MAX_REPRIMANDS:
            await send_warning(ctx,f'''**У администратора {user.mention} уже `{account['reprimands'] - 1}` выговора/ов**''')


    @tasks.loop(seconds=60)
    async def admin_discipline_autoremove_warnings(self):
        seconds_to_remove = Config.ADMIN_WARNING_DAYS * 86400
        database_bot.cursor.execute("SELECT * FROM `admins` WHERE warnings > 0 AND (%s - last_warning_date) >= %s",
                                    (time(), seconds_to_remove))
        data = database_bot.cursor.fetchall()
        for user in data:
            await self.take_admin_discipline_warning(int(user['discord_id']), f'Авто удаление по истечению {Config.ADMIN_WARNING_DAYS} дней', 1094615871252598934)
            database_bot.cursor.execute("UPDATE `admins` SET last_warning_date = %s WHERE discord_id = %s",
                                        (time(), user['discord_id']))

    @tasks.loop(seconds=60)
    async def admin_discipline_autoremove_reprimands(self):
        seconds_to_remove = Config.ADMIN_REPRIMAND_DAYS * 86400
        database_bot.cursor.execute("SELECT * FROM `admins` WHERE reprimands > 0 AND (%s - last_reprimand_date) >= %s",
                                    (time(), seconds_to_remove))
        data = database_bot.cursor.fetchall()
        for user in data:
            await self.take_admin_discipline_reprimand(int(user['discord_id']), f'Авто удаление по истечению {Config.ADMIN_REPRIMAND_DAYS} дней', 1094615871252598934)
            database_bot.cursor.execute("UPDATE `admins` SET last_reprimand_date = %s WHERE discord_id = %s",
                                        (time(), user['discord_id']))


def register_admin_discipline_cogs(bot: Bot) -> None:
    bot.add_cog(__MainAdminDisciplineCog(bot))
