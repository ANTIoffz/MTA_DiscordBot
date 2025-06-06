from disnake.ext.commands import Bot

from bot.cogs.admin import register_admin_cogs, register_find_cogs, register_moderation_cogs, register_SSH_cogs, \
    register_server_cogs, register_database_cogs, register_bot_cogs, register_accounts_cogs, register_admin_discipline_cogs, register_elections_cogs, \
    register_promo_cogs
from bot.cogs.other import register_other_cogs
from bot.cogs.user import register_user_cogs, register_auto_answer_cogs, register_tea_cogs
from bot.cogs.tasks import register_players_task_cogs, register_status_task_cogs, register_ping_databases_cogs, \
    register_admin_discipline_table_cogs, register_register_log_cogs


def register_all_cogs(bot: Bot) -> None:
    cogs = (
        register_user_cogs,
        register_admin_cogs,
        register_other_cogs,
        register_find_cogs,
        register_moderation_cogs,
        register_SSH_cogs,
        register_database_cogs,
        register_bot_cogs,
        register_accounts_cogs,
        register_players_task_cogs,
        register_status_task_cogs,
        register_ping_databases_cogs,
        register_admin_discipline_cogs,
        register_admin_discipline_table_cogs,
        register_register_log_cogs,
        register_auto_answer_cogs,
        register_elections_cogs,
        register_server_cogs,
        register_tea_cogs,
        register_promo_cogs
    )
    for cog in cogs:
        cog(bot)
