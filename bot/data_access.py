from .shared import *

# ── قاعدة البيانات ────────────────────────────────────────────────
def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with db() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY, username TEXT);
            CREATE TABLE IF NOT EXISTS buttons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER REFERENCES buttons(id) ON DELETE CASCADE,
                type TEXT NOT NULL, label TEXT NOT NULL,
                ord INTEGER DEFAULT 0,
                new_row INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS content_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                button_id INTEGER NOT NULL REFERENCES buttons(id) ON DELETE CASCADE,
                type TEXT NOT NULL,
                content TEXT,
                file_id TEXT,
                local_path TEXT,
                channel_msg_id INTEGER,
                ord INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            CREATE TABLE IF NOT EXISTS caption_buttons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                label TEXT NOT NULL,
                url TEXT NOT NULL,
                ord INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id   INTEGER PRIMARY KEY,
                opens     INTEGER DEFAULT 0,
                sessions  INTEGER DEFAULT 0,
                last_notif_opens    INTEGER DEFAULT 0,
                last_notif_sessions INTEGER DEFAULT 0
            );
        """)
        try:
            c.execute("ALTER TABLE buttons ADD COLUMN new_row INTEGER DEFAULT 1")
            c.commit()
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE buttons ADD COLUMN click_count INTEGER DEFAULT 0")
            c.commit()
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE content_items ADD COLUMN local_path TEXT")
            c.commit()
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE buttons ADD COLUMN no_caption INTEGER DEFAULT 0")
            c.commit()
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE buttons ADD COLUMN no_btn_caption INTEGER DEFAULT 0")
            c.commit()
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE user_stats ADD COLUMN pending_notif_bid INTEGER DEFAULT 0")
            c.commit()
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE user_stats ADD COLUMN subscribed_via_notif INTEGER DEFAULT 0")
            c.commit()
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE user_stats ADD COLUMN subscribed_at INTEGER DEFAULT 0")
            c.commit()
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE user_stats ADD COLUMN first_seen INTEGER DEFAULT 0")
            c.commit()
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE user_stats ADD COLUMN last_active INTEGER DEFAULT 0")
            c.commit()
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE user_stats ADD COLUMN ratings_hidden INTEGER DEFAULT 0")
            c.commit()
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE user_stats ADD COLUMN username TEXT")
            c.commit()
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE user_stats ADD COLUMN first_name TEXT")
            c.commit()
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE content_items ADD COLUMN channel_msg_id INTEGER")
            c.commit()
        except Exception:
            pass
        c.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date      TEXT PRIMARY KEY,
                msg_count INTEGER DEFAULT 0,
                new_users INTEGER DEFAULT 0
            );
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS user_button_clicks (
                user_id   INTEGER NOT NULL,
                button_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, button_id)
            );
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS motivational_phrases (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                phrase TEXT NOT NULL
            );
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS pomodoro_settings (
                user_id   INTEGER PRIMARY KEY,
                enabled   INTEGER DEFAULT 1,
                study_min INTEGER DEFAULT 25,
                break_min INTEGER DEFAULT 5
            );
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS item_ratings (
                item_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                rating INTEGER NOT NULL,
                rated_at INTEGER DEFAULT 0,
                PRIMARY KEY (item_id, user_id)
            );
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS file_request_admins (
                user_id INTEGER PRIMARY KEY,
                username TEXT
            );
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS file_reply_sessions (
                admin_id   INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                user_id    INTEGER NOT NULL,
                PRIMARY KEY (admin_id, message_id)
            );
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS user_reply_sessions (
                user_id    INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                PRIMARY KEY (user_id, message_id)
            );
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS active_file_convos (
                user_id INTEGER PRIMARY KEY
            );
        """)
        c.commit()
        try:
            c.execute("ALTER TABLE buttons ADD COLUMN special_action TEXT DEFAULT NULL")
            c.commit()
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE buttons ADD COLUMN unified_rating INTEGER DEFAULT 0")
            c.commit()
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE buttons ADD COLUMN random_quiz INTEGER DEFAULT 0")
            c.commit()
        except Exception:
            pass
        c.execute("""
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                button_id INTEGER NOT NULL REFERENCES buttons(id) ON DELETE CASCADE,
                question  TEXT NOT NULL,
                correct_option INTEGER DEFAULT 0,
                explanation    TEXT DEFAULT '',
                ord       INTEGER DEFAULT 0
            );
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS quiz_options (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL REFERENCES quiz_questions(id) ON DELETE CASCADE,
                text        TEXT NOT NULL,
                ord         INTEGER DEFAULT 0
            );
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS quiz_sent_log (
                user_id     INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                sent_at     INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, question_id)
            );
        """)
        c.commit()
        try:
            c.execute("ALTER TABLE buttons ADD COLUMN random_exam INTEGER DEFAULT 0")
            c.commit()
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE settings ADD COLUMN key TEXT")
            c.commit()
        except Exception:
            pass
        c.execute("""
            CREATE TABLE IF NOT EXISTS exam_questions (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                button_id INTEGER NOT NULL REFERENCES buttons(id) ON DELETE CASCADE,
                q_type    TEXT NOT NULL DEFAULT 'text',
                q_text    TEXT,
                q_file_id TEXT,
                a_type    TEXT NOT NULL DEFAULT 'text',
                a_text    TEXT,
                a_file_id TEXT,
                ord       INTEGER DEFAULT 0
            );
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS button_ratings (
                button_id INTEGER NOT NULL,
                user_id   INTEGER NOT NULL,
                rating    INTEGER NOT NULL,
                rated_at  INTEGER DEFAULT 0,
                PRIMARY KEY (button_id, user_id)
            );
        """)
        c.commit()

