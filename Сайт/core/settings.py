from pathlib import Path
from dotenv import load_dotenv
import os

# Загружаем переменные окружения
load_dotenv()

# ==========================================================
# Пути к проекту и базам данных
# ==========================================================
# Корень проекта "Сайт"
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Папка с общей базой (лежит рядом с "Сайт")
COMMON_DB_DIR = PROJECT_ROOT.parent / "Общая БД"

# Локальная база хранится в корне проекта "Сайт"
LOCAL_DB_PATH = (PROJECT_ROOT.parent / "Бот в тг" / "local_orders.db").resolve()


# Основная база Django
DJANGO_DB_PATH = PROJECT_ROOT / 'db.sqlite3'

# Имя базы для stock_db из .env (DB_NAME=orders.db или local_orders.db)
DB_NAME = os.getenv("DB_NAME", "local_orders.db")

# Выбираем путь к stock_db
if DB_NAME == "orders.db":
    STOCK_DB_PATH = COMMON_DB_DIR / DB_NAME  # общая база
else:
    STOCK_DB_PATH = LOCAL_DB_PATH  # локальная база

# Проверка на существование файлов для отладки
print("Путь к основной базе Django:", DJANGO_DB_PATH)
print("Существует:", DJANGO_DB_PATH.exists())
print("Путь к stock_db:", STOCK_DB_PATH)
print("Существует:", STOCK_DB_PATH.exists())

# ==========================================================
# Основные настройки Django
# ==========================================================
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '172.20.10.3', "1d5e964c65fa.ngrok-free.app"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'store',
    'accounts.apps.AccountsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            PROJECT_ROOT / 'store' / 'templates',
            PROJECT_ROOT / 'accounts' / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ==========================================================
# Database
# ==========================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DJANGO_DB_PATH,
    },
    'stock_db': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': STOCK_DB_PATH,
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# ==========================================================
# Password validation
# ==========================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# ==========================================================
# Internationalization
# ==========================================================
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ==========================================================
# Static and media files
# ==========================================================
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    PROJECT_ROOT / 'store' / 'static',
    PROJECT_ROOT / 'accounts' / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = PROJECT_ROOT / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================================
# Пользовательская модель
# ==========================================================
AUTH_USER_MODEL = 'accounts.CustomUser'
