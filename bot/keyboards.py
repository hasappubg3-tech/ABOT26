from .shared import *

def build_kb(uid, pid=None):
    btns = get_buttons(pid)
    admin = is_admin(uid)
    rows = []
    current_row = []
    last_bid_in_row = None
    for i, b in enumerate(btns):
        if i > 0 and b.get('new_row', 1):
            if current_row:
                if admin and last_bid_in_row is not None:
                    current_row.append(KeyboardButton(_plus_label(last_bid_in_row)))
                rows.append(current_row)
            current_row = []
        current_row.append(KeyboardButton(b['label'] + _encode_bid(b['id'])))
        last_bid_in_row = b['id']
    if current_row:
        if admin and last_bid_in_row is not None:
            current_row.append(KeyboardButton(_plus_label(last_bid_in_row)))
        rows.append(current_row)
    if admin and not btns:
        rows.append([KeyboardButton(BTN_PLUS)])
    if admin:
        rows.append([KeyboardButton(BTN_ADD)])
    if pid is not None:
        rows.append([KeyboardButton(BTN_BACK), KeyboardButton(BTN_HOME)])
    if admin:
        rows.append([KeyboardButton(BTN_SETTINGS)])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True) if (rows or admin) else None

def is_bot_button_text(text: str, pid=None) -> bool:
    if not text:
        return False
    text = _strip_bid_markers(text)
    if text in SPECIAL_BTNS or _parse_plus(text) is not None:
        return True
    return any(b["label"] == text for b in get_buttons(pid))

# ── لوحات Inline ─────────────────────────────────────────────────
def kb_manage(pid=None):
    ctx = "r" if pid is None else str(pid)
    rows = []
    btns = get_buttons(pid)
    for b in btns:
        rows.append([
            InlineKeyboardButton(b['label'], callback_data=f"e_{b['id']}"),
            InlineKeyboardButton("🗑", callback_data=f"confirm_x_{b['id']}"),
            InlineKeyboardButton("➕", callback_data=f"plus_{b['id']}"),
        ])
    rows.append([InlineKeyboardButton("➕ إضافة", callback_data=f"plus_e_{ctx}")])
    if len(btns) >= 2:
        rows.append([InlineKeyboardButton("🔀 تبديل موضع زرين", callback_data=f"swp_start_{ctx}")])
    if pid is not None:
        b = get_btn(pid); back = b["parent_id"] if b else None
        rows.append([InlineKeyboardButton("رجوع", callback_data="m_r" if back is None else f"m_{back}")])
    return InlineKeyboardMarkup(rows)

def kb_add_position(after_bid):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬆️ فوقه (صف جديد)",      callback_data=f"pladd_above_{after_bid}")],
        [InlineKeyboardButton("➡️ بجانبه (نفس السطر)",  callback_data=f"pladd_same_{after_bid}")],
        [InlineKeyboardButton("⬇️ تحته (سطر جديد)",     callback_data=f"pladd_new_{after_bid}")],
        [InlineKeyboardButton("❌ إلغاء",                callback_data="pt_cancel")],
    ])

def kb_add_where(pid):
    """يُعرض عند BTN_ADD ليختار المشرف الموضع أولاً."""
    btns = get_buttons(pid)
    if not btns:
        return None  # لا حاجة للسؤال إذا لم تكن هناك أزرار
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬆️ في أعلى القائمة (صف جديد أول)", callback_data="pt_addtop")],
        [InlineKeyboardButton("⬇️ في أسفل القائمة (نهاية القائمة)", callback_data="pt_addbottom")],
        [InlineKeyboardButton("❌ إلغاء", callback_data="pt_cancel")],
    ])

# ── كويز: دوال الكيبورد ───────────────────────────────────────────
def kb_quiz_panel(bid):
    b = get_btn(bid)
    questions = get_quiz_questions(bid)
    random_q = (b.get("random_quiz", 0) or 0) if b else 0
    rows = []
    if questions:
        rows.append([InlineKeyboardButton(f"📋 الأسئلة ({len(questions)})", callback_data=f"qz_list_{bid}")])
    rows.append([InlineKeyboardButton("➕ إضافة سؤال", callback_data=f"qz_add_{bid}")])
    rand_label = "🔀 إلغاء التوزيع العشوائي" if random_q else "🔀 تفعيل التوزيع العشوائي"
    rows.append([InlineKeyboardButton(rand_label, callback_data=f"qz_toggle_rand_{bid}")])
    rows.append([InlineKeyboardButton("✏️ تغيير الاسم", callback_data=f"el_{bid}")])
    rows.append([InlineKeyboardButton("🗑 حذف الزر", callback_data=f"confirm_x_{bid}")])
    pid = b["parent_id"] if b else None
    rows.append([InlineKeyboardButton("رجوع", callback_data="m_r" if pid is None else f"m_{pid}")])
    return InlineKeyboardMarkup(rows)