def is_admin(uid):
    return db().execute("SELECT 1 FROM admins WHERE id=?", (uid,)).fetchone() is not None

def add_admin(uid, name=None):
    c = db(); c.execute("INSERT OR IGNORE INTO admins VALUES(?,?)", (uid, name)); c.commit(); c.close()

def update_user_info(uid, username=None, first_name=None):
    c = db()
    if username is not None:
        c.execute("UPDATE user_stats SET username=? WHERE user_id=?", (username.lstrip("@") if username else None, uid))
    if first_name is not None:
        c.execute("UPDATE user_stats SET first_name=? WHERE user_id=?", (first_name, uid))
    c.commit(); c.close()

def update_admin_username(uid, username=None):
    if not username:
        return
    c = db()
    c.execute("UPDATE admins SET username=? WHERE id=?", (username.lstrip("@"), uid))
    c.commit(); c.close()

def get_start_message():
    return get_setting("start_message", "👋 أهلاً!")

def set_start_message(value):
    set_setting("start_message", value)

def get_admin_by_username(username):
    username = (username or "").strip().lstrip("@").lower()
    if not username:
        return None
    r = db().execute(
        "SELECT * FROM admins WHERE lower(COALESCE(username,''))=?",
        (username,)
    ).fetchone()
    return dict(r) if r else None

def del_admin(uid):
    c = db(); c.execute("DELETE FROM admins WHERE id=?", (uid,)); c.commit(); c.close()

def all_admins():
    return [dict(r) for r in db().execute("SELECT * FROM admins").fetchall()]

def get_setting(key, default=None):
    r = db().execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return r[0] if r else default

def set_setting(key, value):
    c = db()
    c.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key, value))
    c.commit(); c.close()

def get_global_caption():
    return get_setting("global_caption", "")

def get_storage_channel_id():
    return STORAGE_CHANNEL_ID

def get_buttons(pid=None):
    if pid is None:
        q = "SELECT * FROM buttons WHERE parent_id IS NULL ORDER BY ord,id"
        return [dict(r) for r in db().execute(q).fetchall()]
    return [dict(r) for r in db().execute(
        "SELECT * FROM buttons WHERE parent_id=? ORDER BY ord,id", (pid,)).fetchall()]

def get_btn(bid):
    r = db().execute("SELECT * FROM buttons WHERE id=?", (bid,)).fetchone()
    return dict(r) if r else None

def _siblings(cur, pid):
    if pid is None:
        return [r[0] for r in cur.execute(
            "SELECT id FROM buttons WHERE parent_id IS NULL ORDER BY ord,id").fetchall()]
    return [r[0] for r in cur.execute(
        "SELECT id FROM buttons WHERE parent_id=? ORDER BY ord,id", (pid,)).fetchall()]

def _renumber(cur, ids):
    for i, bid in enumerate(ids):
        cur.execute("UPDATE buttons SET ord=? WHERE id=?", (i + 1, bid))

