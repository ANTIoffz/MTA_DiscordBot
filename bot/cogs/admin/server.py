from disnake.ext.commands import Cog, Bot, slash_command, Param, guild_only
from disnake import Colour, Embed, ui, ModalInteraction, TextInputStyle
from datetime import datetime
from bot.database import database_bot, database_mta
from bot.misc import send_areyousure_message, AreYouSureModal, Config, check_id, change_player_field, check_bot_db, check_server_db, send_error, send_warning, send_success
from bot.server_monitoring import server
from time import time
import os
import re


class __MainServerCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
    
    @Cog.listener()
    async def on_button_click(self, ctx):
        if ctx.component.custom_id == "shutdown_yes":
            if self.requester_user == ctx.author:
                await ctx.message.delete()
                await ctx.response.send_modal(
                    modal=AreYouSureModal(
                        command=f"screen -x {self.screen} -X stuff '^C'"
                    )
                )

        elif ctx.component.custom_id == "shutdown_no":
            if self.requester_user == ctx.author:
                await ctx.message.delete()
                
        elif ctx.component.custom_id == "startup_yes":
            if self.requester_user == ctx.author:
                await ctx.message.delete()
                await ctx.response.send_modal(
                    modal=AreYouSureModal( 
                        command=f"screen -x {self.screen} -X stuff '/mta/mta-server64\n'"
                    )
                )

        elif ctx.component.custom_id == "startup_no":
            if self.requester_user == ctx.author:
                await ctx.message.delete()
       
       
       
    @slash_command(
        name="sv_shutdown",
        description="Выключить сервер ААААА",
    )
    @guild_only()
    async def sv_shutdown(
            self, ctx,
            screen: str = Param(default=Config.MTA_SERVER_SCREEN_NAME, description='Название экрана')
    ) -> None:
        self.requester_user = ctx.author
        self.screen = screen
        server_status = server.reconnect()
        if not server_status:
            await send_areyousure_message(ctx,
                text='**Думаю сервер уже выключен, все равно выполнить?**',
                yes_id='shutdown_yes',
                no_id='shutdown_no'
            )
            return
            
        await ctx.response.send_modal(
            modal=AreYouSureModal(
                command=f"screen -x {self.screen} -X stuff '^C'"
            )
        )
        
    
    
    @slash_command(
        name="sv_startup",
        description="Включить сервер МММММ",
    )
    @guild_only()
    async def sv_startup(
            self, ctx,
            screen: str = Param(default=Config.MTA_SERVER_SCREEN_NAME, description='Название экрана')
    ) -> None:
        self.requester_user = ctx.author
        self.screen = screen
        server_status = server.reconnect()
        if server_status:
            await send_areyousure_message(ctx,
                text='**Думаю сервер уже включен, все равно выполнить?**',
                yes_id='startup_yes',
                no_id='startup_no'
            )
            return
            
        await ctx.response.send_modal(
            modal=AreYouSureModal(
                command=f"screen -d -RR {self.screen} -X stuff '/mta/mta-server64\n'"
            )
        )
    
    
    @slash_command(
        name="players",
        description="Игроки на сервере в данный момент",
    )
    @guild_only()
    async def players(
            self, ctx
    ) -> None:
        server_status = server.reconnect()
        if server_status:
            res = server.server.response.decode('utf-8')
            res = re.sub(r'[^a-zA-Z_?]', '', res, flags=re.UNICODE)
            res = res.split('?')[1:]
            players_list = f"\n".join(f"`{nickname.strip()}`" for nickname in res)
            if any((True if not "_" in nickname else False for nickname in res)):
                players_list += "\n-# имя может быть случайное пока игрок подключается"

            embed = Embed(
                title=f"👥 [{len(res)}]{Config.BOT_SEPARATOR}Игроки на сервере",
                description=players_list if players_list else "**Нету   ¯\_(ツ)_/¯**",
                color=Colour.dark_green(),
                timestamp=datetime.now(),
            )
        else:
            embed = Embed(
                title=f"❌{Config.BOT_SEPARATOR}Ошибка",
                description=f"**Сервер не онлайн**",
                color=Colour.red(),
                timestamp=datetime.now(),
            )
        await ctx.send(embed=embed)

def register_server_cogs(bot: Bot) -> None:
    bot.add_cog(__MainServerCog(bot))