def kb_quiz_quick(bid):
    b = get_btn(bid)
    questions = get_quiz_questions(bid)
    random_q = (b.get("random_quiz", 0) or 0) if b else 0
    rows = []
    if questions:
        rows.append([InlineKeyboardButton(f"📋 الأسئلة ({len(questions)})", callback_data=f"qz_list_{bid}")])
    rows.append([InlineKeyboardButton("➕ إضافة سؤال", callback_data=f"qz_add_{bid}")])
    rand_label = "🔀 إلغاء التوزيع العشوائي" if random_q else "🔀 تفعيل التوزيع العشوائي"
    rows.append([InlineKeyboardButton(rand_label, callback_data=f"qz_toggle_rand_{bid}")])
    rows.append([InlineKeyboardButton("✏️ تغيير الاسم", callback_data=f"el_{bid}")])
    rows.append([InlineKeyboardButton("🗑 حذف", callback_data=f"confirm_x_{bid}")])
    return InlineKeyboardMarkup(rows)

def kb_quiz_question_list(bid):
    questions = get_quiz_questions(bid)
    rows = []
    for q in questions:
        opts = get_quiz_options(q["id"])
        status = "✅" if len(opts) >= 2 else "⚠️"
        rows.append([InlineKeyboardButton(
            f"{status} {q['question'][:35]}", callback_data=f"qz_q_{q['id']}"
        )])
    rows.append([InlineKeyboardButton("➕ إضافة سؤال", callback_data=f"qz_add_{bid}")])
    rows.append([InlineKeyboardButton("رجوع", callback_data=f"qz_panel_{bid}")])
    return InlineKeyboardMarkup(rows)

def kb_quiz_question_manage(qid):
    q = get_quiz_question(qid)
    if not q: return InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="noop")]])
    opts = get_quiz_options(qid)
    rows = []
    for i, opt in enumerate(opts):
        is_correct = (i == q["correct_option"])
        icon = "✅" if is_correct else "◯"
        rows.append([
            InlineKeyboardButton(f"{icon} {opt['text'][:25]}", callback_data=f"qz_setcorrect_{qid}_{i}"),
            InlineKeyboardButton("🗑", callback_data=f"qz_delopt_{opt['id']}_{qid}"),
        ])
    rows.append([InlineKeyboardButton("➕ إضافة خيار", callback_data=f"qz_addopt_{qid}")])
    rows.append([InlineKeyboardButton("🗑 حذف السؤال", callback_data=f"qz_delq_{qid}")])
    rows.append([InlineKeyboardButton("رجوع", callback_data=f"qz_list_{q['button_id']}")])
    return InlineKeyboardMarkup(rows)

def kb_add_type():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📂 قائمة", callback_data="pt_m"),
            InlineKeyboardButton("📄 محتوى", callback_data="pt_c"),
        ],
        [
            InlineKeyboardButton("📊 كويز", callback_data="pt_q"),
            InlineKeyboardButton("📝 اختبار", callback_data="pt_e"),
        ],
        [
            InlineKeyboardButton("🎓 زر امتحان", callback_data="pt_g"),
        ],
        [
            InlineKeyboardButton("⭐ مميز (للمشرفين فقط)", callback_data="pt_s"),
        ],
        [
            InlineKeyboardButton("❌ إلغاء", callback_data="pt_cancel"),
        ],
    ])

def kb_exam_panel(bid):
    b = get_btn(bid)
    questions = get_exam_questions(bid)
    random_e = (b.get("random_exam", 0) or 0) if b else 0
    rows = []
    if questions:
        rows.append([InlineKeyboardButton(f"📋 الأسئلة ({len(questions)})", callback_data=f"ex_list_{bid}")])
    rows.append([InlineKeyboardButton("➕ إضافة سؤال", callback_data=f"ex_add_{bid}")])
    rand_label = "🔀 إلغاء التوزيع العشوائي" if random_e else "🔀 تفعيل التوزيع العشوائي"
    rows.append([InlineKeyboardButton(rand_label, callback_data=f"ex_toggle_rand_{bid}")])
    rows.append([InlineKeyboardButton("✏️ تغيير الاسم", callback_data=f"el_{bid}")])
    rows.append([InlineKeyboardButton("🗑 حذف الزر", callback_data=f"confirm_x_{bid}")])
    pid = b["parent_id"] if b else None
    rows.append([InlineKeyboardButton("رجوع", callback_data="m_r" if pid is None else f"m_{pid}")])
    return InlineKeyboardMarkup(rows)