def add_btn(pid, t, label):
    """يضيف زراً في نهاية القائمة."""
    c = db(); cur = c.cursor()
    ids = _siblings(cur, pid)
    cur.execute("INSERT INTO buttons(parent_id,type,label,ord) VALUES(?,?,?,?)",
                (pid, t, label, len(ids) + 1))
    lid = cur.lastrowid; c.commit(); c.close(); return lid

def add_btn_before(before_bid, pid, t, label):
    """يضيف زراً في صف جديد قبل before_bid مباشرة."""
    c = db(); cur = c.cursor()
    ids = _siblings(cur, pid)
    pos = ids.index(before_bid) if before_bid in ids else 0
    cur.execute("INSERT INTO buttons(parent_id,type,label,ord,new_row) VALUES(?,?,?,?,?)",
                (pid, t, label, 0, 1))
    new_id = cur.lastrowid
    ids.insert(pos, new_id)
    _renumber(cur, ids)
    c.commit(); c.close(); return new_id

def add_btn_after(after_bid, pid, t, label, new_row=1):
    """يضيف زراً بعد after_bid، أو في البداية إذا كان after_bid=None."""
    c = db(); cur = c.cursor()
    ids = _siblings(cur, pid)
    if after_bid is None:
        pos = 0
    else:
        pos = (ids.index(after_bid) + 1) if after_bid in ids else len(ids)
    cur.execute("INSERT INTO buttons(parent_id,type,label,ord,new_row) VALUES(?,?,?,?,?)",
                (pid, t, label, 0, new_row))
    new_id = cur.lastrowid
    ids.insert(pos, new_id)
    _renumber(cur, ids)
    c.commit(); c.close(); return new_id

def upd_btn_label(bid, label):
    c = db(); c.execute("UPDATE buttons SET label=? WHERE id=?", (label, bid)); c.commit(); c.close()

def inc_click_count(bid, uid=None):
    c = db()
    if uid is not None:
        try:
            c.execute("INSERT INTO user_button_clicks(user_id, button_id) VALUES(?,?)", (uid, bid))
            c.execute("UPDATE buttons SET click_count=COALESCE(click_count,0)+1 WHERE id=?", (bid,))
        except Exception:
            pass  # المستخدم ضغط من قبل، لا نعدّ مرة ثانية
    else:
        c.execute("UPDATE buttons SET click_count=COALESCE(click_count,0)+1 WHERE id=?", (bid,))
    c.commit(); c.close()

def get_btn_path(bid) -> str:
    """يُرجع المسار الكامل للزر: قسم1 ‹ قسم2 ‹ اسم الزر"""
    parts = []
    current = get_btn(bid)
    while current:
        parts.append(current["label"])
        pid = current.get("parent_id")
        current = get_btn(pid) if pid else None
    parts.reverse()
    return " › ".join(parts)

def _create_nested_buttons(parent_id, buttons_list, anchor_id=None, use_after=False):
    """ينشئ قائمة أزرار داخل parent_id بشكل متداخل (يدعم children)."""
    added = []
    last_id = anchor_id
    for btn in buttons_list:
        label = btn.get("label", "").strip()
        btype = btn.get("type", "menu")
        new_row = btn.get("new_row", True)
        children = btn.get("children", [])
        if not label:
            continue
        if btype not in ("menu", "content"):
            btype = "menu"
        nr = 0 if not new_row else 1
        if last_id is None and not use_after:
            new_id = add_btn(parent_id, btype, label)
        else:
            new_id = add_btn_after(last_id, parent_id, btype, label, new_row=nr)
        last_id = new_id
        use_after = True
        depth = "📂" if btype == "menu" else "📄"
        added.append(f"{depth} {label}")
        if children and btype == "menu":
            child_added = _create_nested_buttons(new_id, children)
            added.extend(f"  └ {a}" for a in child_added)
    return added

def del_btn(bid):
    c = db(); c.execute("DELETE FROM buttons WHERE id=?", (bid,)); c.commit(); c.close()

# ── الزر الخاص (singleton type='special') ─────────────────────────
def get_special_btn():
    r = db().execute("SELECT * FROM buttons WHERE type='special' LIMIT 1").fetchone()
    return dict(r) if r else None

def create_special_btn(label: str, pid=None) -> int:
    """ينشئ الزر الخاص في نهاية المستوى المحدد ويُرجع id."""
    return add_btn(pid, "special", label)

