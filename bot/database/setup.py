from .main import Database
from bot.misc import Config

# REGISTER MTA DATABASE
database_mta = Database(
    host=Config.DATABASE_HOST,
    port=Config.DATABASE_PORT,
    user=Config.DATABASE_USER,
    password=Config.DATABASE_PASSWORD,
    database=Config.DATABASE_NAME_MTA,
    autoreconnect=Config.DATABASE_AUTORECONNECT,
)

# REGISTER BOT DATABASE
database_bot = Database(
    host=Config.DATABASE_HOST,
    port=Config.DATABASE_PORT,
    user=Config.DATABASE_USER,
    password=Config.DATABASE_PASSWORD,
    database=Config.DATABASE_NAME_BOT,
    autoreconnect=Config.DATABASE_AUTORECONNECT
)

# STARTING
try:
    database_bot.connect()
    database_bot.cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS `accounts` (
            `discord_id` BIGINT NOT NULL PRIMARY KEY,
            `client_id` TEXT NOT NULL,
            `ip` TEXT NOT NULL,
            `game_ids` LONGTEXT NOT NULL DEFAULT '[]'
        );
    """)
    database_bot.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS `elections` (
            `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
            `data` LONGTEXT NOT NULL,
            `active` INT NOT NULL,
            `already_voted` LONGTEXT NOT NULL,
            `name` TEXT NOT NULL,
            `channel_id` BIGINT NOT NULL
        );
    """)
    database_bot.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS `admins` (
            `discord_id` BIGINT NOT NULL PRIMARY KEY,
            `reprimands` INT NOT NULL DEFAULT 0,
            `warnings` INT NOT NULL DEFAULT 0,
            `last_reprimand_date` BIGINT NOT NULL DEFAULT 0,
            `last_warning_date` BIGINT NOT NULL DEFAULT 0
        );
    """)
    database_bot.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS `tea` (
            `discord_id` BIGINT NOT NULL PRIMARY KEY,
            `tea_count` INT NOT NULL DEFAULT 0,
            `last_tea_date` BIGINT NOT NULL DEFAULT 0,
            `banned` TINYINT NOT NULL DEFAULT 0
        );
    """)
except Exception as exc:
    print(f"ERROR WHILE CONNECTING BOT DATABASE!\n\t{exc}")


try:
    database_mta.connect()
except Exception as exc:
    print(f"ERROR WHILE CONNECTING MTA DATABASE!\n\t{exc}")

