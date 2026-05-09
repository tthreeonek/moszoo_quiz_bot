import logging
import os
from urllib.parse import quote

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, ContextTypes, filters

from config import BOT_TOKEN, ADMIN_CHAT_ID, ZOO_EMAIL, ZOO_PHONE, OPECKA_URL, PROXY_URL, GET_UPDATES_PROXY, LOGO_PATH, BOT_USERNAME
from questions_data import QUESTIONS, get_tiebreaker_question
from animals_data import animals_info

# Состояния
QUESTION_STATE = range(len(QUESTIONS))  # 0..4
TIEBREAKER = 100
FEEDBACK = 200

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ---------- Генерация ссылок для соцсетей ----------
def get_share_text(animal_name):
    return f"Моё тотемное животное — {animal_name} в Московском зоопарке! Узнай своего: https://t.me/{BOT_USERNAME.lstrip('@')}"

def get_twitter_share_url(animal_name):
    text = get_share_text(animal_name)
    return f"https://twitter.com/intent/tweet?text={quote(text)}"

def get_vk_share_url(animal_name):
    text = get_share_text(animal_name)
    url = f"https://t.me/{BOT_USERNAME.lstrip('@')}"
    return f"https://vk.com/share.php?url={quote(url)}&title={quote(text)}"

# ---------- Базовые команды ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if os.path.isfile(LOGO_PATH):
            with open(LOGO_PATH, "rb") as logo:
                await update.message.reply_photo(photo=logo)
    except Exception as e:
        logger.warning(f"Логотип не загружен: {e}")

    keyboard = [
        ["🦊 Начать викторину"],
        ["ℹ️ О программе опеки", "📞 Контакты"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Привет! Я бот Московского зоопарка и помогу тебе узнать твоё тотемное животное!\n"
        "А ещё расскажу, как ты можешь помочь настоящим обитателям зоопарка через программу опеки.\n\n"
        "Нажми кнопку ниже, чтобы начать ✨",
        reply_markup=reply_markup
    )

async def show_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🐾 *Программа «Возьми животное под опеку»*\n\n"
        "Ты можешь стать опекуном любого из 6 000 питомцев Московского зоопарка! "
        "Твоя поддержка помогает обеспечивать животным правильное питание, уход и комфортные условия.\n\n"
        "Участником может стать каждый — от ребёнка до крупной компании.\n"
        "Подробнее о программе и условиях читай на сайте зоопарка.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Открыть сайт программы", url=OPECKA_URL)
        ]])
    )

async def show_contacts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📬 *Связь с зоопарком*\n\n"
        f"Email: {ZOO_EMAIL}\n"
        f"Телефон: {ZOO_PHONE}\n\n"
        f"Ты также можешь обратиться через кнопку '📩 Связаться с сотрудником' после прохождения викторины.",
        parse_mode="Markdown"
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Викторина прервана. Ты всегда можешь начать заново.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# ---------- Викторина ----------
async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["scores"] = {key: 0 for key in animals_info.keys()}
    context.user_data["current_question"] = 0
    await update.message.reply_text(
        "🎉 Отлично! Сейчас я задам несколько вопросов, чтобы определить твоё тотемное животное. "
        "Выбирай вариант, который ближе тебе по духу. Поехали!",
        reply_markup=ReplyKeyboardRemove()
    )
    return await show_question(update, context)

async def show_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idx = context.user_data.get("current_question", 0)
    if idx >= len(QUESTIONS):
        return await determine_result(update, context)

    q = QUESTIONS[idx]
    keyboard = [
        [InlineKeyboardButton(opt["text"], callback_data=f"ans_{opt['animal']}")]
        for opt in q["options"]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            f"Вопрос {idx+1}/{len(QUESTIONS)}:\n\n{q['text']}",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            f"Вопрос {idx+1}/{len(QUESTIONS)}:\n\n{q['text']}",
            reply_markup=reply_markup
        )
    return QUESTION_STATE[idx]

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    animal = query.data.split("_", 1)[1]
    context.user_data["scores"][animal] += 1
    context.user_data["current_question"] += 1
    return await show_question(update, context)