def kb_exam_quick(bid):
    b = get_btn(bid)
    questions = get_exam_questions(bid)
    random_e = (b.get("random_exam", 0) or 0) if b else 0
    rows = []
    if questions:
        rows.append([InlineKeyboardButton(f"📋 الأسئلة ({len(questions)})", callback_data=f"ex_list_{bid}")])
    rows.append([InlineKeyboardButton("➕ إضافة سؤال", callback_data=f"ex_add_{bid}")])
    rand_label = "🔀 إلغاء التوزيع العشوائي" if random_e else "🔀 تفعيل التوزيع العشوائي"
    rows.append([InlineKeyboardButton(rand_label, callback_data=f"ex_toggle_rand_{bid}")])
    rows.append([InlineKeyboardButton("✏️ تغيير الاسم", callback_data=f"el_{bid}")])
    rows.append([InlineKeyboardButton("🗑 حذف", callback_data=f"confirm_x_{bid}")])
    return InlineKeyboardMarkup(rows)

def exam_group_text(bid, uid):
    b = get_btn(bid)
    s = exam_group_summary(uid, bid)
    degree = round(((s.get("correct") or 0) / (s.get("total_questions") or 1)) * 100) if s.get("total_questions") else 0
    return (
        f"🎓 *{b['label'] if b else 'زر الامتحان'}*\n\n"
        f"📚 المواضيع: *{s['completed_topics']}/{s['total_topics']}*\n"
        f"🧩 الأسئلة المجابة: *{s['answered']}/{s['total_questions']}*\n"
        f"✅ صحيحة: *{s['correct']}* | ❌ خاطئة: *{s['wrong']}*\n"
        f"🏅 درجتي العامة: *{degree}/100*\n"
        f"📈 الإنجاز: *{s['percent']}%*\n\n"
        "ابدأ بالموضوع الأول، وبعد إكماله ينفتح الموضوع التالي."
    )

def exam_score(correct, total):
    return round(((correct or 0) / total) * 100) if total else 0

def exam_group_stats_text(bid, uid):
    b = get_btn(bid)
    topics = get_exam_topics(bid)
    s = exam_group_summary(uid, bid)
    overall_degree = exam_score(s.get("correct") or 0, s.get("total_questions") or 0)
    lines = [
        f"📊 *إحصائيات الامتحانات: {b['label'] if b else 'زر الامتحان'}*",
        "",
        f"🏅 درجتي العامة: *{overall_degree}/100*",
        f"📚 الامتحانات المكتملة: *{s['completed_topics']}/{s['total_topics']}*",
        f"🧩 الأسئلة المجابة: *{s['answered']}/{s['total_questions']}*",
        f"✅ صحيحة: *{s['correct']}* | ❌ خاطئة: *{s['wrong']}*",
        "",
        "📋 *درجاتي لكل امتحان:*",
    ]
    if not topics:
        lines.append("📭 لا توجد امتحانات بعد.")
        return "\n".join(lines)
    for i, topic in enumerate(topics, start=1):
        questions_count = len(get_exam_questions(topic["id"]))
        progress = get_exam_progress(uid, topic["id"])
        total = questions_count or (progress.get("total") or 0)
        answered = progress.get("answered") or 0
        correct = progress.get("correct") or 0
        wrong = progress.get("wrong") or 0
        degree = exam_score(correct, total)
        status = "✅ مكتمل" if progress.get("completed") else "⏳ غير مكتمل"
        lines.append(
            f"\n{i}. *{topic['label']}* — {status}\n"
            f"   🏅 درجتي: *{degree}/100*\n"
            f"   🧩 المجابة: *{answered}/{total}* | ✅ *{correct}* | ❌ *{wrong}*"
        )
    lines.append("\nملاحظة: يمكن تعديل درجتك خلال إعادة الامتحان.")
    return "\n".join(lines)

