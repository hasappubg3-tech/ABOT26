import logging
import os
import sqlite3
import json
import httpx
import zipfile
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, LabeledPrice
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, PollAnswerHandler, PreCheckoutQueryHandler, filters

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
STORAGE_CHANNEL_ID = "-1003800078762"
DB = "data.db"
MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)

GEMINI_MODEL = "gemini-2.5-flash"

def _load_gemini_keys():
    keys = []
    for k in [
        os.environ.get("GEMINI_API_KEY", ""),
        *[os.environ.get(f"GEMINI_API_KEY_{i}", "") for i in range(1, 11)],
    ]:
        if k and k not in keys:
            keys.append(k)
    return keys

GEMINI_KEYS = _load_gemini_keys()

BTN_BACK     = "رجوع"
BTN_HOME     = "القائمة الرئيسية"
BTN_ADD      = "➕ إضافة"
BTN_MANAGE   = "⚙️ إدارة"
BTN_ADMINS   = "👥 مشرفون"
BTN_CANCEL   = "❌ إلغاء"
BTN_SETTINGS = "⚙️ الاعدادات"

BTN_SWAP = "🔀 تغيير"

ADMIN_BTNS   = {BTN_ADMINS}
BTN_PLUS = "➕"
SPECIAL_BTNS = {BTN_BACK, BTN_HOME, BTN_ADD, BTN_MANAGE, BTN_ADMINS, BTN_CANCEL, BTN_SWAP, BTN_PLUS,
                BTN_SETTINGS, "📂 قائمة", "📄 محتوى"}

_SUP_DIGITS = "⁰¹²³⁴⁵⁶⁷⁸⁹"
_SUP_MAP    = {c: str(i) for i, c in enumerate(_SUP_DIGITS)}

def _plus_label(bid: int) -> str:
    """يُنشئ نص زر ➕ + رقم الزر بأرقام فوقية مثل ➕⁵."""
    return BTN_PLUS + ''.join(_SUP_DIGITS[int(d)] for d in str(bid))

def _parse_plus(text: str):
    """يُعيد bid إذا كان النص زر ➕ مع أرقام فوقية، وإلا None."""
    if not text.startswith(BTN_PLUS):
        return None
    rest = text[len(BTN_PLUS):]
    if not rest:
        return None
    digits = ''.join(_SUP_MAP.get(c, '') for c in rest)
    if not digits:
        return None
    try:
        return int(digits)
    except Exception:
        return None

__all__ = [name for name in globals() if not name.startswith("__")]