def move_special_btn(bid: int, new_pid):
    """ينقل الزر الخاص إلى مستوى جديد (new_pid=None يعني الجذر)."""
    c = db()
    ids = _siblings(c.cursor(), new_pid)
    new_ord = len(ids) + 1
    if new_pid is None:
        c.execute("UPDATE buttons SET parent_id=NULL, ord=?, new_row=1 WHERE id=?", (new_ord, bid))
    else:
        c.execute("UPDATE buttons SET parent_id=?, ord=?, new_row=1 WHERE id=?", (new_pid, new_ord, bid))
    c.commit(); c.close()

def all_menu_levels() -> list:
    """يُرجع قائمة بجميع أزرار النوع menu مرتبة (للاختيار من بينها كوجهة نقل)."""
    return [dict(r) for r in db().execute(
        "SELECT id, label, parent_id FROM buttons WHERE type='menu' ORDER BY ord, id"
    ).fetchall()]

def get_all_special_btns() -> list:
    """يُرجع قائمة بجميع الأزرار المميزة."""
    return [dict(r) for r in db().execute(
        "SELECT * FROM buttons WHERE type='special' ORDER BY ord, id"
    ).fetchall()]

def set_btn_special_action(bid, action):
    c = db()
    c.execute("UPDATE buttons SET special_action=? WHERE id=?", (action, bid))
    c.commit(); c.close()

def get_file_request_admins():
    return [dict(r) for r in db().execute(
        "SELECT user_id, username FROM file_request_admins ORDER BY user_id"
    ).fetchall()]

def is_file_supervisor(uid):
    if is_admin(uid):
        return True
    return db().execute(
        "SELECT 1 FROM file_request_admins WHERE user_id=?", (uid,)
    ).fetchone() is not None

def add_file_request_admin(uid, username=None):
    c = db()
    c.execute(
        "INSERT OR REPLACE INTO file_request_admins(user_id,username) VALUES(?,?)",
        (uid, username)
    )
    c.commit(); c.close()

def del_file_request_admin(uid):
    c = db()
    c.execute("DELETE FROM file_request_admins WHERE user_id=?", (uid,))
    c.commit(); c.close()

def save_file_reply_session(admin_id, message_id, user_id):
    c = db()
    c.execute(
        "INSERT OR REPLACE INTO file_reply_sessions(admin_id,message_id,user_id) VALUES(?,?,?)",
        (admin_id, message_id, user_id)
    )
    c.commit(); c.close()

def get_file_reply_user(admin_id, message_id):
    r = db().execute(
        "SELECT user_id FROM file_reply_sessions WHERE admin_id=? AND message_id=?",
        (admin_id, message_id)
    ).fetchone()
    return r["user_id"] if r else None

def del_file_reply_session(admin_id, message_id):
    c = db()
    c.execute("DELETE FROM file_reply_sessions WHERE admin_id=? AND message_id=?", (admin_id, message_id))
    c.commit(); c.close()

def save_user_reply_session(user_id, message_id):
    c = db()
    c.execute(
        "INSERT OR REPLACE INTO user_reply_sessions(user_id,message_id) VALUES(?,?)",
        (user_id, message_id)
    )
    c.commit(); c.close()

def is_user_reply_msg(user_id, message_id):
    return db().execute(
        "SELECT 1 FROM user_reply_sessions WHERE user_id=? AND message_id=?",
        (user_id, message_id)
    ).fetchone() is not None

def set_file_convo_active(user_id):
    c = db()
    c.execute("INSERT OR IGNORE INTO active_file_convos(user_id) VALUES(?)", (user_id,))
    c.commit(); c.close()

def is_file_convo_active(user_id):
    return db().execute(
        "SELECT 1 FROM active_file_convos WHERE user_id=?", (user_id,)
    ).fetchone() is not None

def clear_file_convo(user_id):
    c = db()
    c.execute("DELETE FROM active_file_convos WHERE user_id=?", (user_id,))
    c.commit(); c.close()

def swap_btns(bid1, bid2):
    """يبدّل موضع زرين (ord + new_row)."""
    c = db(); cur = c.cursor()
    b1 = dict(cur.execute("SELECT ord, new_row FROM buttons WHERE id=?", (bid1,)).fetchone())
    b2 = dict(cur.execute("SELECT ord, new_row FROM buttons WHERE id=?", (bid2,)).fetchone())
    cur.execute("UPDATE buttons SET ord=?, new_row=? WHERE id=?", (b2['ord'], b2['new_row'], bid1))
    cur.execute("UPDATE buttons SET ord=?, new_row=? WHERE id=?", (b1['ord'], b1['new_row'], bid2))
    c.commit(); c.close()