def build_exam_group_kb(uid, parent_bid):
    """كيبورد ثابت يظهر للمستخدم عند الدخول لزر امتحان رئيسي."""
    topics = get_exam_topics(parent_bid)
    rows = [[KeyboardButton(BTN_EXAM_STATS)]]
    for topic in topics:
        rows.append([KeyboardButton(topic['label'] + _encode_bid(topic['id']))])
    rows.append([KeyboardButton(BTN_BACK), KeyboardButton(BTN_HOME)])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)

def kb_exam_group_user(bid, uid):
    rows = []
    topics = get_exam_topics(bid)
    for topic in topics:
        progress = get_exam_progress(uid, topic["id"])
        unlocked = is_exam_topic_unlocked(uid, bid, topic["id"])
        status = "✅" if progress.get("completed") else ("🔓" if unlocked else "🔒")
        q_count = len(get_exam_questions(topic["id"]))
        label = f"{status} {topic['label']} ({progress.get('answered') or 0}/{q_count})"
        cb = f"exg_topic_{bid}_{topic['id']}" if unlocked else "noop"
        rows.append([InlineKeyboardButton(label, callback_data=cb)])
    if not rows:
        rows.append([InlineKeyboardButton("📭 لا توجد مواضيع بعد", callback_data="noop")])
    return InlineKeyboardMarkup(rows)

def kb_exam_group_quick(bid):
    b = get_btn(bid)
    topics = get_exam_topics(bid)
    rows = [
        [InlineKeyboardButton(f"📂 إدارة المواضيع ({len(topics)})", callback_data=f"exg_manage_{bid}")],
        [InlineKeyboardButton("✏️ تغيير الاسم", callback_data=f"el_{bid}")],
        [InlineKeyboardButton("🗑 حذف", callback_data=f"confirm_x_{bid}")],
    ]
    pid = b["parent_id"] if b else None
    rows.append([InlineKeyboardButton("رجوع", callback_data="m_r" if pid is None else f"m_{pid}")])
    return InlineKeyboardMarkup(rows)

def kb_exam_group_manage(bid):
    """لوحة إدارة مواضيع زر الامتحان الرئيسي — خاصة بالمشرف."""
    b = get_btn(bid)
    topics = get_exam_topics(bid)
    rows = []
    for topic in topics:
        q_count = len(get_exam_questions(topic["id"]))
        rows.append([
            InlineKeyboardButton(f"📝 {topic['label']} ({q_count} سؤال)", callback_data=f"e_{topic['id']}"),
            InlineKeyboardButton("🗑", callback_data=f"confirm_x_{topic['id']}"),
        ])
    if not rows:
        rows.append([InlineKeyboardButton("📭 لا توجد مواضيع بعد", callback_data="noop")])
    rows.append([InlineKeyboardButton("➕ إضافة موضوع جديد", callback_data=f"exg_add_topic_{bid}")])
    rows.append([InlineKeyboardButton("✏️ تغيير اسم زر الامتحان", callback_data=f"el_{bid}")])
    rows.append([InlineKeyboardButton("🗑 حذف زر الامتحان", callback_data=f"confirm_x_{bid}")])
    pid = b["parent_id"] if b else None
    rows.append([InlineKeyboardButton("رجوع", callback_data="m_r" if pid is None else f"m_{pid}")])
    return InlineKeyboardMarkup(rows)

def kb_exam_question_list(bid):
    questions = get_exam_questions(bid)
    rows = []
    for i, q in enumerate(questions, start=1):
        has_answer = bool(q.get("a_text") or q.get("a_file_id"))
        status = "✅" if has_answer else "⚠️"
        label = q.get("q_text") or f"سؤال {i} [{q.get('q_type','text')}]"
        rows.append([InlineKeyboardButton(
            f"{status} {label[:35]}", callback_data=f"ex_q_{q['id']}"
        )])
    rows.append([InlineKeyboardButton("➕ إضافة سؤال", callback_data=f"ex_add_{bid}")])
    rows.append([InlineKeyboardButton("رجوع", callback_data=f"ex_panel_{bid}")])
    return InlineKeyboardMarkup(rows)

def kb_exam_question_manage(qid):
    q = get_exam_question(qid)
    if not q:
        return InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="noop")]])
    bid = q["button_id"]
    rows = [
        [InlineKeyboardButton("✏️ تعديل السؤال", callback_data=f"ex_edit_q_{qid}")],
        [InlineKeyboardButton("✏️ تعديل الجواب", callback_data=f"ex_edit_a_{qid}")],
        [InlineKeyboardButton("🗑 حذف السؤال", callback_data=f"ex_delq_{qid}")],
        [InlineKeyboardButton("رجوع", callback_data=f"ex_list_{bid}")],
    ]
    return InlineKeyboardMarkup(rows)

