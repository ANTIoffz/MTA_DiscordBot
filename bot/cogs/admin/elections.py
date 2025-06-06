from disnake.ext.commands import Cog, Bot, slash_command, Param, guild_only
from disnake import Colour, Embed
from datetime import datetime, timedelta
from bot.misc import Config, check_id, check_name, check_bot_db, check_server_db, send_success, send_error
from disnake import Colour, Embed, ui, ApplicationCommandInteraction, ButtonStyle, MessageInteraction, User, NotFound
from time import time
from disnake import TextInputStyle, ui
from disnake.abc import GuildChannel
from bot.database import database_bot, database_mta
import json


class __MainElectionsCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    async def check_elections_id(self, ctx, election_id):
        database_bot.cursor.execute("SELECT * FROM elections WHERE id = %s", (election_id,))
        if database_bot.cursor.fetchone():
            return True
        return False


    @Cog.listener()
    async def on_button_click(self, ctx):
        if not ctx.component.custom_id.split('.')[0] == 'elections':
            return
            
        election_id = ctx.component.custom_id.split('.')[1]
        candidate = ctx.component.custom_id.split('.')[2]
        database_bot.cursor.execute("SELECT active FROM elections WHERE id = %s", (election_id,))
        if database_bot.cursor.fetchone()['active'] == 0:
            await ctx.send('**Выборы окончены**', ephemeral=True)
            return

        database_bot.cursor.execute("SELECT already_voted FROM elections WHERE id = %s", (election_id,))
        already_voted_list = json.loads(database_bot.cursor.fetchone()['already_voted'])
        if ctx.author.id in already_voted_list:
            await ctx.send('**Вы уже голосовали**', ephemeral=True)
            return

        already_voted_list.append(ctx.author.id)
        database_bot.cursor.execute("UPDATE `elections` SET already_voted = %s WHERE id = %s",
                                    (json.dumps(already_voted_list, ensure_ascii=False), election_id))

        database_bot.cursor.execute("SELECT data FROM elections WHERE id = %s", (election_id,))
        data = json.loads(database_bot.cursor.fetchone()['data'])
        data[list(data.keys())[int(candidate)]] += 1
        database_bot.cursor.execute("UPDATE `elections` SET data = %s WHERE id = %s",
                                    (json.dumps(data, ensure_ascii=False), election_id))
        await ctx.send('**Ваш голос учтён!**', ephemeral=True)


    @slash_command(
        name="elections_start",
        description="Начать выборы",
    )
    @check_bot_db()
    @guild_only()
    async def elections_start(
            self, ctx,
            name: str = Param(description='Название'),
            candidates: str = Param(description='Кандидаты через запятую'),
            channel: GuildChannel = Param(description='Канал для выборов')
    ):
        candidates = list(map(lambda text: text.strip(), candidates.split(',')))
        data = {}
        for candidate in candidates:
            data[candidate] = 0
        database_bot.cursor.execute(
            "INSERT INTO `elections` (name, channel_id, data, active, already_voted) VALUES (%s, %s, %s, %s, %s)",
            (name, channel.id, json.dumps(data, ensure_ascii=False), 1, '[]'))
        database_bot.cursor.execute("SELECT LAST_INSERT_ID() FROM `elections`")
        election_id = int(database_bot.cursor.fetchone()['LAST_INSERT_ID()'])

        components = [ui.Button(label=candidate, style=ButtonStyle.success, custom_id=f"elections.{election_id}.{num}") for
                      num, candidate in enumerate(candidates)]
        embed = Embed(
            title=f"📝{Config.BOT_SEPARATOR}Выборы {name}",
            description="",
            color=Colour.dark_gray(),
            timestamp=datetime.now(),
        )
        await channel.send(embed=embed, components=components)
        await send_success(ctx, f"**Выборы запущены!\n`ID : {election_id}`**")


    @slash_command(
        name="elections_stop",
        description="Остановить выборы",
    )
    @check_bot_db()
    @guild_only()
    async def elections_stop(
            self, ctx,
            election_id: int = Param(description='Айди выборов'),
    ):
        if not await self.check_elections_id(ctx, election_id):
            await send_error(ctx, f"**Айди `{election_id}` не найден**")
            return

        database_bot.cursor.execute("SELECT * FROM `elections` WHERE id = %s", (election_id,))
        election = database_bot.cursor.fetchone()
        data = json.loads(election['data'])
        results = "\n".join(f"* `{candidate[0]} - {candidate[1]}`" for candidate in data.items())
        embed = Embed(
            title=f"🗳{Config.BOT_SEPARATOR}Выборы {election['name']} окончены!",
            description=f"**Результаты:\n{results}**",
            color=Colour.dark_gray(),
            timestamp=datetime.now(),
        )
        channel = self.bot.get_channel(election['channel_id'])
        await channel.send(embed=embed)

        database_bot.cursor.execute("UPDATE `elections` SET active = 0 WHERE id = %s", (election_id,))
        await send_success(ctx, f'**Выборы `{election_id}` остановлены**')


    @slash_command(
        name="elections_list",
        description="Список активных выборов",
    )
    @check_bot_db()
    @guild_only()
    async def elections_list(self, ctx):
        database_bot.cursor.execute(f"SELECT * FROM elections WHERE active = 1")
        elections = database_bot.cursor.fetchall()
        description = "\n".join(
            [f"* `[{election['id']}]` - {election['name']}" for election in elections]
        )
        embed = Embed(
            title=f"📝{Config.BOT_SEPARATOR}Список активных выборов",
            description=f"**{description}**" if description else "**Нету**",
            color=Colour.dark_gray(),
            timestamp=datetime.now(),
        )
        await ctx.send(embed=embed)


    @slash_command(
        name="elections_info",
        description="Информация о выборах",
    )
    @check_bot_db()
    @guild_only()
    async def elections_info(
            self, ctx,
            election_id: int = Param(description='Айди выборов')
    ):
        if not await self.check_elections_id(ctx, election_id):
            await send_error(ctx, f"**Айди `{election_id}` не найден**")
            return
        database_bot.cursor.execute("SELECT * FROM elections WHERE id = %s", (election_id,))
        election = database_bot.cursor.fetchone()
        data = json.loads(election['data'])
        info = "\n".join(f"* `{candidate[0]} - {candidate[1]}`" for candidate in data.items())
        embed = Embed(
            title=f"📝{Config.BOT_SEPARATOR}Информация",
            description=f"**`[{election_id}]` - {election['name']}\n{info}**",
            color=Colour.dark_gray(),
            timestamp=datetime.now(),
        )
        await ctx.send(embed=embed)

def register_elections_cogs(bot: Bot) -> None:
    bot.add_cog(__MainElectionsCog(bot))
