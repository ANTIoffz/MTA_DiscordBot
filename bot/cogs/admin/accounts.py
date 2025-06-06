import re
from disnake.ext.commands import Cog, Bot, slash_command, Param, check, CheckFailure, guild_only
from disnake import Colour, Embed, ui, ApplicationCommandInteraction, ButtonStyle, MessageInteraction, User, NotFound
from datetime import datetime, timedelta
from bot.misc import Config, check_id, check_name, bind_account, bind_account, \
    check_is_registered, create_game_account, unbind_account, get_binded_accounts, create_bot_account, find_id, \
    change_account, get_client_id, find_name, check_id_is_registered, check_bot_db, check_server_db, send_success, \
    send_warning, send_error, user_has_role
from bot.database import database_bot, database_mta
from time import time
import json
import asyncio


class __MainAccountsCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.player = None
        self.register_user = None


    @Cog.listener()
    async def on_button_click(self, ctx):
        if ctx.component.custom_id == "accounts_my_account":
            if self.register_user == ctx.author:
                await ctx.message.delete()
                await self.confirm_register(ctx)

        elif ctx.component.custom_id == "accounts_not_my_account":
            if self.register_user == ctx.author:
                await ctx.message.delete()

    async def confirm_register(self, ctx):
        if not self.player['last_ip']:
            await send_error(ctx, "**Ваш ip не найден. Вы вообще были в игре?**")
        await create_bot_account(self.register_user.id, self.player['client_id'], self.player['last_ip'])
        await bind_account(self.register_user.id, self.player['id'])
        await send_success(ctx, f"**Вы зарегистрировались в боте как\n`{self.player['nickname']} [{self.player['id']}]`**")


    @slash_command(
        name="register",
        description="Регистрация в системе аккаунтов",
    )
    @check_server_db()
    @check_bot_db()
    @guild_only()
    async def register(
            self, ctx,
            player_id: int = Param(description="Ваш ID на сервере")
    ) -> None:

        self.register_user = ctx.author
        account = await check_is_registered(self.register_user.id)
        if account:
            await send_error(ctx, f"**Вы уже зарегистрированы**")
            return

        check_player_id = await check_id_is_registered(player_id)
        if check_player_id:
            await send_error(ctx, f"**Данный аккаунт уже привязан к\n<@{check_player_id['discord_id']}>**")
            return

        self.player = await check_id(ctx, player_id)
        if self.player:
            await ctx.send(
                f"**Вы {self.player['nickname']}?**",
                components=[
                    ui.Button(label="Да", style=ButtonStyle.success, custom_id="accounts_my_account"),
                    ui.Button(label="Нет", style=ButtonStyle.danger, custom_id="accounts_not_my_account"),
                ],
            )
        await asyncio.sleep(60)
        
        try:
            await ctx.delete_original_response()
        except NotFound:
            pass



    @slash_command(
        name="create_account",
        description="Создание нового аккаунта",
    )
    @check_server_db()
    @check_bot_db()
    @guild_only()
    async def create_account(
            self, ctx,
            nickname: str = Param(description="Имя Фамилия", converter=lambda inter, nickname: nickname.title()),
            birthday: str = Param(description="Дата рождения (день.месяц.год)"),
            #email: str = Param(description="Ваша электронная почта"),
            #login: str = Param(description="Логин"),
            #password: str = Param(description="Пароль")
    ) -> None:
        account = await check_is_registered(ctx.author.id)
        if not account:
            await send_error(ctx, f"**Вы не зарегистрированы**", ephemeral=True)
            return

        binded_accounts = await get_binded_accounts(ctx.author.id)

        if len(binded_accounts) >= Config.MAX_ACCOUNTS and not await user_has_role(ctx, Config.IGNORE_MAX_ACCOUNTS_ROLES):
            await send_error(ctx, f"**У вас уже есть максимально кол-во аккаунтов ({Config.MAX_ACCOUNTS})**", ephemeral=True)
            return

        if len(nickname.split()) != 2:
            await send_error(ctx, f"**Никнейм должен быть в формате\n`Имя Фамилия`**", ephemeral=True)
            return

        if len(nickname.split()[0]) < Config.NICKNAME_MIN_LEN or len(nickname.split()[1]) < Config.NICKNAME_MIN_LEN:
            await send_error(ctx, f"**`Имя и Фамилия` должны быть длиннее {Config.NICKNAME_MIN_LEN} символов**", ephemeral=True)
            return
        
        #if len(login) < Config.LOGIN_MIN_LEN:
        #    await send_error(ctx, f"**`Логин` должен быть длиннее {Config.LOGIN_MIN_LEN} символов**", ephemeral=True)
        #    return
            
        #if len(password) < Config.PASSWORD_MIN_LEN:
        #    await send_error(ctx, f"**`Пароль` должен быть длиннее {Config.PASSWORD_MIN_LEN} символов**", ephemeral=True)
        #    return
        
        if not bool(re.match(r'[А-яЁё]+', nickname)):
            await send_error(ctx, f"**В никнейме можно использовать только `русские буквы`**", ephemeral=True)
            return
        
        #if not "@" in email or not "." in email:
        #    await send_error(ctx, f"**Странная почта**", ephemeral=True)
        #    return

        
        try:
            birthday = round((datetime.strptime(birthday, '%d.%m.%Y') - datetime(1970, 1, 1)).total_seconds())
        except ValueError:
            await send_error(ctx, f"**Используйте формат `День.Месяц.Год`**", ephemeral=True)
            return

        data = {
            'nickname': f"'{nickname}'",
            'birthday': f"'{birthday}'",
            'reg_serial': f"'{account['client_id']}'",
            'last_serial': f"'{account['client_id']}'",
            'reg_ip': f"'{account['ip']}'",
            'last_ip': f"'{account['ip']}'",
            'reg_date': time(),
            #'email': f"'{email}'",
            #'login': f"'{login}'",
            #'password': f"'{password}'"
        }
        data.update(Config.NEW_ACCOUNT_SETTINGS)

        player_id = await create_game_account(data)
        await bind_account(ctx.author.id, player_id)
        await send_success(ctx, f"**Ваш аккунт создан и привязан\n`{nickname} [{player_id}]`**", ephemeral=True)


    @slash_command(
        name="create_account_",
        description="Создание нового аккаунта игнорируя фильтры",
    )
    @check_server_db()
    @check_bot_db()
    @guild_only()
    async def create_account_(
            self, ctx,
            nickname: str = Param(description="Имя Фамилия", converter=lambda inter, nickname: nickname.title()),
            birthday: str = Param(description="Дата рождения (день.месяц.год)"),
            #email: str = Param(description="Ваша электронная почта"),
            #login: str = Param(description="Логин"),
            #password: str = Param(description="Пароль")
    ) -> None:
        nickname = nickname.title()
        account = await check_is_registered(ctx.author.id)

        if not account:
            await send_error(ctx, f"**Вы не зарегистрированы**", ephemeral=True)
            return

        try:
            birthday = round((datetime.strptime(birthday, '%d.%m.%Y') - datetime(1970, 1, 1)).total_seconds())
        except ValueError:
            await send_error(ctx, f"**Используйте формат `День.Месяц.Год`**", ephemeral=True)
            return

        data = {
            'nickname': f"'{nickname}'",
            'birthday': f"'{birthday}'",
            'reg_serial': f"'{account['client_id']}'",
            'last_serial': f"'{account['client_id']}'",
            'reg_ip': f"'{account['ip']}'",
            'last_ip': f"'{account['ip']}'",
            'reg_date': time(),
            #'email': f"'{email}'",
            #'login': f"'{login}'",
            #'password': f"'{password}'"
        }
        data.update(Config.NEW_ACCOUNT_SETTINGS)

        player_id = await create_game_account(data)
        await bind_account(ctx.author.id, player_id)
        await send_success(ctx, f"**Ваш аккунт создан и привязан\n`{nickname} [{player_id}]`**", ephemeral=True)


    @slash_command(
        name="accounts",
        description="Показать привязаные аккаунты",
    )
    @check_server_db()
    @check_bot_db()
    @guild_only()
    async def accounts(
            self, ctx,
            user: User = Param(default=None, description="Пинг человека")
    ) -> None:
        if not user:
            user = ctx.author

        account = await check_is_registered(user.id)
        if not account:
            if user == ctx.author:
                await send_error(ctx, f"**Вы не зарегистрированы**")
            else:
                await send_error(ctx, f"**Человек не зарегистрирован**")
            return

        binded_accounts = await get_binded_accounts(user.id)
        description = f"{user.mention}\n"
        for account_id in binded_accounts:
            try:
                player_nickname = find_id(account_id)['nickname']
            except:
                player_nickname = "Нет данных"
            description += "".join(f"`{player_nickname} [{account_id}]`\n")

        embed = Embed(
            title=f"👥{Config.BOT_SEPARATOR}Аккаунты {user.mention}",
            description=f"**{description}**",
            color=Colour.green(),
            timestamp=datetime.now(),
        )
        await ctx.send(embed=embed)
    
    
    @slash_command(
        name="bind_account",
        description="Привязать аккаунт к человеку",
    )
    @check_server_db()
    @check_bot_db()
    @guild_only()
    async def bind_account(
            self, ctx,
            user: User = Param(description="Пинг человека"),
            player_id: int = Param(description="Игровой ID")
    ) -> None:
        account = await check_is_registered(user.id)
        if not account:
            await send_error(ctx, f"**Человек не зарегистрирован**")
            return

        if player_id in await get_binded_accounts(user.id):
            await send_error(ctx, f"**Данный аккаунт уже привязан к этому пользователю**")
            return

        player = await check_id(ctx, player_id)
        if player:
            await bind_account(user.id, player_id)
            await send_success(ctx,f"**Аккаунт `{player['nickname']} [{player_id}]`\nпривязан к пользователю {user.mention}**")


    @slash_command(
        name="unbind_account",
        description="Отвязать аккаунт от человека",
    )
    @check_server_db()
    @check_bot_db()
    @guild_only()
    async def unbind_account(
            self, ctx,
            user: User = Param(description="Пинг человека"),
            player_id: int = Param(description="Его игровой ID")
    ) -> None:
        account = await check_is_registered(user.id)
        if not account:
            await send_error(ctx, f"**Человек не зарегистрирован**")
            return

        binded_accounts = await get_binded_accounts(user.id)
        try:
            player_nickname = find_id(player_id)['nickname']
        except:
            player_nickname = "Нет данных"

        if player_id not in binded_accounts:
            await send_error(ctx, f"**Аккаунт `{player_nickname}[{player_id}]`\nне привязан к пользователю {user.mention}**")
            return

        await unbind_account(user.id, player_id)
        await send_success(ctx, f"**Аккаунт `{player_nickname}[{player_id}]`\nбольше не привязан к пользователю {user.mention}**")


    @slash_command(
        name="change_account",
        description="Сменить аккаунт",
    )
    @check_server_db()
    @check_bot_db()
    @guild_only()
    async def change_account(
            self, ctx,
            player_id: int = Param(description="ID аккаунта")
    ) -> None:
        account = await check_is_registered(ctx.author.id)
        if not account:
            await send_error(ctx, f"**Вы не зарегистрированы**")
            return

        if not await check_id(ctx, player_id):
            return
            
        accounts = await get_binded_accounts(ctx.author.id)
        if player_id not in accounts:
            await send_error(ctx, f"**Этот аккаунт не привязан к вам**")
            return

        player = find_id(player_id)
        client_id = await get_client_id(ctx.author.id)
        old_account, new_account = await change_account(player_id, client_id['client_id'])
        await send_success(ctx, f"**Вы переключились на аккаунт\n`{old_account['nickname']} [{old_account['id']}] -> {new_account['nickname']} [{new_account['id']}]`**")
        
        if Config.BOT_ACCOUNT_LOG_CHANNEL:
            log_channel = self.bot.get_channel(Config.BOT_ACCOUNT_LOG_CHANNEL)
            embed = Embed(
                title=f"👥{Config.BOT_SEPARATOR}Смена аккаунта",
                description=f"**`{old_account['nickname']} [{old_account['id']}] -> {new_account['nickname']} [{new_account['id']}]`**",
                color=Colour.dark_green(),
                timestamp=datetime.now(),
            )
            embed.add_field(name='Автор', value=ctx.author.mention)
            embed.add_field(name='Канал', value=ctx.channel.mention)
            await log_channel.send(embed=embed)


def register_accounts_cogs(bot: Bot) -> None:
    bot.add_cog(__MainAccountsCog(bot))