# ── content_items ─────────────────────────────────────────────────
def get_items(bid):
    return [dict(r) for r in db().execute(
        "SELECT * FROM content_items WHERE button_id=? ORDER BY ord,id", (bid,)).fetchall()]

def add_item(bid, t, content=None, file_id=None, local_path=None, channel_msg_id=None):
    c = db(); cur = c.cursor()
    n = cur.execute("SELECT COALESCE(MAX(ord),0)+1 FROM content_items WHERE button_id=?", (bid,)).fetchone()[0]
    cur.execute("INSERT INTO content_items(button_id,type,content,file_id,local_path,channel_msg_id,ord) VALUES(?,?,?,?,?,?,?)",
                (bid, t, content, file_id, local_path, channel_msg_id, n))
    c.commit(); c.close()

def upd_item_file_id(iid, file_id):
    c = db(); c.execute("UPDATE content_items SET file_id=? WHERE id=?", (file_id, iid)); c.commit(); c.close()

def upd_item_channel_msg_id(iid, channel_msg_id):
    c = db(); c.execute("UPDATE content_items SET channel_msg_id=? WHERE id=?", (channel_msg_id, iid)); c.commit(); c.close()

def del_item(iid):
    c = db(); c.execute("DELETE FROM content_items WHERE id=?", (iid,)); c.commit(); c.close()

def upd_item_content(iid, content):
    c = db(); c.execute("UPDATE content_items SET content=? WHERE id=?", (content, iid)); c.commit(); c.close()

def get_item(iid):
    r = db().execute("SELECT * FROM content_items WHERE id=?", (iid,)).fetchone()
    return dict(r) if r else None

def get_item_rating_summary(iid: int) -> dict:
    row = db().execute(
        "SELECT COUNT(*) AS cnt, COALESCE(AVG(rating),0) AS avg_rating FROM item_ratings WHERE item_id=?",
        (iid,)
    ).fetchone()
    return {"count": row["cnt"] if row else 0, "avg": float(row["avg_rating"] or 0) if row else 0.0}

def get_user_item_rating(iid: int, uid: int):
    row = db().execute(
        "SELECT rating FROM item_ratings WHERE item_id=? AND user_id=?",
        (iid, uid)
    ).fetchone()
    return row["rating"] if row else None

def save_item_rating(iid: int, uid: int, rating: int):
    import time as _time
    c = db()
    c.execute(
        "INSERT OR REPLACE INTO item_ratings(item_id,user_id,rating,rated_at) VALUES(?,?,?,?)",
        (iid, uid, rating, int(_time.time()))
    )
    c.commit(); c.close()

def rating_stars(avg: float) -> str:
    filled = int(round(avg))
    filled = max(0, min(5, filled))
    return "★" * filled + "☆" * (5 - filled)

def item_rating_text(iid: int, uid: int | None = None) -> str:
    s = get_item_rating_summary(iid)
    if s["count"] == 0:
        rating_line = "⭐ تقييم الملف: لا يوجد تقييم بعد"
    else:
        rating_line = f"⭐ تقييم الملف: {rating_stars(s['avg'])} {s['avg']:.1f}/5"
    count_line = f"👥 عدد التقييمات: {s['count']}"
    user_line = ""
    if uid:
        user_rating = get_user_item_rating(iid, uid)
        if user_rating:
            user_line = f"\n✅ تقييمك: {user_rating}/5"
    return f"{rating_line}\n{count_line}{user_line}"

def kb_item_rating(iid: int):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("⭐ قيّم الملف", callback_data=f"rate_open_{iid}")
    ]])

def kb_item_rating_choices(iid: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⭐" * i, callback_data=f"rate_set_{iid}_{i}") for i in range(1, 4)],
        [InlineKeyboardButton("⭐" * i, callback_data=f"rate_set_{iid}_{i}") for i in range(4, 6)],
        [InlineKeyboardButton("رجوع", callback_data=f"rate_back_{iid}")],
    ])

async def send_item_rating_message(target, item, uid=None):
    if item.get("type") == "text":
        return
    iid = item.get("id")
    if not iid:
        return
    await target.reply_text(item_rating_text(iid, uid), reply_markup=kb_item_rating(iid))

