from .shared import *

# ── العبارات التحفيزية ────────────────────────────────────────────
def get_phrases():
    return [dict(r) for r in db().execute(
        "SELECT id, phrase FROM motivational_phrases ORDER BY id"
    ).fetchall()]

def add_phrase(text: str):
    c = db()
    c.execute("INSERT INTO motivational_phrases(phrase) VALUES(?)", (text,))
    c.commit(); c.close()

def del_phrase(pid: int):
    c = db()
    c.execute("DELETE FROM motivational_phrases WHERE id=?", (pid,))
    c.commit(); c.close()

def get_phrases_chance() -> int:
    """يُرجع نسبة إرسال العبارة (0-100)."""
    return int(get_setting("phrases_chance", "30"))

def get_random_phrase() -> str | None:
    """يُرجع عبارة عشوائية أو None إذا لم توجد عبارات / لم تتحقق النسبة."""
    import random
    chance = get_phrases_chance()
    if chance <= 0 or random.randint(1, 100) > chance:
        return None
    rows = db().execute("SELECT phrase FROM motivational_phrases ORDER BY RANDOM() LIMIT 1").fetchall()
    return rows[0][0] if rows else None

def toggle_btn_no_caption(bid):
    b = get_btn(bid)
    if not b: return False
    current = b.get("no_caption", 0) or 0
    new_val = 0 if current else 1
    c = db()
    c.execute("UPDATE buttons SET no_caption=? WHERE id=?", (new_val, bid))
    c.commit(); c.close()
    return bool(new_val)

def toggle_btn_no_btn_caption(bid):
    b = get_btn(bid)
    if not b: return False
    current = b.get("no_btn_caption", 0) or 0
    new_val = 0 if current else 1
    c = db()
    c.execute("UPDATE buttons SET no_btn_caption=? WHERE id=?", (new_val, bid))
    c.commit(); c.close()
    return bool(new_val)

def toggle_btn_unified_rating(bid):
    b = get_btn(bid)
    if not b: return False
    current = b.get("unified_rating", 0) or 0
    new_val = 0 if current else 1
    c = db()
    c.execute("UPDATE buttons SET unified_rating=? WHERE id=?", (new_val, bid))
    c.commit(); c.close()
    return bool(new_val)

# ── كويز: دوال قاعدة البيانات ─────────────────────────────────────
def add_quiz_question(bid, question, explanation=""):
    c = db()
    ids = c.execute("SELECT id FROM quiz_questions WHERE button_id=?", (bid,)).fetchall()
    cur = c.execute(
        "INSERT INTO quiz_questions(button_id,question,correct_option,explanation,ord) VALUES(?,?,?,?,?)",
        (bid, question, 0, explanation, len(ids)+1)
    )
    qid = cur.lastrowid; c.commit(); c.close()
    return qid

def get_quiz_questions(bid):
    return [dict(r) for r in db().execute(
        "SELECT * FROM quiz_questions WHERE button_id=? ORDER BY ord,id", (bid,)).fetchall()]

def get_quiz_question(qid):
    r = db().execute("SELECT * FROM quiz_questions WHERE id=?", (qid,)).fetchone()
    return dict(r) if r else None

def del_quiz_question(qid):
    c = db(); c.execute("DELETE FROM quiz_questions WHERE id=?", (qid,)); c.commit(); c.close()

def add_quiz_option(qid, text):
    c = db()
    ids = c.execute("SELECT id FROM quiz_options WHERE question_id=?", (qid,)).fetchall()
    cur = c.execute("INSERT INTO quiz_options(question_id,text,ord) VALUES(?,?,?)", (qid, text, len(ids)+1))
    oid = cur.lastrowid; c.commit(); c.close()
    return oid

def get_quiz_options(qid):
    return [dict(r) for r in db().execute(
        "SELECT * FROM quiz_options WHERE question_id=? ORDER BY ord,id", (qid,)).fetchall()]

def del_quiz_option(oid):
    c = db(); c.execute("DELETE FROM quiz_options WHERE id=?", (oid,)); c.commit(); c.close()

def set_correct_option(qid, option_idx):
    c = db()
    c.execute("UPDATE quiz_questions SET correct_option=? WHERE id=?", (option_idx, qid))
    c.commit(); c.close()

