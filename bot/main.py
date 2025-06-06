from disnake import Intents, Game
from disnake.ext.commands import Bot

from bot.misc import Env, Config
from bot.cogs import register_all_cogs


def start_bot():
    intents = Intents.all()
    bot = Bot(Config.BOT_PREFIX, intents=intents, owner_id=562921512794062858, help_command=None, activity=Game(name=Config.BOT_PLAYING_IN))
    register_all_cogs(bot)
    bot.run(Env.TOKEN)