# ── تقييم موحد على مستوى الزر ────────────────────────────────────
def get_btn_rating_summary(bid: int) -> dict:
    row = db().execute(
        "SELECT COUNT(*) AS cnt, COALESCE(AVG(rating),0) AS avg_rating FROM button_ratings WHERE button_id=?",
        (bid,)
    ).fetchone()
    return {"count": row["cnt"] if row else 0, "avg": float(row["avg_rating"] or 0) if row else 0.0}

def get_user_btn_rating(bid: int, uid: int):
    row = db().execute(
        "SELECT rating FROM button_ratings WHERE button_id=? AND user_id=?",
        (bid, uid)
    ).fetchone()
    return row["rating"] if row else None

def save_btn_rating(bid: int, uid: int, rating: int):
    import time as _time
    c = db()
    c.execute(
        "INSERT OR REPLACE INTO button_ratings(button_id,user_id,rating,rated_at) VALUES(?,?,?,?)",
        (bid, uid, rating, int(_time.time()))
    )
    c.commit(); c.close()

def btn_rating_text(bid: int, uid: int | None = None) -> str:
    s = get_btn_rating_summary(bid)
    if s["count"] == 0:
        rating_line = "⭐ تقييم المحتوى: لا يوجد تقييم بعد"
    else:
        rating_line = f"⭐ تقييم المحتوى: {rating_stars(s['avg'])} {s['avg']:.1f}/5"
    count_line = f"👥 عدد التقييمات: {s['count']}"
    user_line = ""
    if uid:
        user_rating = get_user_btn_rating(bid, uid)
        if user_rating:
            user_line = f"\n✅ تقييمك: {user_rating}/5"
    return f"{rating_line}\n{count_line}{user_line}"

def kb_btn_rating(bid: int):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("⭐ قيّم المحتوى", callback_data=f"brate_open_{bid}")
    ]])

def kb_btn_rating_choices(bid: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⭐" * i, callback_data=f"brate_set_{bid}_{i}") for i in range(1, 4)],
        [InlineKeyboardButton("⭐" * i, callback_data=f"brate_set_{bid}_{i}") for i in range(4, 6)],
        [InlineKeyboardButton("رجوع", callback_data=f"brate_back_{bid}")],
    ])

async def send_btn_unified_rating_message(target, bid: int, uid=None):
    await target.reply_text(btn_rating_text(bid, uid), reply_markup=kb_btn_rating(bid))