async def determine_result(update_or_query, context):
    scores = context.user_data["scores"]
    max_score = max(scores.values())
    leaders = [key for key, val in scores.items() if val == max_score]

    if len(leaders) == 1:
        return await show_result(update_or_query, context, leaders[0])
    else:
        context.user_data["leaders"] = leaders
        tie_q = get_tiebreaker_question(leaders)
        keyboard = [
            [InlineKeyboardButton(opt["text"], callback_data=f"tie_{opt['animal']}")]
            for opt in tie_q["options"]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update_or_query.callback_query:
            await update_or_query.callback_query.edit_message_text(tie_q["text"], reply_markup=reply_markup)
        else:
            await update_or_query.message.reply_text(tie_q["text"], reply_markup=reply_markup)
        return TIEBREAKER

async def handle_tiebreaker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    animal = query.data.split("_", 1)[1]
    context.user_data["scores"][animal] += 1

    leaders = context.user_data.get("leaders", [])
    if leaders:
        new_scores = {key: context.user_data["scores"][key] for key in leaders}
        max_val = max(new_scores.values())
        winner = [key for key, val in new_scores.items() if val == max_val][0]
    else:
        max_val = max(context.user_data["scores"].values())
        winner = [key for key, val in context.user_data["scores"].items() if val == max_val][0]

    return await show_result(update, context, winner)

async def show_result(update, context, animal_key):
    animal = animals_info[animal_key]
    img_path = animal.get("image_path", "")

    msg = update.callback_query.message if update.callback_query else update.message

    # Отправляем фото
    try:
        if os.path.isfile(img_path):
            await msg.reply_photo(
                photo=open(img_path, "rb"),
                caption=animal["description"],
                parse_mode="Markdown"
            )
        else:
            await msg.reply_photo(
                photo=img_path,
                caption=animal["description"],
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.warning(f"Не удалось отправить изображение: {e}")
        await msg.reply_text(animal["description"], parse_mode="Markdown")

    # Блок с опекой и соцсетями
    info_text = (
        f"🐾 *Хочешь помочь {animal['name']} и другим обитателям зоопарка?*\n\n"
        f"{animal['care_info']}\n\n"
        "Стань опекуном прямо сейчас! Это просто и приятно."
    )

    twitter_url = get_twitter_share_url(animal["name"])
    vk_url = get_vk_share_url(animal["name"])

    keyboard = [
        [InlineKeyboardButton("❤️ Узнать больше об опеке", url=OPECKA_URL)],
        [InlineKeyboardButton("🐦 Поделиться в Twitter", url=twitter_url),
         InlineKeyboardButton("💙 Поделиться ВКонтакте", url=vk_url)],
        [InlineKeyboardButton("🔄 Поделиться в Telegram", switch_inline_query="")],
        [InlineKeyboardButton("📩 Связаться с сотрудником", callback_data="contact"),
         InlineKeyboardButton("📝 Оставить отзыв", callback_data="feedback")],
        [InlineKeyboardButton("🔁 Попробовать ещё раз", callback_data="restart")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await msg.reply_text(info_text, parse_mode="Markdown", reply_markup=reply_markup)

    context.user_data.clear()
    return ConversationHandler.END

# ---------- Обработчики кнопок результата ----------
async def contact_staff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id

    try:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"📥 Запрос на связь от пользователя @{update.effective_user.username or 'без ника'}, ID: {user_id}.\n"
                 f"Результат викторины: {query.message.text if query.message else 'не определён'}"
        )
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение админу: {e}")

    await query.message.reply_text(
        f"✅ Информация передана сотруднику зоопарка.\n\n"
        f"Ты также можешь написать или позвонить нам самостоятельно:\n"
        f"📧 {ZOO_EMAIL}\n"
        f"📞 {ZOO_PHONE}"
    )

# ---------- Отзыв (отдельный ConversationHandler) ----------
async def feedback_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("✍️ Пожалуйста, напиши свой отзыв или пожелание. Я всё передам!")
    return FEEDBACK

async def feedback_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    feedback_text = update.message.text
    user_id = update.effective_user.id
    with open("feedback.log", "a", encoding="utf-8") as f:
        f.write(f"User {user_id}: {feedback_text}\n")
    logger.info(f"Получен отзыв от {user_id}: {feedback_text}")
    await update.message.reply_text("❤️ Спасибо за твой отзыв! Он поможет нам стать лучше.")
    return ConversationHandler.END

async def restart_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.message.reply_text(
        "🔄 Давай попробуем ещё раз!",
        reply_markup=ReplyKeyboardMarkup([["🦊 Начать викторину"]], resize_keyboard=True)
    )
    return ConversationHandler.END

# ---------- Главная функция ----------
def main():
    builder = Application.builder().token(BOT_TOKEN)
    if PROXY_URL:
        builder = builder.proxy_url(PROXY_URL).get_updates_proxy_url(GET_UPDATES_PROXY)

    application = builder.build()

    # ConversationHandler викторины
    quiz_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🦊 Начать викторину$"), start_quiz)],
        states={
            **{state: [CallbackQueryHandler(handle_answer, pattern="^ans_")] for state in QUESTION_STATE},
            TIEBREAKER: [CallbackQueryHandler(handle_tiebreaker, pattern="^tie_")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )

    # ConversationHandler отзыва
    feedback_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(feedback_start, pattern="^feedback$")],
        states={
            FEEDBACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, feedback_received)]
        },
        fallbacks=[],
        allow_reentry=True
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(quiz_conv)
    application.add_handler(feedback_conv)
    application.add_handler(MessageHandler(filters.Regex("^ℹ️ О программе опеки$"), show_info))
    application.add_handler(MessageHandler(filters.Regex("^📞 Контакты$"), show_contacts))
    application.add_handler(CallbackQueryHandler(contact_staff, pattern="^contact$"))
    application.add_handler(CallbackQueryHandler(restart_quiz, pattern="^restart$"))

    logger.info("Бот запущен")
    application.run_polling()

if __name__ == "__main__":
    main()