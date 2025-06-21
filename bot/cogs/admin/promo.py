from disnake.ext.commands import Cog, Bot, slash_command, Param, guild_only
from disnake import Colour, Embed, ui, ButtonStyle, ModalInteraction, TextInputStyle, Interaction
from datetime import datetime
from bot.database import database_bot, database_mta
from bot.misc import Config, check_id, change_player_field, check_bot_db, check_server_db, send_error, send_success, \
    send_warning, create_promo_db, find_promo
from time import time
import re
from pprint import pprint
import json


class RewardsModal(ui.Modal):
    def __init__(
            self, 
            ckey: str, 
            type: str = 'all',
            for_new_users: bool = False,
            start_date: int = int(time()),
            end_date: int = int(time()) + 86400,
            max_uses: int = 4294967292,
            timeout: int = 600,
            on_create_callback: callable = None
        ):
        self.ckey = ckey
        self.type = type
        self.for_new_users = for_new_users
        self.start_date = start_date
        self.end_date = end_date
        self.max_uses = max_uses
        self.timeout = timeout
        self.on_create_callback = on_create_callback
        
        components = [
            ui.TextInput(
                label=f'Валюта',
                custom_id="soft",
                style=TextInputStyle.short,
                required=False
            ),
            ui.TextInput(
                label=f'Донатная валюта',
                custom_id="hard",
                style=TextInputStyle.short,
                required=False
            ),
            ui.TextInput(
                label=f'Рем. Комплекты',
                custom_id="repairbox",
                style=TextInputStyle.short,
                required=False
            ),
            ui.TextInput(
                label=f'Премиум',
                custom_id="premium",
                style=TextInputStyle.short,
                required=False
            ),
            ui.TextInput(
                label=f'Кейсы',
                custom_id="case",
                style=TextInputStyle.paragraph,
                required=False,
                placeholder='silver 5\nПример выдачи 5 серебряных кейсов\nКаждый элемент в новой строке'
            )
        ]
        super().__init__(
            title="Награды",
            timeout=self.timeout,
            components=components,
        )

    async def callback(self, ctx: ModalInteraction):
        rewards = []
        reward_items = []
        
        if ctx.text_values.get("soft"):
            reward_items.append({
                "id": "soft",
                "params": {
                    "count": int(ctx.text_values["soft"])
                }
            })
            
        if ctx.text_values.get("hard"):
            reward_items.append({
                "id": "hard", 
                "params": {
                    "count": int(ctx.text_values["hard"])
                }
            })
            
        if ctx.text_values.get("repairbox"):
            reward_items.append({
                "id": "repairbox",
                "params": {
                    "count": int(ctx.text_values["repairbox"])
                }
            })
            
        if ctx.text_values.get("premium"):
            reward_items.append({
                "id": "premium",
                "params": {
                    "days": int(ctx.text_values["premium"])
                }
            })
            
        if ctx.text_values.get("case"):
            case_data_all = ctx.text_values["case"].splitlines()
            for case in case_data_all:
                case_data = case.split(" ")
                if len(case_data) != 2:
                    await send_error(ctx, "Неверный формат выдачи кейсов")
                    return
                
                reward_items.append({
                    "id": "case",
                    "params": {
                        "id": case_data[0],
                        "count": int(case_data[1])
                    }
                })
            
        if reward_items:
            rewards.append(reward_items)
        
        self.rewards_str = json.dumps(rewards, indent=4).replace('"', '\\"')
        data = {
            "ckey": f"'{self.ckey}'",
            "type": f"'{self.type}'",
            "rewards": f'"{self.rewards_str}"',
            "for_new_users": f"'{self.for_new_users}'",
            "start_date": f"'{self.start_date}'",
            "end_date": f"'{self.end_date}'",
            "client_ids ": "'[ [ ] ]'",
            "max_uses_count": f"'{self.max_uses}'",
            "max_server_uses_count": f"'{self.max_uses}'",
            "is_blocked": f"'0'",
            "is_generated": f"'1'",
        }

        await create_promo_db(data)
        await send_success(ctx, f"**Промокод `{self.ckey}` создан!**\n```json\n{rewards}```")
        if self.on_create_callback:
            await self.on_create_callback(ctx, data, rewards)


        
    async def on_error(self, error: Exception, ctx: ModalInteraction):
        if error.__class__ is ValueError:
            error_str = str(error)
            invalid_value = error_str.split("'")[1]
            
            retry_button = ui.Button(style=ButtonStyle.primary, label="Исправить", custom_id="retry_modal")
            
            view = ui.View()
            view.add_item(retry_button)
            
            await send_error(
                ctx, 
                f"**`{invalid_value}` не является числом!**",
                view=view,
                ephemeral=True
            )
            
            async def button_callback(interaction: Interaction):
                await interaction.response.send_modal(
                    modal=RewardsModal(
                        ckey=self.ckey,
                        type=self.type, 
                        for_new_users=self.for_new_users,
                        start_date=self.start_date,
                        end_date=self.end_date,
                        max_uses=self.max_uses,
                        on_create_callback=self.send_announce
                    )
                )
            
            retry_button.callback = button_callback
        else:
            raise error
        
            
