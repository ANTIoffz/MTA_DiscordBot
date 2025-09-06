from abc import ABC
from typing import Final


class Config(ABC):
    BOT_MAIN_SERVERS_IDS = [] # Доверенные сервера - Впишите ID серверов, на которых будет работать бот 
    BOT_PREFIX: Final = '/' # Префикс бота
    BOT_SEPARATOR: Final = '┆' # Отделитель смайлика от текста в заголовках
    BOT_GMT: Final = +3 # GMT
    BOT_PLAYING_IN = '' # Играет в ... статус
    
    WEBSITE_URL: Final = "" # Адрес сайта (если есть)
    FORUM_URL: Final = "" # Адрес формуа (если есть)

    BOT_LOG_CHANNEL: Final = 0 # Канал логов 
    BOT_ACCOUNT_LOG_CHANNEL: Final = 0 # Канал логов смены аккаунтов 
    BOT_NEW_ACCOUNTS_LOG_CHANNEL: Final = 0 # Канал логов новых аккаунтов 
    BOT_ADMIN_DISCIPLINE_LOG_CHANNEL: Final = 0 # Канал логов предов выговоров 
    BOT_STATUS_CHANNEL: Final = 0 # Канал для динамического status 
    BOT_PLAYERS_CHANNEL: Final = 0 # Канал с кол-вом игроков 
    BOT_FEEDBACK_CHANNEL: Final = 0 # Канал для отсылки Feedback-оф 
    BOT_ADMIN_DISCIPLINE_TABLE_CHANNEL: Final = 0 # Канал динамической таблицы предов выговоров 
    BOT_TEA_LOG_CHANNEL: Final = 0 # Канал логов чая 
    BOT_NEW_PROMO_CHANNEL: Final = 0 # Канал логов новых промокодов
    BOT_NEW_PROMO_IMAGE: Final = '' # Изображение для промокода
    
    BOT_LOG_EXCEPTIONS: Final = [ # Игнорируемые команды в логах
        'status',
        'bt_status',
        'info',
        'online',
        'players',
        'accounts',
        'tea_give',
        'tea_leaders',
        'tea_balance',
        'tea_ban_list',
        'random'
    ] 

    DATABASE_HOST: Final = "localhost" # БД хост
    DATABASE_PORT: Final = 3306 # БД порт
    DATABASE_USER: Final = "bot" # БД юзернейм 
    DATABASE_PASSWORD: Final = "" # БД пароль 
    DATABASE_NAME_MTA: Final = "nextrp" # Название таблицы с мта
    DATABASE_NAME_BOT: Final = "bot" # Название таблицы бота
    DATABASE_AUTORECONNECT: Final = True # БД реконнект по времени

    SERVER_HOST = '' # Айпи сервера 
    SERVER_PORT = 22003 # Порт сервера
    
    SSH_IP: Final = '' # SSH айпи 
    SSH_PORT: Final = 22 # SSH порт 
    SSH_USER: Final = 'root' # SSH юзернейм
    SSH_PASSWORD: Final = r"" # SSH пароль 
    
    MAX_ACCOUNTS: Final = 2 # Макс аккаунтов
    NEW_ACCOUNT_SETTINGS: Final = { # Дефолт настройки для новых аккаунтов
        'skin': 163
    } 
    NICKNAME_MIN_LEN: Final = 3 # Минимальная длина имени
    LOGIN_MIN_LEN: Final = 3 # Минимальная длина логина
    PASSWORD_MIN_LEN: Final = 3 # Минимальная длина пароля
    IGNORE_MAX_ACCOUNTS_ROLES: Final = [] # Роли с игнором ограничения акков
    ADMIN_MAX_WARNINGS: Final = 3 # Максимум предов до выговора
    ADMIN_MAX_REPRIMANDS: Final = 2 # Максимум выговоров до снятия
    ADMIN_WARNING_DAYS: Final = 4 # Дни отката преда
    ADMIN_REPRIMAND_DAYS: Final = 7 # Дни отката выговора

    TEA_DELAY_SECONDS: Final = 3600 #Минуты отката чая
    TEA_GIVE_BAN_ROLES = [] #Роли, которые не могут заваривать чай (админы)
    TEA_RECIVE_BAN_ROLES = [] #Роли, которые не могут принять чай (боты)
    
    AUTO_ANSWERS = {
        "amogus": """ඞ""",
        "🍕": """😋""",
        "pepperoni": """🍕""",
    } # Авто ответ на частые вопросы в чате
    AUTO_ANSWERS_ERROR_RATE = 80 # Погрешность обнаружения
    
    TEXT_IF_NOT_IN_BOT_GUILD = "https://resizer.mail.ru/p/e58872a5-a839-536d-a932-3dcd4702fbcf/AQAKjsrxw7T5GxIl8m7kxG6oMgWdVEkXIw-rQ_ZVIaG8O8wklNS3WC8S10lznJDmv_Sj62VNHPXb_CK9FO76yku85Vk.jpg" # Текст при попытке выполнения команды в лс бота или на другом сервере

    MTA_SERVER_SCREEN_NAME = 'ser' # название экрана в мультиплексор Screen с запущенным MTA сервером 
    