def kb_swap_select(pid=None, first_bid=None):
    """لوحة اختيار الزر للتبديل — بنفس تخطيط الأزرار الأصلي."""
    btns = get_buttons(pid)
    rows = []
    current_row = []
    for i, b in enumerate(btns):
        if i > 0 and b.get('new_row', 1) and current_row:
            rows.append(current_row)
            current_row = []
        if first_bid is None:
            current_row.append(InlineKeyboardButton(b['label'], callback_data=f"swp1_{b['id']}"))
        elif b['id'] == first_bid:
            current_row.append(InlineKeyboardButton(f"✅ {b['label']}", callback_data="noop"))
        else:
            current_row.append(InlineKeyboardButton(b['label'], callback_data=f"swp2_{first_bid}_{b['id']}"))
    if current_row:
        rows.append(current_row)
    rows.append([InlineKeyboardButton("❌ إلغاء", callback_data="m_r" if pid is None else f"m_{pid}")])
    return InlineKeyboardMarkup(rows)

def kb_edit_menu_btn(bid):
    b = get_btn(bid)
    rows = [
        [InlineKeyboardButton("📂 فتح القائمة", callback_data=f"m_{bid}")],
        [InlineKeyboardButton("✏️ تغيير الاسم", callback_data=f"el_{bid}")],
        [InlineKeyboardButton("🗑 حذف",          callback_data=f"confirm_x_{bid}")],
    ]
    pid = b["parent_id"] if b else None
    rows.append([InlineKeyboardButton("رجوع", callback_data="m_r" if pid is None else f"m_{pid}")])
    return InlineKeyboardMarkup(rows)

def kb_content_panel(bid):
    """لوحة إدارة محتوى الزر (كاملة)."""
    items = get_items(bid)
    b = get_btn(bid)
    rows = []
    if items:
        rows.append([InlineKeyboardButton("👁 عرض المحتوى", callback_data=f"ci_view_{bid}")])
    rows.append([InlineKeyboardButton("➕ إضافة محتوى", callback_data=f"ci_add_{bid}")])
    global_cap = get_global_caption()
    if global_cap:
        no_cap = (b.get("no_caption", 0) or 0) if b else 0
        cap_label = "✅ تفعيل كليشة الكلام" if no_cap else "🚫 إلغاء كليشة الكلام"
        rows.append([InlineKeyboardButton(cap_label, callback_data=f"ci_toggle_cap_{bid}")])
    cap_btns = get_caption_buttons()
    if cap_btns:
        no_btn_cap = (b.get("no_btn_caption", 0) or 0) if b else 0
        btn_cap_label = "✅ تفعيل كليشة الأزرار" if no_btn_cap else "🚫 إلغاء كليشة الأزرار"
        rows.append([InlineKeyboardButton(btn_cap_label, callback_data=f"ci_toggle_btn_cap_{bid}")])
    unified = (b.get("unified_rating", 0) or 0) if b else 0
    unified_label = "🔀 إلغاء توحيد التقييم" if unified else "⭐ توحيد التقييم"
    rows.append([InlineKeyboardButton(unified_label, callback_data=f"ci_toggle_urating_{bid}")])
    rows.append([InlineKeyboardButton("✏️ تغيير الاسم", callback_data=f"el_{bid}")])
    rows.append([InlineKeyboardButton("🗑 حذف الزر",    callback_data=f"confirm_x_{bid}")])
    pid = b["parent_id"] if b else None
    rows.append([InlineKeyboardButton("رجوع", callback_data="m_r" if pid is None else f"m_{pid}")])
    return InlineKeyboardMarkup(rows)

def kb_menu_quick(bid):
    """خيارات سريعة لزر قائمة عند الضغط من الكيبورد — بدون إضافة أو رجوع."""
    b = get_btn(bid)
    pid = b["parent_id"] if b else None
    siblings = get_buttons(pid)
    rows = [
        [InlineKeyboardButton("✏️ تغيير الاسم", callback_data=f"el_{bid}")],
        [InlineKeyboardButton("🗑 حذف",          callback_data=f"confirm_x_{bid}")],
    ]
    if len(siblings) >= 2:
        rows.append([InlineKeyboardButton("🔀 تبديل الموضع", callback_data=f"swp_start_{'r' if pid is None else str(pid)}")])
    return InlineKeyboardMarkup(rows)

