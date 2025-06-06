from disnake.ext.commands import Cog, Bot, slash_command, Param, guild_only
from disnake import Colour, Embed, Attachment, User
from datetime import datetime
from bot.database import database_bot, database_mta
from bot.misc import Config, check_id, change_player_field, send_success, send_error, send_warning
from bot.server_monitoring import server
from time import time
import urllib.request
from pytz import timezone
from random import randint


class __MainUserCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(
        name="online",
        description="Показывает онлайн сервера",
    )
    async def online(
            self, ctx
    ) -> None:
        if server.reconnect():
            embed = Embed(
                title=f"👥{Config.BOT_SEPARATOR}Онлайн сервера",
                description=f"**{server.server.players} / {server.server.maxplayers}**",
                color=Colour.dark_green(),
                timestamp=datetime.now(),
            )
            await ctx.send(embed=embed)
        else:
            await send_error(ctx, f"**Сервер не онлайн**")


    @slash_command(
        name="status",
        description="Показывает статус",
    )
    async def status(
            self, ctx
    ) -> None:
        server_status = server.reconnect()
        try:
            async with ClientSession() as session:
                async with session.get(Config.WEBSITE_URL, timeout=5) as resp:
                    website_status = resp.status
        except:
            website_status = False

        try:
            async with ClientSession() as session:
                async with session.get(Config.FORUM_URL, timeout=5) as resp:
                    forum_status = resp.status
        except:
            forum_status = False
                
        try:
            has_password = int(server.server.read_row(44)[1])
        except AttributeError:
            has_password = False
        except ValueError:
            has_password = False
        
                
        embed = Embed(
            title=f"💻{Config.BOT_SEPARATOR}Статус",
            description=f"",
            color=(Colour.dark_green() if not has_password else Colour.orange()) if server_status else Colour.red(),
        )
            
        embed.add_field(
                f'🖥 Сервер',
                value=('**`🟢 Онлайн`**' if not has_password else '**`🟠 Debug`**') if server_status else '**`🔴 Оффлайн`**'
        )

        if server_status:
            embed.add_field(
                'Онлайн',
                value=f'**`{server.server.players}` / `{server.server.maxplayers}`**'
            )
                
        embed.add_field('Время МСК', value=f"**`{datetime.now(timezone('Europe/Moscow')).strftime('%H:%M:%S')}`**")
        await ctx.send(embed=embed)


    @slash_command(
        name="info",
        description="Показывает информацию",
    )
    async def info(
            self, ctx
    ) -> None:
        embed = Embed(
            title=f"📕{Config.BOT_SEPARATOR}Информация",
            description=f"""**
🛠 Разработчик бота 
`(все вопросы сюда)`
<@562921512794062858>
                        **""".strip(),
            color=Colour.dark_green(),
            timestamp=datetime.now(),
        )
        await ctx.send(embed=embed)


    @slash_command(
        name="feedback",
        description="Отправить отзыв или зарепортить баг",
    )
    @guild_only()
    async def feedback(
            self, ctx,
            text: str = Param(description='Ваше послание'),
            attachment: Attachment = Param(default=None, description='Вложение')
    ) -> None:
        channel = self.bot.get_channel(Config.BOT_FEEDBACK_CHANNEL)
        embed = Embed(
            title=f"✨{Config.BOT_SEPARATOR}Получено новое сообщение",
            description=f"```{text}```",
            color=Colour.dark_green(),
            timestamp=datetime.now(),
        )
        embed.add_field(name='Автор', value=ctx.author.mention)
        if attachment:
            embed.add_field(name='Вложение', value=attachment.url)
            embed.set_image(url=attachment.url)
        await channel.send(embed=embed)
        await send_success(ctx, f"**Ваш фидбек отправлен**")
   
   
    @slash_command(
        name="random",
        description="Случайное число",
    )
    async def random(
            self, ctx,
            from_number: int = Param(description='От'),
            to_number: int = Param(description='До'),
            #use_randomorg: bool = Param(default=False, description='Использовать random.org'),
    ) -> None:
        if from_number > to_number:
            await send_error(ctx, "**Минимальное число болше максимального**")
            return

        result_number = randint(from_number, to_number)
        embed = Embed(
            title=f"🎲{Config.BOT_SEPARATOR}Случайное число от `{from_number}` до `{to_number}`",
            description=f"**## `{result_number}`**",
            color=Colour.dark_green(),
            timestamp=datetime.now(),
        )
        await ctx.send(embed=embed)


def register_user_cogs(bot: Bot) -> None:
    bot.add_cog(__MainUserCog(bot))
