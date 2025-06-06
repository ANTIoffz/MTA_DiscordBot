from .ssh import SSH
from bot.misc import Config

console = SSH(
    host=Config.SSH_IP,
    port=Config.SSH_PORT,
    user=Config.SSH_USER,
    password=Config.SSH_PASSWORD
)
console.connect()