def kb_content_quick(bid):
    """خيارات سريعة لزر محتوى عند الضغط من الكيبورد — بدون رجوع."""
    items = get_items(bid)
    b = get_btn(bid)
    rows = []
    if items:
        rows.append([InlineKeyboardButton("👁 عرض المحتوى", callback_data=f"ci_view_{bid}")])
    rows.append([InlineKeyboardButton("➕ إضافة محتوى", callback_data=f"ci_add_{bid}")])
    global_cap = get_global_caption()
    if global_cap:
        no_cap = (b.get("no_caption", 0) or 0) if b else 0
        cap_label = "✅ تفعيل كليشة الكلام" if no_cap else "🚫 إلغاء كليشة الكلام"
        rows.append([InlineKeyboardButton(cap_label, callback_data=f"ci_toggle_cap_{bid}")])
    cap_btns = get_caption_buttons()
    if cap_btns:
        no_btn_cap = (b.get("no_btn_caption", 0) or 0) if b else 0
        btn_cap_label = "✅ تفعيل كليشة الأزرار" if no_btn_cap else "🚫 إلغاء كليشة الأزرار"
        rows.append([InlineKeyboardButton(btn_cap_label, callback_data=f"ci_toggle_btn_cap_{bid}")])
    unified = (b.get("unified_rating", 0) or 0) if b else 0
    unified_label = "🔀 إلغاء توحيد التقييم" if unified else "⭐ توحيد التقييم"
    rows.append([InlineKeyboardButton(unified_label, callback_data=f"ci_toggle_urating_{bid}")])
    rows.append([InlineKeyboardButton("✏️ تغيير الاسم", callback_data=f"el_{bid}")])
    rows.append([InlineKeyboardButton("🗑 حذف",          callback_data=f"confirm_x_{bid}")])
    return InlineKeyboardMarkup(rows)

def kb_special_quick(bid):
    """خيارات سريعة لزر مميز عند ضغط الأدمن عليه من الكيبورد."""
    b = get_btn(bid)
    rows = [
        [InlineKeyboardButton("✏️ تغيير الاسم", callback_data=f"el_{bid}")],
        [InlineKeyboardButton("🗑 حذف",          callback_data=f"confirm_x_{bid}")],
    ]
    if b and b.get("special_action") in ("file_request", "file_upload"):
        rows.insert(0, [InlineKeyboardButton("👥 مشرفين الملفات", callback_data=f"fr_admins_{bid}")])
    if b and b.get("special_action") == "file_upload":
        rows.insert(1, [InlineKeyboardButton("✏️ تعديل رسالة الشكر", callback_data=f"fu_thanks_set_{bid}")])
    return InlineKeyboardMarkup(rows)

def kb_file_request_admins(bid):
    admins = get_file_request_admins()
    rows = []
    for a in admins:
        name = a.get("username") or str(a["user_id"])
        rows.append([
            InlineKeyboardButton(f"👤 {name}", callback_data="noop"),
            InlineKeyboardButton("🗑", callback_data=f"fr_admin_del_{bid}_{a['user_id']}")
        ])
    if not rows:
        rows.append([InlineKeyboardButton("لا يوجد مشرفين ملفات حالياً", callback_data="noop")])
    rows.append([InlineKeyboardButton("➕ إضافة مشرف ملفات", callback_data=f"fr_admin_add_{bid}")])
    rows.append([InlineKeyboardButton("رجوع", callback_data=f"e_{bid}")])
    return InlineKeyboardMarkup(rows)

def kb_file_request_cancel():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ إلغاء الطلب", callback_data="fr_cancel")
    ]])

def kb_file_upload_cancel():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("❌ إلغاء", callback_data="fu_cancel")
    ]])

def kb_special_container_quick(bid):
    """خيارات سريعة لزر مميز حاوية عند ضغط الأدمن عليه."""
    rows = [
        [InlineKeyboardButton("📂 إدارة الأزرار الداخلية", callback_data=f"m_{bid}")],
        [InlineKeyboardButton("✏️ تغيير الاسم",            callback_data=f"el_{bid}")],
        [InlineKeyboardButton("🗑 حذف",                    callback_data=f"confirm_x_{bid}")],
    ]
    return InlineKeyboardMarkup(rows)

