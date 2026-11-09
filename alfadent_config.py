# AlfaDent private runtime configuration.
# This file belongs ONLY in the private Analdin/alfadent-miniapp repository.
# The public mini-app_main and private alfa-dent_max repositories import it at runtime.
# Never copy this file into a public Git repository.

TELEGRAM_TOKEN = "8467382002:AAH11wp1u1jLzBGUbErcjJXGzC-TomNtkc4"
BITRIX24_WEBHOOK_RAW = "https://alfadent23.bitrix24.ru/rest/11599/tleyme67jjk7x2gf/"
BITRIX24_WEBHOOK = BITRIX24_WEBHOOK_RAW.strip().rstrip("/") + "/" if BITRIX24_WEBHOOK_RAW else ""
TELEGRAM_PROXY = "socks5://WPQT0J2C:WJXIKKC2@130.180.226.183:59637"
WEBAPP_URL = "https://alfadent-miniapp.onrender.com/miniapp.html"

MAX_BOT_TOKEN = "f9LHodD0cOKi_QdXn3Y_X9xWn9U-KQpNwlQfWqJ47fZL0Hr71E9I9bOt7-R_Lfq0J_0y_AHKpVw-QMkhasZx"
MAX_API_BASE = "https://platform-api2.max.ru"
MAX_MINIAPP_LINK = "https://alfadent-miniapp.onrender.com/miniapp.html"
PROMOTIONS_URL = "https://alfadent-miniapp.onrender.com/assets/promotions.json"
MAX_WEBHOOK_SECRET = ""
MAX_REQUIRE_WEBHOOK_SECRET = False

# Server-to-server authentication secret shared by all three processes.
INTERNAL_AUTH_SECRET = "b8122828c72e899370c14ac58dbba982540f15dd0823b582982c0f84264a3005"
AUTH_API_URL = "http://127.0.0.1:8001"
AUTH_DB_PATH = "/var/lib/alfadent/auth.sqlite3"
TELEGRAM_DATA_DIR = "/var/lib/alfadent/telegram"
MAX_DATA_DIR = "/var/lib/alfadent/max"
BITRIX_ASSIGNED_BY_ID = 33
INITDATA_MAX_AGE_SECONDS = 3600
LOG_LEVEL = "INFO"