def get_stats() -> str:
    import time as _time
    now = int(_time.time())
    today = _today_str()
    yesterday = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    day30_ago  = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    ts_7d  = now - 7  * 86400
    ts_14d = now - 14 * 86400
    ts_30d = now - 30 * 86400

    with db() as c:
        # ── المستخدمون ──────────────────────────────────
        total_users   = c.execute("SELECT COUNT(*) FROM user_stats").fetchone()[0]
        new_today     = c.execute("SELECT COALESCE(SUM(new_users),0) FROM daily_stats WHERE date=?", (today,)).fetchone()[0]
        new_yesterday = c.execute("SELECT COALESCE(SUM(new_users),0) FROM daily_stats WHERE date=?", (yesterday,)).fetchone()[0]
        new_month     = c.execute("SELECT COALESCE(SUM(new_users),0) FROM daily_stats WHERE date>=?", (day30_ago,)).fetchone()[0]

        # ── الرسائل ──────────────────────────────────────
        msg_today     = c.execute("SELECT COALESCE(SUM(msg_count),0) FROM daily_stats WHERE date=?", (today,)).fetchone()[0]
        msg_yesterday = c.execute("SELECT COALESCE(SUM(msg_count),0) FROM daily_stats WHERE date=?", (yesterday,)).fetchone()[0]
        msg_month     = c.execute("SELECT COALESCE(SUM(msg_count),0) FROM daily_stats WHERE date>=?", (day30_ago,)).fetchone()[0]

        # ── الاحتفاظ بالمستخدمين ─────────────────────────
        # مستخدمون انضموا قبل 14 يوم أو أكثر (يمكن تقييمهم)
        eligible_7d  = c.execute("SELECT COUNT(*) FROM user_stats WHERE first_seen>0 AND first_seen<=?", (ts_14d,)).fetchone()[0]
        retained_7d  = c.execute("SELECT COUNT(*) FROM user_stats WHERE first_seen>0 AND first_seen<=? AND last_active>=?", (ts_14d, ts_7d)).fetchone()[0]
        eligible_30d = c.execute("SELECT COUNT(*) FROM user_stats WHERE first_seen>0 AND first_seen<=?", (ts_30d,)).fetchone()[0]
        retained_30d = c.execute("SELECT COUNT(*) FROM user_stats WHERE first_seen>0 AND first_seen<=? AND last_active>=?", (ts_30d, ts_30d)).fetchone()[0]

        # ── القناة ───────────────────────────────────────
        import time as _time2
        ts_today_start    = int(datetime.datetime.utcnow().replace(hour=0,minute=0,second=0,microsecond=0).timestamp())
        ts_yest_start     = ts_today_start - 86400
        ts_month_start    = int((_time2.time()) - 30 * 86400)
        subscribed_via_notif  = c.execute("SELECT COUNT(*) FROM user_stats WHERE subscribed_via_notif=1").fetchone()[0]
        sub_today             = c.execute("SELECT COUNT(*) FROM user_stats WHERE subscribed_at>=?", (ts_today_start,)).fetchone()[0]
        sub_yesterday         = c.execute("SELECT COUNT(*) FROM user_stats WHERE subscribed_at>=? AND subscribed_at<?", (ts_yest_start, ts_today_start)).fetchone()[0]
        sub_month             = c.execute("SELECT COUNT(*) FROM user_stats WHERE subscribed_at>=?", (ts_month_start,)).fetchone()[0]

        # ── البوت ────────────────────────────────────────
        total_btns = c.execute("SELECT COUNT(*) FROM buttons").fetchone()[0]
        menus      = c.execute("SELECT COUNT(*) FROM buttons WHERE type='menu'").fetchone()[0]
        content    = c.execute("SELECT COUNT(*) FROM buttons WHERE type='content'").fetchone()[0]
        admins     = c.execute("SELECT COUNT(*) FROM admins").fetchone()[0]

    retention_7d  = f"{round(retained_7d/eligible_7d*100)}%" if eligible_7d > 0 else "—"
    retention_30d = f"{round(retained_30d/eligible_30d*100)}%" if eligible_30d > 0 else "—"
    sub_rate      = f"{round(subscribed_via_notif/total_users*100)}%" if total_users > 0 else "—"
    db_size_kb    = round(os.path.getsize(DB) / 1024, 1) if os.path.exists(DB) else 0

    return (
        "📊 *إحصائيات البوت*\n\n"
        "👥 *المستخدمون*\n"
        f"  ├ إجمالي المستخدمين: `{total_users}`\n"
        f"  ├ جدد اليوم: `{new_today}`\n"
        f"  ├ جدد الأمس: `{new_yesterday}`\n"
        f"  └ جدد آخر 30 يوم: `{new_month}`\n\n"
        "📢 *الاشتراك بالقناة*\n"
        f"  ├ إجمالي المشتركين عبر الرسالة: `{subscribed_via_notif}` ({sub_rate})\n"
        f"  ├ اليوم: `{sub_today}`\n"
        f"  ├ الأمس: `{sub_yesterday}`\n"
        f"  └ آخر 30 يوم: `{sub_month}`\n\n"
        "💬 *الرسائل*\n"
        f"  ├ اليوم: `{msg_today}`\n"
        f"  ├ الأمس: `{msg_yesterday}`\n"
        f"  └ آخر 30 يوم: `{msg_month}`\n\n"
        "📈 *معدل الاحتفاظ بالمستخدمين*\n"
        f"  ├ خلال 7 أيام: `{retention_7d}`\n"
        f"  └ خلال 30 يوم: `{retention_30d}`\n\n"
        "🤖 *البوت*\n"
        f"  ├ قوائم: `{menus}` | محتوى: `{content}` | إجمالي: `{total_btns}`\n"
        f"  ├ المشرفون: `{admins}`\n"
        f"  └ حجم قاعدة البيانات: `{db_size_kb} KB`"
    )

