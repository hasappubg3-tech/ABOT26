import logging
import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters
)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
DB = "data.db"

# ── حالات المحادثة ──────────────────────────────────────────────
MAIN, WAIT_LABEL, WAIT_CONTENT, WAIT_ADMIN_ID, WAIT_EDIT_LABEL, WAIT_EDIT_CONTENT = range(6)

TYPES = {"menu": "📂 قائمة", "text": "📝 نص", "photo": "🖼 صورة",
         "file": "📎 ملف", "video": "🎬 فيديو", "audio": "🎵 صوت"}
ICONS = {"menu": "📂", "text": "📝", "photo": "🖼", "file": "📎", "video": "🎬", "audio": "🎵"}

# أزرار الكيبورد السفلي
BTN_ADD    = "➕ إضافة زر"
BTN_MANAGE = "📋 إدارة الأزرار"
BTN_ADMINS = "👥 المشرفون"
ADMIN_BTNS = {BTN_ADD, BTN_MANAGE, BTN_ADMINS}

# ── قاعدة البيانات ───────────────────────────────────────────────
def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with db() as c:
        c.executescript("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY,
                username TEXT
            );
            CREATE TABLE IF NOT EXISTS buttons (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER REFERENCES buttons(id) ON DELETE CASCADE,
                type      TEXT NOT NULL,
                label     TEXT NOT NULL,
                content   TEXT,
                file_id   TEXT,
                ord       INTEGER DEFAULT 0
            );
        """)

def is_admin(uid): return db().execute("SELECT 1 FROM admins WHERE id=?", (uid,)).fetchone() is not None
def add_admin(uid, name=None):
    conn = db(); conn.execute("INSERT OR IGNORE INTO admins VALUES(?,?)", (uid, name)); conn.commit(); conn.close()
def del_admin(uid):
    conn = db(); conn.execute("DELETE FROM admins WHERE id=?", (uid,)); conn.commit(); conn.close()
def all_admins(): return [dict(r) for r in db().execute("SELECT * FROM admins").fetchall()]

def get_buttons(pid=None):
    q = "SELECT * FROM buttons WHERE parent_id IS NULL ORDER BY ord,id" if pid is None \
        else "SELECT * FROM buttons WHERE parent_id=? ORDER BY ord,id"
    return [dict(r) for r in (db().execute(q) if pid is None else db().execute(q, (pid,))).fetchall()]

def get_btn(bid):
    r = db().execute("SELECT * FROM buttons WHERE id=?", (bid,)).fetchone()
    return dict(r) if r else None

def add_btn(pid, t, label, content=None, file_id=None):
    conn = db(); cur = conn.cursor()
    q = "SELECT COALESCE(MAX(ord),0)+1 FROM buttons WHERE parent_id IS NULL" if pid is None \
        else "SELECT COALESCE(MAX(ord),0)+1 FROM buttons WHERE parent_id=?"
    n = (cur.execute(q) if pid is None else cur.execute(q, (pid,))).fetchone()[0]
    cur.execute("INSERT INTO buttons(parent_id,type,label,content,file_id,ord) VALUES(?,?,?,?,?,?)",
                (pid, t, label, content, file_id, n))
    conn.commit(); lid = cur.lastrowid; conn.close(); return lid

def upd_btn(bid, label=None, content=None, file_id=None):
    conn = db(); cur = conn.cursor()
    if label   is not None: cur.execute("UPDATE buttons SET label=?   WHERE id=?", (label,   bid))
    if content is not None: cur.execute("UPDATE buttons SET content=? WHERE id=?", (content, bid))
    if file_id is not None: cur.execute("UPDATE buttons SET file_id=? WHERE id=?", (file_id, bid))
    conn.commit(); conn.close()

def del_btn(bid):
    conn = db(); conn.execute("DELETE FROM buttons WHERE id=?", (bid,)); conn.commit(); conn.close()

def move_btn(bid, direction):
    conn = db(); cur = conn.cursor()
    row = dict(cur.execute("SELECT * FROM buttons WHERE id=?", (bid,)).fetchone())
    pid = row["parent_id"]
    q = "SELECT id FROM buttons WHERE parent_id IS NULL ORDER BY ord,id" if pid is None \
        else "SELECT id FROM buttons WHERE parent_id=? ORDER BY ord,id"
    ids = [r[0] for r in (cur.execute(q) if pid is None else cur.execute(q, (pid,))).fetchall()]
    i = ids.index(bid); j = i - 1 if direction == "up" else i + 1
    if not (0 <= j < len(ids)): conn.close(); return
    o1 = cur.execute("SELECT ord FROM buttons WHERE id=?", (bid,)).fetchone()[0]
    o2 = cur.execute("SELECT ord FROM buttons WHERE id=?", (ids[j],)).fetchone()[0]
    cur.execute("UPDATE buttons SET ord=? WHERE id=?", (o2, bid))
    cur.execute("UPDATE buttons SET ord=? WHERE id=?", (o1, ids[j]))
    conn.commit(); conn.close()

# ── مساعد لوحة التحكم (رسالة واحدة تُعدَّل) ─────────────────────
async def set_panel(ctx, chat_id, text, markup=None):
    panel_id = ctx.user_data.get("panel_id")
    if panel_id:
        try:
            await ctx.bot.edit_message_text(
                chat_id=chat_id, message_id=panel_id,
                text=text, reply_markup=markup, parse_mode="Markdown"
            )
            return
        except Exception:
            pass
    msg = await ctx.bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
    ctx.user_data["panel_id"] = msg.message_id

# ── لوحات المفاتيح ───────────────────────────────────────────────
def kb_user(pid=None):
    rows = []
    for b in get_buttons(pid):
        rows.append([InlineKeyboardButton(f"{ICONS.get(b['type'],'')} {b['label']}", callback_data=f"v_{b['id']}")])
    if pid is not None:
        parent = get_btn(pid)
        back = parent["parent_id"] if parent else None
        rows.append([InlineKeyboardButton("🔙 رجوع", callback_data="v_root" if back is None else f"v_{back}")])
    return InlineKeyboardMarkup(rows) if rows else None

def kb_admin_reply():
    return ReplyKeyboardMarkup([[BTN_ADD, BTN_MANAGE, BTN_ADMINS]], resize_keyboard=True)

def kb_admin_list(pid=None):
    rows = []
    for b in get_buttons(pid):
        rows.append([
            InlineKeyboardButton(f"{ICONS.get(b['type'],'')} {b['label']}", callback_data=f"a_edit_{b['id']}"),
            InlineKeyboardButton("⬆️", callback_data=f"a_up_{b['id']}"),
            InlineKeyboardButton("⬇️", callback_data=f"a_dn_{b['id']}"),
            InlineKeyboardButton("🗑", callback_data=f"a_del_{b['id']}"),
        ])
    ctx_str = "root" if pid is None else str(pid)
    rows.append([InlineKeyboardButton("➕ إضافة زر هنا", callback_data=f"a_add_{ctx_str}")])
    if pid is not None:
        parent = get_btn(pid)
        back_pid = parent["parent_id"] if parent else None
        rows.append([InlineKeyboardButton("🔙 رجوع", callback_data="a_list_root" if back_pid is None else f"a_list_{back_pid}")])
    return InlineKeyboardMarkup(rows)

def kb_types(ctx_str):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(v, callback_data=f"a_type_{k}_{ctx_str}")] for k, v in TYPES.items()]
        + [[InlineKeyboardButton("❌ إلغاء", callback_data="a_cancel")]]
    )

def kb_edit(bid):
    b = get_btn(bid)
    rows = []
    if b and b["type"] == "menu":
        rows.append([InlineKeyboardButton("📂 فتح القائمة", callback_data=f"a_list_{bid}")])
    rows += [
        [InlineKeyboardButton("✏️ تعديل الاسم",    callback_data=f"a_elabel_{bid}")],
        [InlineKeyboardButton("✏️ تعديل المحتوى", callback_data=f"a_econtent_{bid}")],
        [InlineKeyboardButton("🗑 حذف",             callback_data=f"a_del_{bid}")],
    ]
    pid = b["parent_id"] if b else None
    rows.append([InlineKeyboardButton("🔙 رجوع", callback_data="a_list_root" if pid is None else f"a_list_{pid}")])
    return InlineKeyboardMarkup(rows)

def kb_admins():
    rows = []
    for a in all_admins():
        name = a.get("username") or str(a["id"])
        rows.append([
            InlineKeyboardButton(f"👤 {name}", callback_data="noop"),
            InlineKeyboardButton("🗑 إزالة", callback_data=f"a_deladmin_{a['id']}"),
        ])
    rows += [
        [InlineKeyboardButton("➕ إضافة مشرف", callback_data="a_addadmin")],
    ]
    return InlineKeyboardMarkup(rows)

def kb_cancel():
    return InlineKeyboardMarkup([[InlineKeyboardButton("❌ إلغاء", callback_data="a_cancel")]])

# ── أوامر المستخدم ───────────────────────────────────────────────
async def cmd_start(update: Update, ctx):
    uid = update.effective_user.id
    if is_admin(uid):
        await update.message.reply_text("🔧 أدوات المشرف:", reply_markup=kb_admin_reply())
    btns = get_buttons()
    if not btns:
        await update.message.reply_text("👋 أهلاً! لا توجد أزرار متاحة حالياً.")
        return
    await update.message.reply_text("👋 أهلاً! اختر من القائمة:", reply_markup=kb_user())

async def cmd_myid(update: Update, ctx):
    u = update.effective_user
    await update.message.reply_text(f"🆔 معرّفك: `{u.id}`", parse_mode="Markdown")

async def cb_user(update: Update, ctx):
    q = update.callback_query; await q.answer()
    data = q.data
    if data == "v_root":
        kb = kb_user()
        if not kb:
            await q.edit_message_text("لا توجد أزرار."); return
        await q.edit_message_text("👋 القائمة الرئيسية:", reply_markup=kb); return

    bid = int(data[2:])
    b = get_btn(bid)
    if not b:
        await q.edit_message_text("❌ الزر غير موجود."); return

    pid = b["parent_id"]
    back_data = "v_root" if pid is None else f"v_{pid}"
    back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data=back_data)]])

    if b["type"] == "menu":
        sub = get_buttons(bid)
        kb = kb_user(bid)
        text = f"📂 *{b['label']}*\n\n" + ("اختر من القائمة:" if sub else "هذه القائمة فارغة.")
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb or back_kb)
    elif b["type"] == "text":
        await q.edit_message_text(f"📝 *{b['label']}*\n\n{b.get('content') or ''}",
                                  parse_mode="Markdown", reply_markup=back_kb)
    elif b["type"] == "photo" and b.get("file_id"):
        cap = f"🖼 *{b['label']}*" + (f"\n\n{b['content']}" if b.get("content") else "")
        await q.message.reply_photo(b["file_id"], caption=cap, parse_mode="Markdown", reply_markup=back_kb)
        await q.delete_message()
    elif b["type"] == "file" and b.get("file_id"):
        cap = f"📎 *{b['label']}*" + (f"\n\n{b['content']}" if b.get("content") else "")
        await q.message.reply_document(b["file_id"], caption=cap, parse_mode="Markdown", reply_markup=back_kb)
        await q.delete_message()
    elif b["type"] == "video" and b.get("file_id"):
        cap = f"🎬 *{b['label']}*" + (f"\n\n{b['content']}" if b.get("content") else "")
        await q.message.reply_video(b["file_id"], caption=cap, parse_mode="Markdown", reply_markup=back_kb)
        await q.delete_message()
    elif b["type"] == "audio" and b.get("file_id"):
        cap = f"🎵 *{b['label']}*" + (f"\n\n{b['content']}" if b.get("content") else "")
        await q.message.reply_audio(b["file_id"], caption=cap, parse_mode="Markdown", reply_markup=back_kb)
        await q.delete_message()
    else:
        await q.edit_message_text("❌ لا يوجد محتوى.", reply_markup=back_kb)

# ── معالج كيبورد المشرف (الأزرار السفلية) ───────────────────────
async def on_admin_kb(update: Update, ctx):
    uid = update.effective_user.id
    if not is_admin(uid): return ConversationHandler.END
    text = update.message.text
    chat_id = update.effective_chat.id

    if text == BTN_ADD:
        ctx.user_data["pctx"] = "root"
        await set_panel(ctx, chat_id, "➕ اختر نوع الزر:", kb_types("root"))
        return MAIN

    if text == BTN_MANAGE:
        await set_panel(ctx, chat_id, "📋 *إدارة الأزرار* — القائمة الرئيسية:", kb_admin_list())
        return MAIN

    if text == BTN_ADMINS:
        await set_panel(ctx, chat_id, f"👥 *المشرفون* ({len(all_admins())}):", kb_admins())
        return MAIN

    return ConversationHandler.END

# ── معالج أزرار لوحة التحكم (Inline) ────────────────────────────
async def cb_admin(update: Update, ctx):
    q = update.callback_query; await q.answer()
    uid = q.from_user.id
    if not is_admin(uid):
        await q.edit_message_text("❌ ليس لديك صلاحية."); return ConversationHandler.END
    d = q.data
    chat_id = q.message.chat_id
    ctx.user_data["panel_id"] = q.message.message_id

    if d == "a_cancel":
        ctx.user_data.clear()
        await q.edit_message_text("✅ تم الإلغاء."); return ConversationHandler.END

    if d == "a_list_root":
        await q.edit_message_text("📋 *إدارة الأزرار* — القائمة الرئيسية:",
                                  parse_mode="Markdown", reply_markup=kb_admin_list()); return MAIN

    if d.startswith("a_list_"):
        pid = int(d[7:])
        b = get_btn(pid)
        await q.edit_message_text(f"📂 *{b['label']}*", parse_mode="Markdown",
                                  reply_markup=kb_admin_list(pid)); return MAIN

    if d.startswith("a_edit_"):
        bid = int(d[7:])
        b = get_btn(bid)
        text = f"*{b['label']}*  —  {ICONS.get(b['type'],'')} {b['type']}"
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=kb_edit(bid)); return MAIN

    if d.startswith("a_up_") or d.startswith("a_dn_"):
        up = d.startswith("a_up_")
        bid = int(d[5:])
        move_btn(bid, "up" if up else "down")
        b = get_btn(bid)
        await q.edit_message_reply_markup(reply_markup=kb_admin_list(b["parent_id"])); return MAIN

    if d.startswith("a_del_"):
        bid = int(d[6:])
        b = get_btn(bid); pid = b["parent_id"] if b else None
        del_btn(bid)
        await q.edit_message_text("📋 *إدارة الأزرار*:", parse_mode="Markdown",
                                  reply_markup=kb_admin_list(pid)); return MAIN

    if d.startswith("a_add_"):
        pctx = d[6:]
        ctx.user_data["pctx"] = pctx
        await q.edit_message_text("➕ اختر نوع الزر:", reply_markup=kb_types(pctx)); return MAIN

    if d.startswith("a_type_"):
        rest = d[7:]; t, pctx = rest.split("_", 1)
        ctx.user_data["type"] = t; ctx.user_data["pctx"] = pctx
        await q.edit_message_text(f"✏️ اكتب اسم الزر وأرسله:", reply_markup=kb_cancel())
        return WAIT_LABEL

    if d == "a_admins":
        await q.edit_message_text(f"👥 *المشرفون* ({len(all_admins())}):",
                                  parse_mode="Markdown", reply_markup=kb_admins()); return MAIN

    if d == "a_addadmin":
        await q.edit_message_text("👤 أرسل معرّف المستخدم (ID):", reply_markup=kb_cancel())
        return WAIT_ADMIN_ID

    if d.startswith("a_deladmin_"):
        tid = int(d[11:])
        if tid == uid: await q.answer("❌ لا يمكنك إزالة نفسك!", show_alert=True); return MAIN
        del_admin(tid)
        await q.edit_message_text(f"👥 *المشرفون* ({len(all_admins())}):",
                                  parse_mode="Markdown", reply_markup=kb_admins()); return MAIN

    if d.startswith("a_elabel_"):
        bid = int(d[9:]); ctx.user_data["bid"] = bid
        b = get_btn(bid)
        await q.edit_message_text(f"✏️ الاسم الحالي: *{b['label']}*\n\nاكتب الاسم الجديد وأرسله:",
                                  parse_mode="Markdown", reply_markup=kb_cancel()); return WAIT_EDIT_LABEL

    if d.startswith("a_econtent_"):
        bid = int(d[11:]); b = get_btn(bid)
        if b["type"] == "menu":
            await q.answer("القوائم لا تحتوي محتوى مباشر.", show_alert=True); return MAIN
        ctx.user_data["bid"] = bid; ctx.user_data["type"] = b["type"]
        await q.edit_message_text("✏️ أرسل المحتوى الجديد:", reply_markup=kb_cancel())
        return WAIT_EDIT_CONTENT

    if d == "noop": return MAIN
    return MAIN

# ── معالجات الإدخال النصي ────────────────────────────────────────
async def on_label(update: Update, ctx):
    if not is_admin(update.effective_user.id): return ConversationHandler.END
    label = update.message.text.strip()
    t = ctx.user_data.get("type"); pctx = ctx.user_data.get("pctx")
    pid = None if pctx == "root" else int(pctx)
    chat_id = update.effective_chat.id

    if t == "menu":
        add_btn(pid, "menu", label)
        ctx.user_data.clear()
        await set_panel(ctx, chat_id, f"✅ تم إنشاء القائمة *{label}*", kb_admin_list(pid))
        return MAIN

    ctx.user_data["label"] = label
    await set_panel(ctx, chat_id, f"📤 أرسل محتوى الزر *{label}*:", kb_cancel())
    return WAIT_CONTENT

async def on_content(update: Update, ctx):
    if not is_admin(update.effective_user.id): return ConversationHandler.END
    t = ctx.user_data.get("type"); label = ctx.user_data.get("label", "زر")
    pctx = ctx.user_data.get("pctx"); pid = None if pctx == "root" else int(pctx)
    m = update.message; content = None; fid = None

    if t == "text": content = m.text
    elif t == "photo" and m.photo: fid = m.photo[-1].file_id; content = m.caption
    elif t == "file" and m.document: fid = m.document.file_id; content = m.caption
    elif t == "video" and m.video: fid = m.video.file_id; content = m.caption
    elif t == "audio" and (m.audio or m.voice): fid = (m.audio or m.voice).file_id; content = m.caption
    else:
        await set_panel(ctx, update.effective_chat.id, "❌ نوع المحتوى غير صحيح. أعد الإرسال:", kb_cancel())
        return WAIT_CONTENT

    add_btn(pid, t, label, content, fid)
    ctx.user_data.clear()
    await set_panel(ctx, update.effective_chat.id, f"✅ تم إضافة *{label}*", kb_admin_list(pid))
    return MAIN

async def on_admin_id(update: Update, ctx):
    if not is_admin(update.effective_user.id): return ConversationHandler.END
    try:
        tid = int(update.message.text.strip())
    except ValueError:
        await set_panel(ctx, update.effective_chat.id, "❌ أرسل رقماً صحيحاً:", kb_cancel())
        return WAIT_ADMIN_ID
    add_admin(tid)
    ctx.user_data.clear()
    await set_panel(ctx, update.effective_chat.id, f"✅ تمت الإضافة.\n\n👥 *المشرفون* ({len(all_admins())}):", kb_admins())
    return MAIN

async def on_edit_label(update: Update, ctx):
    if not is_admin(update.effective_user.id): return ConversationHandler.END
    bid = ctx.user_data.get("bid"); label = update.message.text.strip()
    upd_btn(bid, label=label)
    b = get_btn(bid); pid = b["parent_id"] if b else None
    ctx.user_data.clear()
    await set_panel(ctx, update.effective_chat.id, f"✅ تم تحديث الاسم إلى *{label}*", kb_admin_list(pid))
    return MAIN

async def on_edit_content(update: Update, ctx):
    if not is_admin(update.effective_user.id): return ConversationHandler.END
    bid = ctx.user_data.get("bid"); t = ctx.user_data.get("type")
    m = update.message; content = None; fid = None

    if t == "text": content = m.text
    elif t == "photo" and m.photo: fid = m.photo[-1].file_id; content = m.caption
    elif t == "file" and m.document: fid = m.document.file_id; content = m.caption
    elif t == "video" and m.video: fid = m.video.file_id; content = m.caption
    elif t == "audio" and (m.audio or m.voice): fid = (m.audio or m.voice).file_id; content = m.caption
    else:
        await set_panel(ctx, update.effective_chat.id, "❌ نوع المحتوى غير صحيح. أعد الإرسال:", kb_cancel())
        return WAIT_EDIT_CONTENT

    upd_btn(bid, content=content, file_id=fid)
    b = get_btn(bid); pid = b["parent_id"] if b else None
    ctx.user_data.clear()
    await set_panel(ctx, update.effective_chat.id, "✅ تم تحديث المحتوى.", kb_admin_list(pid))
    return MAIN

# ── إعداد البوت ─────────────────────────────────────────────────
async def post_init(app):
    sid = os.environ.get("SUPER_ADMIN_ID", "").strip()
    if sid.isdigit() and not is_admin(int(sid)):
        add_admin(int(sid)); logging.info(f"Super admin {sid} added.")

def main():
    if not BOT_TOKEN:
        logging.error("TELEGRAM_BOT_TOKEN غير موجود!"); return
    init_db()
    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    admin_kb_filter = filters.Text(ADMIN_BTNS)
    media_filter = filters.TEXT | filters.PHOTO | filters.Document.ALL | filters.VIDEO | filters.AUDIO | filters.VOICE

    admin_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(cb_admin, pattern="^a_"),
            MessageHandler(admin_kb_filter, on_admin_kb),
        ],
        states={
            MAIN: [
                CallbackQueryHandler(cb_admin, pattern="^a_"),
                MessageHandler(admin_kb_filter, on_admin_kb),
            ],
            WAIT_LABEL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND & ~admin_kb_filter, on_label),
                MessageHandler(admin_kb_filter, on_admin_kb),
                CallbackQueryHandler(cb_admin, pattern="^a_cancel"),
            ],
            WAIT_CONTENT: [
                MessageHandler(media_filter & ~filters.COMMAND & ~admin_kb_filter, on_content),
                MessageHandler(admin_kb_filter, on_admin_kb),
                CallbackQueryHandler(cb_admin, pattern="^a_cancel"),
            ],
            WAIT_ADMIN_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND & ~admin_kb_filter, on_admin_id),
                MessageHandler(admin_kb_filter, on_admin_kb),
                CallbackQueryHandler(cb_admin, pattern="^a_cancel"),
            ],
            WAIT_EDIT_LABEL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND & ~admin_kb_filter, on_edit_label),
                MessageHandler(admin_kb_filter, on_admin_kb),
                CallbackQueryHandler(cb_admin, pattern="^a_cancel"),
            ],
            WAIT_EDIT_CONTENT: [
                MessageHandler(media_filter & ~filters.COMMAND & ~admin_kb_filter, on_edit_content),
                MessageHandler(admin_kb_filter, on_admin_kb),
                CallbackQueryHandler(cb_admin, pattern="^a_cancel"),
            ],
        },
        fallbacks=[
            MessageHandler(admin_kb_filter, on_admin_kb),
            CallbackQueryHandler(cb_admin, pattern="^a_cancel"),
        ],
        per_message=False,
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("myid", cmd_myid))
    app.add_handler(admin_conv)
    app.add_handler(CallbackQueryHandler(cb_user, pattern="^v_"))

    logging.info("البوت يعمل...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