def toggle_random_quiz(bid):
    b = get_btn(bid)
    if not b: return False
    current = b.get("random_quiz", 0) or 0
    new_val = 0 if current else 1
    c = db()
    c.execute("UPDATE buttons SET random_quiz=? WHERE id=?", (new_val, bid))
    c.commit(); c.close()
    return bool(new_val)

def log_question_sent(uid, qid):
    import time as _time
    c = db()
    c.execute(
        "INSERT OR REPLACE INTO quiz_sent_log(user_id,question_id,sent_at) VALUES(?,?,?)",
        (uid, qid, int(_time.time()))
    )
    c.commit(); c.close()

def get_next_random_question(bid, uid):
    import random, time as _time
    one_hour_ago = int(_time.time()) - 3600
    questions = get_quiz_questions(bid)
    if not questions: return None
    sent_ids = {r[0] for r in db().execute(
        "SELECT question_id FROM quiz_sent_log WHERE user_id=? AND sent_at>?",
        (uid, one_hour_ago)
    ).fetchall()}
    available = [q for q in questions if q["id"] not in sent_ids]
    if not available:
        available = questions
    return random.choice(available)

def get_caption_buttons():
    return [dict(r) for r in db().execute(
        "SELECT * FROM caption_buttons ORDER BY ord,id").fetchall()]

def add_caption_button(label, url):
    c = db(); cur = c.cursor()
    n = cur.execute("SELECT COALESCE(MAX(ord),0)+1 FROM caption_buttons").fetchone()[0]
    cur.execute("INSERT INTO caption_buttons(label,url,ord) VALUES(?,?,?)", (label, url, n))
    c.commit(); c.close()

def del_caption_button(cbid):
    c = db(); c.execute("DELETE FROM caption_buttons WHERE id=?", (cbid,)); c.commit(); c.close()

def build_caption_btn_markup(buttons):
    if not buttons:
        return None
    rows = [[InlineKeyboardButton(b["label"], url=b["url"])] for b in buttons]
    return InlineKeyboardMarkup(rows)

# ── نظام التنبيهات ────────────────────────────────────────────────
def _today_str():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d")

def _ensure_user_stats(uid):
    import time as _time
    c = db()
    now = int(_time.time())
    today = _today_str()
    existing = c.execute("SELECT user_id, first_seen FROM user_stats WHERE user_id=?", (uid,)).fetchone()
    if existing is None:
        c.execute("INSERT OR IGNORE INTO user_stats(user_id, first_seen, last_active) VALUES(?,?,?)", (uid, now, now))
        c.execute("INSERT INTO daily_stats(date, new_users) VALUES(?,1) ON CONFLICT(date) DO UPDATE SET new_users=new_users+1", (today,))
    elif existing["first_seen"] == 0:
        c.execute("UPDATE user_stats SET first_seen=? WHERE user_id=?", (now, uid))
    c.commit(); c.close()

def track_message(uid):
    import time as _time
    _ensure_user_stats(uid)
    c = db()
    today = _today_str()
    now = int(_time.time())
    c.execute("UPDATE user_stats SET last_active=? WHERE user_id=?", (now, uid))
    c.execute("INSERT INTO daily_stats(date, msg_count) VALUES(?,1) ON CONFLICT(date) DO UPDATE SET msg_count=msg_count+1", (today,))
    c.commit(); c.close()

def get_user_stats(uid):
    _ensure_user_stats(uid)
    r = db().execute("SELECT * FROM user_stats WHERE user_id=?", (uid,)).fetchone()
    return dict(r) if r else {}

def inc_user_opens(uid):
    _ensure_user_stats(uid)
    c = db()
    c.execute("UPDATE user_stats SET opens=opens+1 WHERE user_id=?", (uid,))
    c.commit(); c.close()
    return db().execute("SELECT opens FROM user_stats WHERE user_id=?", (uid,)).fetchone()[0]

def inc_user_sessions(uid):
    _ensure_user_stats(uid)
    c = db()
    c.execute("UPDATE user_stats SET sessions=sessions+1 WHERE user_id=?", (uid,))
    c.commit(); c.close()
    return db().execute("SELECT sessions FROM user_stats WHERE user_id=?", (uid,)).fetchone()[0]