class __MainPromoCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @slash_command(
        name="create_promo",
        description="Создать промокод",
    )
    @check_server_db()
    @guild_only()
    async def create_promo(
            self, ctx,
            ckey: str = Param(description="Название промокода"),
            start_date: str = Param(default=datetime.now().strftime('%d.%m.%Y'), description="Дата начала действия промокода (день.месяц.год)"),
            end_date: str = Param(description="Дата конца действия промокода (день.месяц.год)"),
            type: str = Param(default="all", description="Тип промокода (для всех, для админов)", choices=["all", "admin"]),
            for_new_users: bool = Param(default=0, description="Для новых пользователей", choices=[1, 0]),
            max_uses: int = Param(default=4294967292, description="Количество использований"),
            announce: bool = Param(description="Оповестить пользователей", choices=[1, 0])
    ) -> None:
        if find_promo(ckey):
            await send_error(ctx, f"**Промокод `{ckey}` уже существует!**", ephemeral=True)
            return

        try:
            start_date_unix = round((datetime.strptime(start_date, '%d.%m.%Y') - datetime(1970, 1, 1)).total_seconds())
        except ValueError:
            await send_error(ctx, f"**Используйте формат `День.Месяц.Год`**", ephemeral=True)
            return
        
        try:
            end_date_unix = round((datetime.strptime(end_date, '%d.%m.%Y') - datetime(1970, 1, 1)).total_seconds())
        except ValueError:
            await send_error(ctx, f"**Используйте формат `День.Месяц.Год`**", ephemeral=True)
            return

        await ctx.response.send_modal(
            modal=RewardsModal(
                ckey=ckey,
                type=type,
                for_new_users=int(for_new_users),
                start_date=start_date_unix,
                end_date=end_date_unix,
                max_uses=max_uses,
                on_create_callback=self.send_announce if announce else None
            )
        )


    async def send_announce(self, ctx, data, rewards):
        rewards_data = {}
        ckey = str(data['ckey']).replace("'", "")

        for num, reward in enumerate(rewards[0]):
            if reward['id'] == 'case':
                rewards_data[f"{reward['id']}{num}"] = reward['params']
                continue
            rewards_data[reward['id']] = reward['params']

        rewards_str = "**"
        rewards_str += f"# Промокод `{ckey}`\n"
        rewards_str += f"Содержимое -\n"
        rewards_str += f"* Деньги `{rewards_data.get('soft')['count']} $`\n" if rewards_data.get('soft') else ""
        rewards_str += f"* Донатная валюта: `{rewards_data.get('hard')['count']} $`\n" if rewards_data.get('hard') else ""
        rewards_str += f"* Рем. комплекты: `x{rewards_data.get('repairbox')['count']}`\n" if rewards_data.get('repairbox') else ""
        rewards_str += f"* Дней премиума `{rewards_data.get('premium')['days']}`\n" if rewards_data.get('premium') else ""
        for key, reward in rewards_data.items():
            if key.startswith('case'):
                rewards_str += f"* Кейс `{reward['id']}` x{reward['count']}\n"
        rewards_str += "**"

        embed = Embed(
            description=rewards_str,
            color=Colour.orange(),
            timestamp=datetime.now(),            
        )
        if Config.BOT_NEW_PROMO_IMAGE:
            embed.set_image(url=Config.BOT_NEW_PROMO_IMAGE)

        announce_channel = self.bot.get_channel(Config.BOT_NEW_PROMO_CHANNEL)
        await announce_channel.send(embed=embed)
    
def register_promo_cogs(bot: Bot) -> None:
    bot.add_cog(__MainPromoCog(bot))