def kb_pomodoro_settings(uid: int, show_modes: bool = False):
    """لوحة إعدادات مؤقت البومودورو."""
    s = get_pomodoro_settings(uid)
    enabled  = s["enabled"]
    study    = s["study_min"]
    brk      = s["break_min"]
    rows = []
    toggle_lbl = "🔕 إيقاف المؤقت" if enabled else "🔔 تفعيل المؤقت"
    rows.append([InlineKeyboardButton(toggle_lbl, callback_data="pom_toggle")])
    if enabled:
        for sm, bm, lbl in POMODORO_MODES:
            check = "✅ " if (sm == study and bm == brk) else ""
            rows.append([InlineKeyboardButton(
                f"{check}{lbl}", callback_data=f"pom_mode_{sm}_{bm}"
            )])
        rows.append([InlineKeyboardButton("✏️ تخصيص وقت الدراسة والاستراحة", callback_data="pom_custom")])
        rows.append([InlineKeyboardButton("▶️ ابدأ جلسة دراسة", callback_data="pom_start")])
    rows.append([InlineKeyboardButton("❌ إغلاق", callback_data="pom_close")])
    return InlineKeyboardMarkup(rows)

def kb_item_actions(iid):
    """أزرار تحت كل عنصر محتوى عند العرض."""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✏️ تغيير الوصف", callback_data=f"ci_edit_{iid}"),
        InlineKeyboardButton("🗑 حذف",          callback_data=f"ci_del_{iid}"),
    ]])

def kb_admins_inline():
    rows = []
    for a in all_admins():
        name = a.get("username") or str(a["id"])
        rows.append([
            InlineKeyboardButton(f"👤 {name}", callback_data="noop"),
            InlineKeyboardButton("🗑", callback_data=f"da_{a['id']}"),
        ])
    rows.append([InlineKeyboardButton("➕ إضافة مشرف", callback_data="aa")])
    rows.append([InlineKeyboardButton("رجوع", callback_data="st_back")])
    return InlineKeyboardMarkup(rows)

def kb_settings():
    global_cap = get_global_caption()
    cap_btns = get_caption_buttons()
    notif1_on  = get_setting("notif_enabled", "1") == "1"
    notif1_msg = get_setting("notif_message", "")
    cap_label    = "✏️ تغيير كليشة الكلام" if global_cap else "📌 كليشة الكلام"
    capbtn_label = f"🔗 كليشة الأزرار ({len(cap_btns)} زر)" if cap_btns else "🔗 كليشة الأزرار"
    notif1_icon  = "✅" if (notif1_on and notif1_msg) else "⭕"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 المشرفون",                     callback_data="st_admins")],
        [InlineKeyboardButton("💾 النسخ الاحتياطي",              callback_data="st_backup_menu")],
        [InlineKeyboardButton("✏️ تعديل رسالة البداية",          callback_data="st_startmsg")],
        [InlineKeyboardButton(cap_label,                         callback_data="st_caption")],
        [InlineKeyboardButton(capbtn_label,                      callback_data="st_capbtn")],
        [InlineKeyboardButton(f"📢 رسالة الاشتراك {notif1_icon}", callback_data="st_notif1")],
        [InlineKeyboardButton("📊 الإحصائيات",                   callback_data="st_stats")],
        [InlineKeyboardButton("🔥 الملفات الترند",                callback_data="st_trending_0")],
        [InlineKeyboardButton("📡 الإذاعة",                       callback_data="st_broadcast")],
        [InlineKeyboardButton("💬 العبارات التحفيزية",             callback_data="st_phrases")],
        [InlineKeyboardButton("⭐ الأزرار المميزة",                callback_data="st_specials")],
    ])

def kb_notif1_settings():
    notif_on     = get_setting("notif_enabled", "1") == "1"
    msg          = get_setting("notif_message", "")
    chan         = get_setting("notif_channel", "")
    every_op     = get_setting("notif_every_opens", "5")
    ok_text      = get_setting("notif_ok_text",    "✅ نعم، اشتركت")
    cancel_text  = get_setting("notif_cancel_text", "❌ لا، لاحقاً")
    toggle_label = "🔕 إيقاف رسالة الاشتراك" if notif_on else "📢 تفعيل رسالة الاشتراك"
    rows = []
    rows.append([InlineKeyboardButton(toggle_label, callback_data="st_notif_toggle")])
    rows.append([InlineKeyboardButton(
        "✏️ تغيير نص التنبيه" if msg else "✏️ كتابة نص التنبيه",
        callback_data="st_notif_msg"
    )])
    rows.append([InlineKeyboardButton(
        f"📢 القناة: {chan}" if chan else "📢 تحديد رابط القناة",
        callback_data="st_notif_chan"
    )])
    rows.append([InlineKeyboardButton(
        f"📂 يظهر كل {every_op} ضغطة",
        callback_data="st_notif_opens"
    )])
    rows.append([
        InlineKeyboardButton(f'زر "نعم": {ok_text}',    callback_data="st_notif_ok_text"),
        InlineKeyboardButton(f'زر "لا": {cancel_text}', callback_data="st_notif_cancel_text"),
    ])
    rows.append([InlineKeyboardButton("رجوع", callback_data="st_back")])
    return InlineKeyboardMarkup(rows)