def mark_notif_sent(uid):
    s = get_user_stats(uid)
    c = db()
    c.execute("UPDATE user_stats SET last_notif_opens=?, last_notif_sessions=? WHERE user_id=?",
              (s.get("opens", 0), s.get("sessions", 0), uid))
    c.commit(); c.close()

def set_pending_notif(uid, bid):
    _ensure_user_stats(uid)
    c = db()
    c.execute("UPDATE user_stats SET pending_notif_bid=? WHERE user_id=?", (bid, uid))
    c.commit(); c.close()

def clear_pending_notif(uid):
    _ensure_user_stats(uid)
    c = db()
    c.execute("UPDATE user_stats SET pending_notif_bid=0 WHERE user_id=?", (uid,))
    c.commit(); c.close()

def record_channel_subscription(uid):
    import time as _time
    _ensure_user_stats(uid)
    c = db()
    already = c.execute("SELECT subscribed_via_notif FROM user_stats WHERE user_id=?", (uid,)).fetchone()
    if already and already[0] == 0:
        c.execute("UPDATE user_stats SET subscribed_via_notif=1, subscribed_at=? WHERE user_id=?", (int(_time.time()), uid))
        c.commit()
    c.close()

def get_pending_notif(uid):
    s = get_user_stats(uid)
    return s.get("pending_notif_bid", 0) or 0

def get_user_ratings_hidden(uid):
    s = get_user_stats(uid)
    return bool(s.get("ratings_hidden", 0) or 0)

def toggle_user_ratings_hidden(uid):
    _ensure_user_stats(uid)
    current = get_user_ratings_hidden(uid)
    new_val = 0 if current else 1
    c = db()
    c.execute("UPDATE user_stats SET ratings_hidden=? WHERE user_id=?", (new_val, uid))
    c.commit(); c.close()
    return bool(new_val)

async def is_subscribed(bot, uid: int):
    """
    يتحقق من اشتراك المستخدم في القناة.
    يُرجع: True إذا مشترك، False إذا غير مشترك، None إذا تعذّر الفحص.
    """
    chan = get_setting("notif_channel", "").strip()
    if not chan:
        return None
    try:
        if chan.startswith("http"):
            parts = chan.rstrip("/").split("/")
            channel_id = f"@{parts[-1]}"
        elif chan.startswith("-"):
            channel_id = int(chan)
        else:
            channel_id = f"@{chan.lstrip('@')}"
        member = await bot.get_chat_member(channel_id, uid)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return None

def should_notify(uid) -> bool:
    """النظام 1: هل يجب إظهار التنبيه المنبثق؟"""
    chan = get_setting("notif_channel", "").strip()
    if not chan:
        return False
    msg = get_setting("notif_message", "")
    if not msg:
        return False
    enabled = get_setting("notif_enabled", "1")
    if enabled != "1":
        return False
    s = get_user_stats(uid)
    opens   = s.get("opens", 0)
    last_op = s.get("last_notif_opens", 0)
    try:
        every_opens = int(get_setting("notif_every_opens", "5"))
    except Exception:
        every_opens = 5
    if every_opens > 0 and opens > 0 and (opens - last_op) >= every_opens:
        return True
    return False


async def send_notif_gate(target, uid, bid):
    """يُرسل نافذة التنبيه المنبثقة — المستخدم لا يستطيع تجاوزها."""
    msg         = get_setting("notif_message", "🔔 يرجى الاشتراك في قناتنا!")
    chan        = get_setting("notif_channel", "").strip()
    ok_text     = get_setting("notif_ok_text",    "✅ نعم، اشتركت")
    cancel_text = get_setting("notif_cancel_text", "❌ لا، لاحقاً")

    rows = []
    if chan:
        url = chan if chan.startswith("http") else f"https://t.me/{chan.lstrip('@')}"
        rows.append([InlineKeyboardButton("📢 انضم للقناة الآن", url=url)])
    rows.append([
        InlineKeyboardButton(ok_text,     callback_data=f"notif_ok_{bid}"),
        InlineKeyboardButton(cancel_text, callback_data=f"notif_skip_{bid}"),
    ])
    markup = InlineKeyboardMarkup(rows)
    try:
        try:
            await target.reply_text(msg, parse_mode="Markdown", reply_markup=markup)
        except Exception:
            await target.reply_text(msg, reply_markup=markup)
        mark_notif_sent(uid)
        set_pending_notif(uid, bid)
    except Exception:
        pass

