from disnake.ext.commands import Cog, Bot, slash_command, Param, guild_only
from disnake import Colour, Embed, Attachment, User
from datetime import datetime
from bot.database import database_bot, database_mta
from bot.misc import Config, check_id, change_player_field, send_success, send_error, send_warning, get_tea_account, user_has_role, other_user_has_role, check_bot_db
from bot.server_monitoring import server
from time import time
import urllib.request
from pytz import timezone
from math import ceil


class __MainTeaCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
    
    
    async def _give_tea(
            self,
            to_user_id: int, 
            from_user_id: int,
            count: int = 1,
            no_last_tea_date: bool = False
    ):
        to_user_account = await get_tea_account(to_user_id)
        database_bot.cursor.execute("UPDATE `tea` SET tea_count = tea_count + %s WHERE discord_id = %s",
                                    (count, to_user_id))
        if not no_last_tea_date:
            database_bot.cursor.execute("UPDATE `tea` SET last_tea_date = %s WHERE discord_id = %s",
                                        (time(), from_user_id))
        if not Config.BOT_TEA_LOG_CHANNEL:
            return
         
        log_channel = self.bot.get_channel(Config.BOT_TEA_LOG_CHANNEL)
        embed = Embed(
            description=f"**+ {count} ☕ <@{to_user_id}> от <@{from_user_id}>\n* `{to_user_account['tea_count']} > {to_user_account['tea_count'] + count}`**",
            color=Colour.orange()
        )
        await log_channel.send(embed=embed)
        
        
    async def _take_tea(
            self,
            to_user_id: int, 
            from_user_id: int,
            count: int = 1,
            no_last_tea_date: bool = False
    ):
        to_user_account = await get_tea_account(to_user_id)
        database_bot.cursor.execute("UPDATE `tea` SET tea_count = tea_count - %s WHERE discord_id = %s",
                                    (count, to_user_id))
        if not no_last_tea_date:
            database_bot.cursor.execute("UPDATE `tea` SET last_tea_date = %s WHERE discord_id = %s",
                                        (time(), from_user_id))
        if not Config.BOT_TEA_LOG_CHANNEL:
            return
        
        log_channel = self.bot.get_channel(Config.BOT_TEA_LOG_CHANNEL)
        embed = Embed(
            description=f"**- {count} ☕ <@{to_user_id}> от <@{from_user_id}>\n* `{to_user_account['tea_count']} > {to_user_account['tea_count'] - count}`**",
            color=Colour.orange()
        )
        await log_channel.send(embed=embed)
        
        
    async def _set_tea(
            self,
            to_user_id: int, 
            from_user_id: int,
            count: int = 1,
            no_last_tea_date: bool = False
    ):
        to_user_account = await get_tea_account(to_user_id)
        database_bot.cursor.execute("UPDATE `tea` SET tea_count = %s WHERE discord_id = %s", (count, to_user_id))
        if not no_last_tea_date:
            database_bot.cursor.execute("UPDATE `tea` SET last_tea_date = %s WHERE discord_id = %s",
                                        (time(), from_user_id))
        if not Config.BOT_TEA_LOG_CHANNEL:
            return
        
        log_channel = self.bot.get_channel(Config.BOT_TEA_LOG_CHANNEL)
        embed = Embed(
            description=f"**~ {count} ☕ <@{to_user_id}> от <@{from_user_id}>\n* `{to_user_account['tea_count']} > {count}`**",
            color=Colour.orange()
        )
        await log_channel.send(embed=embed)

    
    
    async def _send_log(
            self, ctx, 
            title: str, 
            description: str, 
            color: Colour = Colour.orange()
    ):
        if Config.BOT_TEA_LOG_CHANNEL:
            log_channel = self.bot.get_channel(Config.BOT_TEA_LOG_CHANNEL)
            embed = Embed(
                title=title,
                description=description,
                color=color,
                timestamp=datetime.now(),
            )
            embed.add_field(name='Автор', value=ctx.author.mention)
            embed.add_field(name='Канал', value=ctx.channel.mention)
            await log_channel.send(embed=embed)
        

    @slash_command(
        name="tea_balance",
        description="Посмотреть баланс чая",
    )
    @check_bot_db()
    async def tea_balance(
            self, ctx,
            user: User = Param(default=None, description="Пинг человека")
    ) -> None:
        target_user_id = ctx.author.id if not user else user.id
        from_user_account = await get_tea_account(target_user_id)
        tea_count = from_user_account['tea_count']
        embed = Embed(
            title=f"☕{Config.BOT_SEPARATOR}Количество чая",
            description=f"**У <@{target_user_id}> `{tea_count} чая`**",
            color=Colour.orange(),
            timestamp=datetime.now(),
        )
        await ctx.send(embed=embed)

    
    @slash_command(
        name="tea_give",
        description="Заварить чай",
    )
    @check_bot_db()
    @guild_only()
    async def tea_give(
            self, ctx,
            to_user: User = Param(description="Пинг человека")
    ) -> None:
        from_user_account = await get_tea_account(ctx.author.id)
        to_user_account = await get_tea_account(to_user.id)
        passed = datetime.now() - datetime.fromtimestamp(int(from_user_account['last_tea_date']))
        if ctx.author == to_user:
            await ctx.send(f"**Нельзя заварить чай себе 😡**", ephemeral=True)
            return
        
        if from_user_account['banned'] == 1:
            await ctx.send(f"**Вы заблокированы в системе чая**", ephemeral=True)
            return
            
        if to_user_account['banned'] == 1:
            await ctx.send(f"**Пользователь заблокирован в системе чая**", ephemeral=True)
            return
            
        if await other_user_has_role(to_user.roles, Config.TEA_RECIVE_BAN_ROLES):
            await ctx.send(f"**Этому пользователю нельзя заварить чай**", ephemeral=True)
            return
        
        if await user_has_role(ctx, Config.TEA_GIVE_BAN_ROLES):
            await ctx.send(f"**Вы не можете заваривать чай**", ephemeral=True)
            return
        
        if passed.total_seconds() < Config.TEA_DELAY_SECONDS:
            left_seconds = round(Config.TEA_DELAY_SECONDS - passed.total_seconds())
            left_minutes = round(left_seconds/60)
            await ctx.send(f"**Вы можете заварить чай только через `{left_seconds} секунд` `({left_minutes} минут)`**", ephemeral=True)
            return
            
        await self._give_tea(to_user.id, ctx.author.id)
        embed = Embed(
            description=f"**+ ☕ {to_user.mention} от {ctx.author.mention}**",
            color=Colour.orange()
        )
        await ctx.send(embed=embed)
        #await ctx.send(f"**+ <a:SPOTLIGHTGIF25:1193178219927584789> {to_user.mention} от {ctx.author.mention}**")
    
    
    @slash_command(
        name="tea_give_",
        description="Выдать чай",
    )
    @check_bot_db()
    @guild_only()
    async def tea_give_(
            self, ctx,
            to_user: User = Param(description="Пинг человека"),
            count: int = Param(default=1, description="Количество чая")
    ) -> None:
        from_user_account = await get_tea_account(ctx.author.id)
        await self._give_tea(to_user.id, ctx.author.id, count=count, no_last_tea_date=True)
        embed = Embed(
            description=f"**+ {count} ☕ {to_user.mention} от {ctx.author.mention}**",
            color=Colour.orange()
        )
        await ctx.send(embed=embed)

    
    @slash_command(
        name="tea_take_",
        description="Выпить чай",
    )
    @check_bot_db()
    @guild_only()
    async def tea_take_(
            self, ctx,
            to_user: User = Param(description="Пинг человека"),
            count: int = Param(default=1, description="Количество чая")
    ) -> None:
        from_user_account = await get_tea_account(ctx.author.id)
        await self._take_tea(to_user.id, ctx.author.id, count=count, no_last_tea_date=True)
        embed = Embed(
            description=f"**\- {count} ☕ {to_user.mention} от {ctx.author.mention}**",
            color=Colour.orange()
        )
        await ctx.send(embed=embed)

    
    @slash_command(
        name="tea_set_",
        description="Установить чай",
    )
    @check_bot_db()
    @guild_only()
    async def tea_set_(
            self, ctx,
            to_user: User = Param(description="Пинг человека"),
            count: int = Param(description="Количество чая")
    ) -> None:
        from_user_account = await get_tea_account(ctx.author.id)
        await self._set_tea(to_user.id, ctx.author.id, count=count, no_last_tea_date=True)
        embed = Embed(
            description=f"**~ {count} ☕ {to_user.mention} от {ctx.author.mention}**",
            color=Colour.orange()
        )
        await ctx.send(embed=embed)
    
    
    @slash_command(
        name="tea_leaders",
        description="Посмотреть топ чая",
    )
    @check_bot_db()
    async def tea_leaders(
            self, ctx,
    ) -> None:
        database_bot.cursor.execute(f"SELECT * FROM `tea` WHERE tea_count > 0 ORDER BY `tea`.`tea_count` DESC")
        data = database_bot.cursor.fetchall()[:10]
        text=''
        for number, user in enumerate(data):
            text+=f"**#{number+1}. <@{user['discord_id']}>{'(blocked)' if user['banned'] else ''}**\n"
            text+=f"**⠀⠀⠀◟`{user['tea_count']} чая`**\n"
            text+=f"⠀\n"
            
        embed = Embed(
            title=f"☕{Config.BOT_SEPARATOR}Лидеры чая",
            description=text,
            color=Colour.orange(),
            timestamp=datetime.now(),
        )
        await ctx.send(embed=embed)
        
        
    @slash_command(
        name="tea_ban",
        description="Бан в системе чая",
    )
    @check_bot_db()
    @guild_only()
    async def tea_ban(
            self, ctx,
            user: User = Param(description="Пинг человека")
    ) -> None:
        user_account = await get_tea_account(user.id)
        if user_account['banned'] == 1:
            await send_error(ctx, f"**{user.mention} уже заблокирован**", ephemeral=True)
            return
        database_bot.cursor.execute("UPDATE `tea` SET banned = 1 WHERE discord_id = %s", (user.id,))
        await send_success(ctx, f"**{user.mention} заблокирован**", ephemeral=True)
        await self._send_log(
            ctx, 
            title = f"🔴{Config.BOT_SEPARATOR}Блокировка",
            description = f"**Заблокирован пользователь {user.mention}**",
            color = Colour.red()
        )
        
    
    @slash_command(
        name="tea_unban",
        description="Разбан в системе чая",
    )
    @check_bot_db()
    @guild_only()
    async def tea_unban(
            self, ctx,
            user: User = Param(description="Пинг человека")
    ) -> None:
        user_account = await get_tea_account(user.id)
        if user_account['banned'] == 0:
            await send_error(ctx, f"**{user.mention} не заблокирован**", ephemeral=True)
            return
        database_bot.cursor.execute("UPDATE `tea` SET banned = 0 WHERE discord_id = %s", (user.id,))
        await send_success(ctx, f"**{user.mention} разблокирован**", ephemeral=True)
        await self._send_log(
            ctx, 
            title = f"🟢{Config.BOT_SEPARATOR}Разблокировка",
            description = f"**Разблокирован пользователь {user.mention}**",
            color = Colour.dark_green()
        )
        
    
    @slash_command(
        name="tea_ban_list",
        description="Список банов",
    )
    @check_bot_db()
    @guild_only()
    async def tea_ban_list(
            self, ctx,
            page: int = Param(default = 1, description="Страница")
    ) -> None:
        database_bot.cursor.execute(f"SELECT * FROM `tea` WHERE banned = 1")
        data = database_bot.cursor.fetchall()
        sliced_data = data[(page-1)*10:10]
        text=''
        for number, user in enumerate(sliced_data):
            text+=f"**#{number+1}. <@{user['discord_id']}>{'(blocked)' if user['banned'] else ''}**\n"
            text+=f"**⠀⠀⠀◟`{user['tea_count']} чая`**\n"
            text+=f"⠀\n"
            
        embed = Embed(
            title=f"☕{Config.BOT_SEPARATOR}Заблокированные пользователи `( {page} / {ceil(len(data)/10)} )`",
            description=text,
            color=Colour.orange(),
            timestamp=datetime.now(),
        )
        await ctx.send(embed=embed)
        
        
    @slash_command(
        name="tea_skip_timeout",
        description="Пропустить перезарядку чая",
    )
    @check_bot_db()
    @guild_only()
    async def tea_skip_timeout(
            self, ctx,
            user: User = Param(description="Пинг человека")
    ) -> None:
        database_bot.cursor.execute("UPDATE `tea` SET last_tea_date = 0 WHERE discord_id = %s", (user.id,))
        await send_success(ctx, f"**{user.mention} перезарядка пропущена**", ephemeral=True)
        await self._send_log(
            ctx, 
            title = f"↪{Config.BOT_SEPARATOR}Пропущена перезарядка",
            description = f"**Пропущена перезарядка для {user.mention}**",
        )



def register_tea_cogs(bot: Bot) -> None:
    bot.add_cog(__MainTeaCog(bot))