def kb_broadcast():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📩 إرسال رسالة جديدة", callback_data="st_broadcast_send")],
        [InlineKeyboardButton("رجوع",                  callback_data="st_back")],
    ])

def kb_broadcast_confirm():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ إرسال للجميع",  callback_data="st_broadcast_confirm"),
            InlineKeyboardButton("❌ إلغاء",          callback_data="st_broadcast"),
        ],
    ])

def kb_phrases():
    phrases = get_phrases()
    chance  = get_phrases_chance()
    rows = []
    for p in phrases:
        short = p["phrase"][:30] + ("…" if len(p["phrase"]) > 30 else "")
        rows.append([
            InlineKeyboardButton(f"🗑 {short}", callback_data=f"st_phrase_del_{p['id']}"),
        ])
    rows.append([InlineKeyboardButton("➕ إضافة عبارة",            callback_data="st_phrase_add")])
    rows.append([InlineKeyboardButton(f"🎲 نسبة الظهور: {chance}%", callback_data="st_phrase_chance")])
    rows.append([InlineKeyboardButton("رجوع",                       callback_data="st_back")])
    return InlineKeyboardMarkup(rows)

def kb_specials_list():
    """قائمة بجميع الأزرار المميزة في الإعدادات."""
    sp_btns = get_all_special_btns()
    rows = []
    for sp in sp_btns:
        pid_info = "الرئيسية" if sp.get("parent_id") is None else (
            (get_btn(sp["parent_id"]) or {}).get("label", "—"))
        rows.append([InlineKeyboardButton(
            f"⭐ {sp['label']} (#{sp['id']}) — {pid_info}",
            callback_data=f"st_special_view_{sp['id']}"
        )])
    if not sp_btns:
        rows.append([InlineKeyboardButton("لا توجد أزرار مميزة بعد", callback_data="noop")])
    rows.append([InlineKeyboardButton("رجوع", callback_data="st_back")])
    return InlineKeyboardMarkup(rows)

def kb_special_manage(bid):
    """لوحة إدارة زر مميز واحد من الإعدادات."""
    b = get_btn(bid)
    if not b:
        return InlineKeyboardMarkup([[InlineKeyboardButton("رجوع", callback_data="st_specials")]])
    rows = [
        [InlineKeyboardButton("✏️ تغيير الاسم", callback_data=f"el_{bid}")],
        [InlineKeyboardButton("🗑 حذف الزر",    callback_data=f"confirm_x_{bid}")],
        [InlineKeyboardButton("رجوع",           callback_data="st_specials")],
    ]
    return InlineKeyboardMarkup(rows)

def kb_caption_settings():
    global_cap = get_global_caption()
    rows = []
    if global_cap:
        rows.append([InlineKeyboardButton("✏️ تغيير الكليشة", callback_data="st_caption_set")])
        rows.append([InlineKeyboardButton("🗑 حذف الكليشة",   callback_data="st_caption_clear")])
    else:
        rows.append([InlineKeyboardButton("➕ كتابة الكليشة", callback_data="st_caption_set")])
    rows.append([InlineKeyboardButton("رجوع", callback_data="st_back")])
    return InlineKeyboardMarkup(rows)

def kb_caption_btn_settings():
    btns = get_caption_buttons()
    rows = []
    for b in btns:
        rows.append([
            InlineKeyboardButton(f"🔗 {b['label']}", url=b["url"]),
            InlineKeyboardButton("🗑", callback_data=f"st_capbtn_del_{b['id']}"),
        ])
    rows.append([InlineKeyboardButton("➕ إضافة زر رابط", callback_data="st_capbtn_add")])
    rows.append([InlineKeyboardButton("رجوع", callback_data="st_back")])
    return InlineKeyboardMarkup(rows)
