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
STORAGE_CHANNEL_ID = os.environ.get("STORAGE_CHANNEL_ID", "-1003800078762").strip()
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
BTN_EXAM_STATS = "📊 إحصائيات الامتحانات"

ADMIN_BTNS   = {BTN_ADMINS}
BTN_PLUS = "➕"
SPECIAL_BTNS = {BTN_BACK, BTN_HOME, BTN_ADD, BTN_MANAGE, BTN_ADMINS, BTN_CANCEL, BTN_SWAP, BTN_PLUS,
                BTN_SETTINGS, "📂 قائمة", "📄 محتوى", BTN_EXAM_STATS}

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

# ── ترميز معرّف الزر بأحرف غير مرئية لتمييز الأزرار المتشابهة الاسم ──
# نلصق بصمة غير مرئية بنهاية نص الزر تحوي معرّفه الفريد، فيظل النص الظاهر
# مطابقاً للمستخدم بينما يتمكن البوت من التعرف على الزر المضغوط بدقة حتى
# لو وُجد أكثر من زر بنفس الاسم في أماكن مختلفة، ولا يعتمد على آخر موقع
# للمستخدم (pid) الذي قد يكون خاطئاً بسبب لوحة قديمة أو إعادة تشغيل.
_BID_ZERO = "\u200B"   # ZWSP — البت 0
_BID_ONE  = "\u200C"   # ZWNJ — البت 1
_BID_END  = "\u2060"   # WJ   — نهاية البصمة
_BID_INVISIBLES = (_BID_ZERO, _BID_ONE, _BID_END)

def _encode_bid(bid) -> str:
    """يُولّد بصمة غير مرئية تُلصق بنص الزر لتُعرّف معرّفه الفريد."""
    try:
        n = int(bid)
    except (TypeError, ValueError):
        return ""
    if n < 0:
        return ""
    bits = format(n, "b")
    return "".join(_BID_ONE if c == "1" else _BID_ZERO for c in bits) + _BID_END

def _decode_bid(text: str):
    """يفك البصمة من نص الزر ويعيد (نص_بدون_البصمة, bid_or_None)."""
    if not text:
        return text, None
    bid = None
    if _BID_END in text:
        end_idx = text.rfind(_BID_END)
        bits = []
        i = end_idx - 1
        while i >= 0 and text[i] in (_BID_ZERO, _BID_ONE):
            bits.append("1" if text[i] == _BID_ONE else "0")
            i -= 1
        bits.reverse()
        if bits:
            try:
                bid = int("".join(bits), 2)
            except Exception:
                bid = None
    cleaned = "".join(c for c in text if c not in _BID_INVISIBLES)
    return cleaned, bid

def _strip_bid_markers(text: str) -> str:
    cleaned, _ = _decode_bid(text or "")
    return cleaned

__all__ = [name for name in globals() if not name.startswith("__")]