def get_trending_page(page: int, page_size: int = 10):
    """يُرجع (قائمة الأزرار, إجمالي العدد) لصفحة معينة مرتّبة بالأكثر طلباً."""
    offset = page * page_size
    rows = db().execute(
        "SELECT id, label, click_count FROM buttons WHERE type='content' AND COALESCE(click_count,0)>0 "
        "ORDER BY click_count DESC LIMIT ? OFFSET ?",
        (page_size, offset)
    ).fetchall()
    total = db().execute(
        "SELECT COUNT(*) FROM buttons WHERE type='content' AND COALESCE(click_count,0)>0"
    ).fetchone()[0]
    return [dict(r) for r in rows], total

_TYPE_ICON = {"text": "📝", "photo": "🖼", "video": "🎬", "file": "📁", "audio": "🎵"}

def _content_summary(bid) -> str:
    """يُرجع ملخص أنواع المحتوى داخل الزر مثل: 🖼×2 🎬×1"""
    rows = db().execute(
        "SELECT type, COUNT(*) as cnt FROM content_items WHERE button_id=? GROUP BY type", (bid,)
    ).fetchall()
    if not rows:
        return "📭"
    parts = []
    for r in rows:
        icon = _TYPE_ICON.get(r["type"], "📄")
        cnt = r["cnt"]
        parts.append(f"{icon}×{cnt}" if cnt > 1 else icon)
    return " ".join(parts)

def build_trending_text(page: int, page_size: int = 10) -> tuple:
    """يبني النص ولوحة التنقل للترند. يُرجع (text, markup)."""
    btns, total = get_trending_page(page, page_size)
    total_pages = max(1, (total + page_size - 1) // page_size)
    if not btns:
        text = "🔥 *الملفات الترند*\n\nلا توجد بيانات بعد.\nستظهر الأرقام بعد أن يبدأ المستخدمون بالضغط على الأزرار."
    else:
        start = page * page_size + 1
        lines = []
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        for i, b in enumerate(btns, start=start):
            rank = i
            icon = medals.get(rank, f"{rank}\\.")
            path = get_btn_path(b["id"])
            content_sum = _content_summary(b["id"])
            lines.append(f"{icon} {content_sum} `{b['click_count']}` طلب\n_📍 {path}_")
        text = f"🔥 *الملفات الترند* — صفحة {page+1}/{total_pages}\n\n" + "\n\n".join(lines)
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◀️ السابق", callback_data=f"st_trending_{page-1}"))
    if (page + 1) * page_size < total:
        nav.append(InlineKeyboardButton("التالي ▶️", callback_data=f"st_trending_{page+1}"))
    rows_kb = []
    if nav:
        rows_kb.append(nav)
    rows_kb.append([InlineKeyboardButton("رجوع", callback_data="st_back")])
    return text, InlineKeyboardMarkup(rows_kb)

def kb_cancel_inline():
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="cancel")]])

# ── امتحانات ───────────────────────────────────────────────────────────────

def add_exam_question(bid, q_type, q_text, q_file_id):
    with db() as c:
        count = c.execute("SELECT COUNT(*) FROM exam_questions WHERE button_id=?", (bid,)).fetchone()[0]
        cur = c.execute(
            "INSERT INTO exam_questions(button_id,q_type,q_text,q_file_id,ord) VALUES(?,?,?,?,?)",
            (bid, q_type, q_text, q_file_id, count + 1)
        )
        qid = cur.lastrowid
    return qid

def set_exam_answer(qid, a_type, a_text, a_file_id):
    with db() as c:
        c.execute(
            "UPDATE exam_questions SET a_type=?, a_text=?, a_file_id=? WHERE id=?",
            (a_type, a_text, a_file_id, qid)
        )

def get_exam_questions(bid):
    return [dict(r) for r in db().execute(
        "SELECT * FROM exam_questions WHERE button_id=? ORDER BY ord, id", (bid,)
    ).fetchall()]

def get_exam_question(qid):
    r = db().execute("SELECT * FROM exam_questions WHERE id=?", (qid,)).fetchone()
    return dict(r) if r else None

def del_exam_question(qid):
    with db() as c:
        c.execute("DELETE FROM exam_questions WHERE id=?", (qid,))

def toggle_random_exam(bid):
    b = get_btn(bid)
    if not b:
        return False
    current = b.get("random_exam", 0) or 0
    new_val = 0 if current else 1
    with db() as c:
        c.execute("UPDATE buttons SET random_exam=? WHERE id=?", (new_val, bid))
    return bool(new_val)

def kb_add_content_active(bid: int):
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ انتهاء الإضافة", callback_data=f"ci_add_done_{bid}")
    ]])