def get_pomodoro_settings(uid: int) -> dict:
    r = db().execute("SELECT * FROM pomodoro_settings WHERE user_id=?", (uid,)).fetchone()
    if r:
        return dict(r)
    return {"user_id": uid, "enabled": 1, "study_min": 25, "break_min": 5}

def save_pomodoro_settings(uid: int, enabled=None, study_min=None, break_min=None):
    cur = get_pomodoro_settings(uid)
    if enabled   is not None: cur["enabled"]   = enabled
    if study_min is not None: cur["study_min"] = study_min
    if break_min is not None: cur["break_min"] = break_min
    c = db()
    c.execute(
        "INSERT OR REPLACE INTO pomodoro_settings(user_id,enabled,study_min,break_min) VALUES(?,?,?,?)",
        (uid, cur["enabled"], cur["study_min"], cur["break_min"])
    )
    c.commit(); c.close()

def parse_pomodoro_minutes(text: str, max_minutes: int = 240):
    if not text:
        return None
    import re
    match = re.search(r"\d+", text.strip())
    if not match:
        return None
    try:
        val = int(match.group(0))
    except Exception:
        return None
    if val < 1 or val > max_minutes:
        return None
    return val

def pomodoro_settings_text(uid: int) -> str:
    s = get_pomodoro_settings(uid)
    status = "✅ مفعّل" if s["enabled"] else "❌ موقف"
    return (
        f"🍅 *مؤقت الدراسة (بومودورو)*\n\n"
        f"⏱ الوضع: {s['study_min']} دراسة + {s['break_min']} استراحة\n"
        f"الحالة: {status}"
    )

def parse_stars_amount(text: str, max_stars: int = 10000):
    if not text:
        return None
    import re
    match = re.search(r"\d+", text.strip())
    if not match:
        return None
    try:
        amount = int(match.group(0))
    except Exception:
        return None
    if amount < 1 or amount > max_stars:
        return None
    return amount

def donation_text() -> str:
    return (
        "💝 *دعم البوت بالنجوم*\n\n"
        "إذا استفدت من المحتوى وتحب تدعم استمرار البوت، تقدر تتبرع بأي عدد من نجوم تلغرام.\n\n"
        "اختر مبلغاً جاهزاً أو اكتب عدد النجوم الذي تريده."
    )

def default_donation_thanks_message() -> str:
    return "💝 شكراً جزيلاً على دعمك بـ {stars} نجمة!\n\nدعمك يساعدنا نستمر ونطور المحتوى."

def get_donation_thanks_message(stars: int = 0) -> str:
    msg = get_setting("donation_thanks_message", default_donation_thanks_message())
    if not msg:
        msg = default_donation_thanks_message()
    stars_text = str(stars) if stars else "نجوم"
    return msg.replace("{stars}", stars_text)

def kb_donation_stars(uid=None):
    rows = [
        [
            InlineKeyboardButton("10 ⭐", callback_data="don_amount_10"),
            InlineKeyboardButton("25 ⭐", callback_data="don_amount_25"),
            InlineKeyboardButton("50 ⭐", callback_data="don_amount_50"),
        ],
        [
            InlineKeyboardButton("100 ⭐", callback_data="don_amount_100"),
            InlineKeyboardButton("250 ⭐", callback_data="don_amount_250"),
        ],
        [InlineKeyboardButton("✏️ أكتب عدد النجوم", callback_data="don_custom")],
    ]
    if uid is not None and is_admin(uid):
        rows.append([InlineKeyboardButton("✏️ تعديل رسالة الشكر", callback_data="don_thanks_set")])
    rows.append([InlineKeyboardButton("❌ إغلاق", callback_data="don_close")])
    return InlineKeyboardMarkup(rows)

