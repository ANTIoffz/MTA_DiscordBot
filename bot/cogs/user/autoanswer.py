from disnake.ext.commands import Cog, Bot, slash_command, Param
from disnake import Colour, Embed, Attachment
from datetime import datetime
from bot.database import database_bot, database_mta
from bot.misc import Config, check_id, change_player_field, send_success, send_error, send_warning
from bot.server_monitoring import server
from time import time
import urllib.request
from fuzzywuzzy import fuzz

class __MainAutoAnswerCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot


    @Cog.listener()
    async def on_message(
            self,
            message
    ) -> None:
        if message.author != self.bot.user:
            for text, answer in Config.AUTO_ANSWERS.items():
                if fuzz.ratio(text.lower(), message.content) >= Config.AUTO_ANSWERS_ERROR_RATE:
                    await message.reply(answer)
                    return


def register_auto_answer_cogs(bot: Bot) -> None:
    bot.add_cog(__MainAutoAnswerCog(bot))