def toggle_ratings_text(uid: int) -> str:
    hidden = get_user_ratings_hidden(uid)
    status = "⭕ مخفية حالياً" if hidden else "✅ ظاهرة حالياً"
    desc = (
        "عند إخفاء التقييمات لن تظهر لك رسائل التقييم بعد استلام الملفات."
        if not hidden else
        "عند تفعيل التقييمات ستظهر لك رسائل التقييم بعد استلام الملفات."
    )
    return (
        f"⭐ *إعدادات التقييمات*\n\n"
        f"الحالة: {status}\n\n"
        f"{desc}"
    )

def kb_toggle_ratings(uid: int):
    hidden = get_user_ratings_hidden(uid)
    toggle_label = "✅ تفعيل التقييمات" if hidden else "🚫 إخفاء التقييمات"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_label, callback_data="rating_toggle")],
        [InlineKeyboardButton("❌ إغلاق", callback_data="rating_close")],
    ])

async def send_stars_invoice(bot, chat_id: int, stars: int):
    await bot.send_invoice(
        chat_id=chat_id,
        title="دعم البوت بالنجوم",
        description=f"تبرع اختياري لدعم استمرار البوت بقيمة {stars} نجمة.",
        payload=f"stars_donation:{stars}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label=f"{stars} نجمة", amount=stars)],
    )

def _setup_pomodoro_feature():
    """يضبط زر 421 كحاوية وينشئ الأزرار الخاصة داخله إن لم تكن موجودة."""
    c = db()
    b421 = c.execute("SELECT * FROM buttons WHERE id=421").fetchone()
    if not b421:
        c.close(); return
    c.execute("UPDATE buttons SET special_action='container' WHERE id=421")
    existing = c.execute(
        "SELECT id FROM buttons WHERE parent_id=421 AND special_action='pomodoro' LIMIT 1"
    ).fetchone()
    if not existing:
        ids = [r[0] for r in c.execute(
            "SELECT id FROM buttons WHERE parent_id=421 ORDER BY ord,id"
        ).fetchall()]
        c.execute(
            "INSERT INTO buttons(parent_id,type,label,ord,new_row,special_action) VALUES(?,?,?,?,?,?)",
            (421, "special", "🍅 مؤقت الدراسة", len(ids)+1, 1, "pomodoro")
        )
    existing_donate = c.execute(
        "SELECT id FROM buttons WHERE parent_id=421 AND special_action='donate_stars' LIMIT 1"
    ).fetchone()
    if not existing_donate:
        ids = [r[0] for r in c.execute(
            "SELECT id FROM buttons WHERE parent_id=421 ORDER BY ord,id"
        ).fetchall()]
        c.execute(
            "INSERT INTO buttons(parent_id,type,label,ord,new_row,special_action) VALUES(?,?,?,?,?,?)",
            (421, "special", "💝 ادعمنا بالنجوم", len(ids)+1, 1, "donate_stars")
        )
    existing_toggle_ratings = c.execute(
        "SELECT id FROM buttons WHERE parent_id=421 AND special_action='toggle_ratings' LIMIT 1"
    ).fetchone()
    if not existing_toggle_ratings:
        ids = [r[0] for r in c.execute(
            "SELECT id FROM buttons WHERE parent_id=421 ORDER BY ord,id"
        ).fetchall()]
        c.execute(
            "INSERT INTO buttons(parent_id,type,label,ord,new_row,special_action) VALUES(?,?,?,?,?,?)",
            (421, "special", "⭐ التقييمات", len(ids)+1, 1, "toggle_ratings")
        )
    existing_file_request = c.execute(
        "SELECT id FROM buttons WHERE parent_id=421 AND special_action='file_request' LIMIT 1"
    ).fetchone()
    if not existing_file_request:
        ids = [r[0] for r in c.execute(
            "SELECT id FROM buttons WHERE parent_id=421 ORDER BY ord,id"
        ).fetchall()]
        c.execute(
            "INSERT INTO buttons(parent_id,type,label,ord,new_row,special_action) VALUES(?,?,?,?,?,?)",
            (421, "special", "📩 طلب إضافة ملف", len(ids)+1, 1, "file_request")
        )
    c.commit(); c.close()
