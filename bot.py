import asyncio
from email.mime import application
import json
from telegram.ext import MessageHandler, filters
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton,  WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)
import asyncpg
import os
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

DATABASE_URL = os.getenv("DATABASE_URL")
TOKEN = os.getenv("BOT_TOKEN")

# Biznes lokatsiyasi
LATITUDE = 41.270528
LONGITUDE = 69.171306

ADMIN_ID = 5522204543

ORDER_NUMBER = 0

# Ustaga yozilish bosqichlari
CAR, SERVICE, PHONE, DATE, CAR_OTHER, SERVICE_OTHER, PART_CAR, PART_YEAR, PART_NAME, PART_PHOTO, PART_VIN, PART_PHONE = range(12)


# =========================
# START
# =========================



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [KeyboardButton(
            "🛒 Zapchastlar",
            web_app=WebAppInfo(
                url="https://auto-service-bice.vercel.app"
            )
        )],
        [KeyboardButton("🔧 Xizmatlar"), KeyboardButton("💰 Narxlar")],
        [KeyboardButton("📍 Manzil"), KeyboardButton("🕐 Ish vaqti")],
        [KeyboardButton("📅 Ustaga yozilish"), KeyboardButton("🧩 Zapchast so‘rash")],
        [KeyboardButton("📞 Aloqa")]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🚗 AVTOSERVISga xush kelibsiz!\n\n"
        "Sizga qanday yordam bera olamiz?",
        reply_markup=reply_markup
    )


# =========================
# XIZMATLAR
# =========================

async def web_app_order(update, context):
    print("🔥 WEB APP DATA KELDI")

    try:
        data = update.effective_message.web_app_data.data
        print("📦 DATA:", data)

        order = json.loads(data)

        brand = order.get("brand", "")
        model = order.get("model", "")
        products = order.get("products", [])

        product_text = ""

        for i, product in enumerate(products, start=1):
            product_text += (
                f"{i}. {product.get('name')}\n"
                f"💰 {product.get('price')}\n\n"
            )

        user = update.effective_user

        text = (
            "🔔 YANGI BUYURTMA\n\n"
            f"👤 Mijoz: {user.full_name}\n"
            f"🆔 Telegram ID: {user.id}\n"
            f"🚗 Mashina: {brand} {model}\n\n"
            "🛒 TANLANGAN ZAPCHASTLAR:\n\n"
            f"{product_text}"
        )

        print("📤 ADMINGA YUBORILMOQDA...")

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=text
        )

        print("✅ ADMININGA YUBORILDI")

        await update.message.reply_text(
            "✅ Buyurtmangiz qabul qilindi!"
        )

    except Exception as e:
        print("❌ WEB APP ORDER ERROR:", repr(e))

async def services(update: Update):
    await update.message.reply_text(
        "🔧 BIZNING XIZMATLAR:\n\n"
        "🔹 Moy almashtirish\n"
        "🔹 Kompyuter diagnostikasi\n"
        "🔹 Hodovoy tekshirish\n"
        "🔹 Batareya yomkostini tekshirish\n"
        "🔹 Batareya disbalans\n"
        "🔹 Batareya remont\n"
    )


# =========================
# NARXLAR
# =========================

async def prices(update: Update):
    await update.message.reply_text(
        "💰 XIZMATLAR NARXI:\n\n"
        "🔧 Moy almashtirish — 150 000 so'mdan\n"
        "💻 Diagnostika — 200 000 so'mdan\n"
        "🔩 Batareya yomkostini tekshirish — 300 000 so'mdan\n"
        "⚠️ Aniq narx avtomobil va muammoga qarab belgilanadi."
    )


# =========================
# MANZIL
# =========================

async def location(update: Update):
    await update.message.reply_location(
        latitude=LATITUDE,
        longitude=LONGITUDE
    )

    await update.message.reply_text(
    "📍 MANZIL:\n\n"
    "Katta Qani ko‘chasi, 3-A uy\n\n"

    "📞 ASOSIY ALOQA RAQAMI:\n\n"
    "+998 99 220 11 11\n\n"

    "🚗 EVAKUATOR XIZMATI:\n\n"
    "PANDA’da evakuator xizmati mavjud.\n"
    "Evakuator uchun: +998 99 220 11 11\n\n"

    "🕐 ISH VAQTI:\n\n"
    "09:00–19:00"
)
# =========================
# ISH VAQTI
# =========================

async def working_time(update: Update):
    await update.message.reply_text(
        "🕐 ISH VAQTI:\n\n"
        "Dushanba – Shanba: 09:00 – 19:00"
    )


# =========================
# ALOQA
# =========================

async def contact(update: Update):
    await update.message.reply_text(
        "📞 ALOQA:\n\n"
        "Telefon: +998 99 220 11 11\n"
        "Telegram: @pandaavtoservis\n\n"
        "Operator bilan bog'lanish uchun telefon qiling."
    )


# =========================
# USTAGA YOZILISH - 1
# =========================

async def booking_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    
    keyboard = [
        [KeyboardButton("BYD"), KeyboardButton("Dongfeng")],
        [KeyboardButton("Deepal"), KeyboardButton("Senova")],
        [KeyboardButton("Boshqa")],
        [KeyboardButton("⬅️ Bosh menyu")]
    ]

    await update.message.reply_text(
        "🚗 Avtomobilingiz markasini tanlang:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )

    return CAR


# =========================
# USTAGA YOZILISH - 2
# =========================

async def get_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    car = update.message.text

    if car == "Boshqa":
        await update.message.reply_text(
            "✍️ Avtomobil modelingizni yozing:\n\n"
            "Masalan: BYD"
        )
        return CAR_OTHER

    context.user_data["car"] = car

    keyboard = [
        [KeyboardButton("🔧 Moy almashtirish")],
        [KeyboardButton("💻 Diagnostika")],
        [KeyboardButton("🔩 Batareya yomkost tekshirish")],
        [KeyboardButton("🛑 Batareya disbalans")],
        [KeyboardButton("⚙️ Batareya remont")],
        [KeyboardButton("🔧 Boshqa")],
        [KeyboardButton("⬅️ Bosh menyu")]
    ]

    await update.message.reply_text(
        "🔧 Qanday xizmat kerak?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )

    return SERVICE

async def get_car_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["car"] = update.message.text

    keyboard = [
        [KeyboardButton("🔧 Moy almashtirish")],
        [KeyboardButton("💻 Diagnostika")],
        [KeyboardButton("🔩 Batareya yomkost tekshirish")],
        [KeyboardButton("🛑 Batareya disbalans")],
        [KeyboardButton("⚙️ Batareya remont")],
        [KeyboardButton("🔧 Boshqa")],
        [KeyboardButton("⬅️ Bosh menyu")]
    ]

    await update.message.reply_text(
        "🔧 Qanday xizmat kerak?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )

    return SERVICE



async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.contact:
        phone = update.message.contact.phone_number
    elif update.message.text:
        phone = update.message.text
    else:
        await update.message.reply_text(
            "📞 Telefon raqamingizni yuboring."
        )
        return PHONE

    context.user_data["phonenumber"] = phone

    await update.message.reply_text(
        "📅 Qaysi kunga yozilmoqchisiz?\n\n"
        "Masalan:\n"
        "22-avgust"
    )

    return DATE
    # Agar qo'lda raqam yozsa
    
# =========================
# USTAGA YOZILISH - 3
# =========================

async def get_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    service = update.message.text

    if service == "🔧 Boshqa":
        await update.message.reply_text(
            "✍️ Kerakli xizmatni yozing:\n\n"
            "Masalan: Karobka ta'miri"
        )
        return SERVICE_OTHER

    context.user_data["service"] = service

    keyboard = [
        [KeyboardButton(
            "📱 Kontaktni yuborish",
            request_contact=True
        )],
        [KeyboardButton("⬅️ Bosh menyu")]
        
    ]

    await update.message.reply_text(
        "📞 Telefon raqamingizni yuboring:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )

    return PHONE
async def get_service_other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["service"] = update.message.text

    keyboard = [
        [KeyboardButton(
            "📱 Kontaktni yuborish",
            request_contact=True
        )]
    ]

    await update.message.reply_text(
        "📞 Telefon raqamingizni yuboring:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )

    return PHONE

# =========================
# USTAGA YOZILISH - 4
# =========================

async def get_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global ORDER_NUMBER

    context.user_data["date"] = update.message.text

    car = context.user_data["car"]
    service = context.user_data["service"]
    phone = context.user_data["phonenumber"]
    user = update.effective_user
    username = f"@{user.username}" if user.username else "Username yo‘q"
    full_name = user.full_name
    user_id = user.id
    date = context.user_data["date"]

    # Buyurtma raqamini oshiramiz
    ORDER_NUMBER += 1

    order_id = f"PANDA-{ORDER_NUMBER:04d}"

    conn = await asyncpg.connect(DATABASE_URL)

    await conn.execute("""
        INSERT INTO orders
        (order_number, user_id, username, full_name, phone, car, service, date)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
    """,
        order_id,
        user_id,
        username,
        full_name,
        phone,
        car,
        service,
        date
    )

    await conn.close()

    # Klientga
    main_keyboard = [
    [KeyboardButton("🔧 Xizmatlar"), KeyboardButton("💰 Narxlar")],
    [KeyboardButton("📍 Manzil"), KeyboardButton("🕐 Ish vaqti")],
    [KeyboardButton("📅 Ustaga yozilish"), KeyboardButton("🧩 Zapchast so‘rash")],
    [KeyboardButton("📞 Aloqa")]
    ]

    await update.message.reply_text(
        "✅ BUYURTMANGIZ QABUL QILINDI!\n\n"
        f"🆔 Buyurtma: #{order_id}\n"
        f"🚗 Avtomobil: {car}\n"
        f"🔧 Xizmat: {service}\n"
        f"📞 Telefon raqam: {phone}\n"
        f"📅 Sana: {date}\n\n"
        "📞 Tez orada operator siz bilan bog‘lanadi.\n\n"
        "🏠 Bosh menyu:",
        reply_markup=ReplyKeyboardMarkup(
            main_keyboard,
            resize_keyboard=True
        )
    )

    # Adminga
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            f"🔔 YANGI BUYURTMA #{order_id}\n\n"
            f"👤 Klient: {full_name}\n"
            f"🔗 Username: {username}\n"
            f"🆔 Telegram ID: {user_id}\n\n"
            f"🚗 Avtomobil: {car}\n"
            f"🔧 Xizmat: {service}\n"
            f"📞 Telefon raqam: {phone}\n"
            f"📅 Sana: {date}"
        )
    )

    context.user_data.clear()

    return ConversationHandler.END

# =========================
# BEKOR QILISH
# =========================

async def back_to_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await start(update, context)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "❌ Buyurtma bekor qilindi.\n\n"
        "Bosh menyuga qaytish uchun /start ni bosing."
    )

    return ConversationHandler.END



async def parts_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [KeyboardButton("⬅️ Bosh menyu")]
    ]

    await update.message.reply_text(
        "🚗 Mashina markasi va modelini yozing:\n\n"
        "Masalan:\n"
        "Senova\n\n"
        "⬅️ Bosh menyuga qaytish mumkin.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )

    return PART_CAR
async def get_part_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["part_car"] = update.message.text

    await update.message.reply_text(
        "📅 Mashina yilini yozing:\n\n"
        "Masalan:\n"
        "2021"
    )

    return PART_YEAR

async def get_part_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["part_year"] = update.message.text

    await update.message.reply_text(
        "🔧 Qaysi zapchast kerak?\n\n"
        "Zapchast nomini yozing.\n"
        "Masalan:\n"
        "Batareya moduli"
    )

    return PART_NAME

async def get_part_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["part_name"] = update.message.text

    keyboard = [
        [KeyboardButton("⏭️ O‘tkazib yuborish")],
        [KeyboardButton("⬅️ Bosh menyu")]
    ]

    await update.message.reply_text(
        "📸 Zapchast yoki avtomobilning rasmini yuboring.\n\n"
        "Agar rasm bo‘lmasa, ⏭️ O‘tkazib yuborish tugmasini bosing.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )

    return PART_PHOTO

async def get_part_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        photo = update.message.photo[-1]
        context.user_data["part_photo"] = photo.file_id

        await update.message.reply_text(
            "🔢 VIN kodini yuboring.\n\n"
            "Masalan:\n"
            "XW8ZZZ61Z..."
        )

        return PART_VIN

    if update.message.text == "⏭️ O‘tkazib yuborish":
        context.user_data["part_photo"] = None

        await update.message.reply_text(
            "🔢 VIN kodini yuboring.\n\n"
            "Agar VIN kod bo‘lmasa, ⏭️ O‘tkazib yuborish tugmasini bosing."
        )

        return PART_VIN

    await update.message.reply_text(
        "📸 Iltimos, rasm yuboring yoki ⏭️ O‘tkazib yuborish tugmasini bosing."
    )

    return PART_PHOTO

async def get_part_vin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text != "⏭️ O‘tkazib yuborish":
        context.user_data["part_vin"] = update.message.text
    else:
        context.user_data["part_vin"] = "Kiritilmagan"

    keyboard = [
        [KeyboardButton(
            "📱 Kontaktni yuborish",
            request_contact=True
        )],
        [KeyboardButton("⬅️ Bosh menyu")]
    ]

    await update.message.reply_text(
        "📞 Telefon raqamingizni yuboring:\n\n"
        "📱 Kontaktni yuborishingiz mumkin yoki "
        "raqamingizni qo‘lda yozishingiz mumkin.\n\n"
        "Masalan: +998 99 123 45 67",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )

    return PART_PHONE

async def get_part_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text

    context.user_data["part_phone"] = phone

    car = context.user_data.get("part_car", "Kiritilmagan")
    year = context.user_data.get("part_year", "Kiritilmagan")
    part_name = context.user_data.get("part_name", "Kiritilmagan")
    vin = context.user_data.get("part_vin", "Kiritilmagan")
    photo_id = context.user_data.get("part_photo")
    user = update.effective_user
    username = f"@{user.username}" if user.username else "Username yo‘q"
    full_name = user.full_name
    user_id = user.id

    conn = await asyncpg.connect(DATABASE_URL)

    await conn.execute("""
        INSERT INTO parts_orders
        (user_id, username, full_name, phone, car, year, part_name, vin, photo_id)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    """,
        user_id,
        username,
        full_name,
        phone,
        car,
        year,
        part_name,
        vin,
        photo_id
    )

    await conn.close()

    # Klientga
    main_keyboard = [
    [KeyboardButton("🔧 Xizmatlar"), KeyboardButton("💰 Narxlar")],
    [KeyboardButton("📍 Manzil"), KeyboardButton("🕐 Ish vaqti")],
    [KeyboardButton("📅 Ustaga yozilish"), KeyboardButton("🧩 Zapchast so‘rash")],
    [KeyboardButton("📞 Aloqa")]
    ]

    await update.message.reply_text(
        "✅ ZAPCHAST SO‘ROVINGIZ QABUL QILINDI!\n\n"
        f"👤 Klient: {full_name}\n"
        f"🔗 Username: {username}\n"
        f"🆔 Telegram ID: {user_id}\n\n"
        f"🚗 Mashina: {car}\n"
        f"📅 Yili: {year}\n"
        f"🔧 Zapchast: {part_name}\n"
        f"🔢 VIN: {vin}\n"
        f"📞 Telefon: {phone}\n\n"
        "📞 Tez orada operator siz bilan bog‘lanadi.\n\n"
        "🏠 Bosh menyu:",
        reply_markup=ReplyKeyboardMarkup(
            main_keyboard,
            resize_keyboard=True
        )
    )

    # Adminga
    admin_text = (
        "🧩 YANGI ZAPCHAST SO‘ROVI!\n\n"
        f"🚗 Mashina: {car}\n"
        f"📅 Yili: {year}\n"
        f"🔧 Zapchast: {part_name}\n"
        f"🔢 VIN: {vin}\n"
        f"📞 Telefon: {phone}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_text
    )

    # Rasm yuborilgan bo‘lsa
    if photo_id:
        await context.bot.send_photo(
            chat_id=ADMIN_ID,
            photo=photo_id,
            caption="📸 Zapchast/avtomobil rasmi"
        )

    context.user_data.clear()

    return ConversationHandler.END
# =========================
# UMUMIY MESSAGE HANDLER
# =========================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🔧 Xizmatlar":
        await services(update)

    elif text == "💰 Narxlar":
        await prices(update)

    elif text == "📍 Manzil":
        await location(update)

    elif text == "🕐 Ish vaqti":
        await working_time(update)

    elif text == "📞 Aloqa":
        await contact(update)

    else:
        await update.message.reply_text(
            "Iltimos, menyudagi tugmalardan birini tanlang."
        )


# =========================
# MAIN
# =========================

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            order_number TEXT,
            user_id BIGINT,
            username TEXT,
            full_name TEXT,
            phone TEXT,
            car TEXT,
            service TEXT,
            date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS parts_orders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            username TEXT,
            full_name TEXT,
            phone TEXT,
            car TEXT,
            year TEXT,
            part_name TEXT,
            vin TEXT,
            photo_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    await conn.close()

def main():
    asyncio.run(init_db())

    app = Application.builder().token(TOKEN).build()

    # Start
    app.add_handler(
        CommandHandler("start", start)
    )

    # Ustaga yozilish
    booking = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^📅 Ustaga yozilish$"),
                booking_start
            ),

            MessageHandler(
                filters.Regex("^🧩 Zapchast so‘rash$"),
                parts_start
            )
        ],

        states={

    # =========================
    # USTAGA YOZILISH
    # =========================

    CAR: [
        MessageHandler(
            filters.Regex("^⬅️ Bosh menyu$"),
            back_to_menu
        ),
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            get_car
        )
    ],

    CAR_OTHER: [
        MessageHandler(
            filters.Regex("^⬅️ Bosh menyu$"),
            back_to_menu
        ),
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            get_car_other
        )
    ],

    SERVICE: [
        MessageHandler(
            filters.Regex("^⬅️ Bosh menyu$"),
            back_to_menu
        ),
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            get_service
        )
    ],

    SERVICE_OTHER: [
        MessageHandler(
            filters.Regex("^⬅️ Bosh menyu$"),
            back_to_menu
        ),
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            get_service_other
        )
    ],

    PHONE: [
        MessageHandler(
            filters.Regex("^⬅️ Bosh menyu$"),
            back_to_menu
        ),
        MessageHandler(
            filters.CONTACT,
            get_phone
        ),
        MessageHandler(
            filters.TEXT & ~filters.Regex("^⬅️ Bosh menyu$") & ~filters.COMMAND,
            get_phone
        )
    ],

    DATE: [
        MessageHandler(
            filters.Regex("^⬅️ Bosh menyu$"),
            back_to_menu
        ),
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            get_date
        )
    ],

    # =========================
    # ZAPCHAST SO‘RASH
    # =========================

    PART_CAR: [
        MessageHandler(
            filters.Regex("^⬅️ Bosh menyu$"),
            back_to_menu
        ),
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            get_part_car
        )
    ],

    PART_YEAR: [
        MessageHandler(
            filters.Regex("^⬅️ Bosh menyu$"),
            back_to_menu
        ),
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            get_part_year
        )
    ],

    PART_NAME: [
        MessageHandler(
            filters.Regex("^⬅️ Bosh menyu$"),
            back_to_menu
        ),
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            get_part_name
        )
    ],

    PART_PHOTO: [
        MessageHandler(
            filters.Regex("^⬅️ Bosh menyu$"),
            back_to_menu
        ),
        MessageHandler(
            filters.PHOTO,
            get_part_photo
        ),
        MessageHandler(
            filters.Regex("^⏭️ O‘tkazib yuborish$"),
            get_part_photo
        )
    ],

    PART_VIN: [
        MessageHandler(
            filters.Regex("^⬅️ Bosh menyu$"),
            back_to_menu
        ),
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            get_part_vin
        )
    ],

    PART_PHONE: [
        MessageHandler(
            filters.Regex("^⬅️ Bosh menyu$"),
            back_to_menu
        ),
        MessageHandler(
            filters.CONTACT,
            get_part_phone
        ),
        MessageHandler(
            filters.TEXT & ~filters.Regex("^⬅️ Bosh menyu$") & ~filters.COMMAND,
            get_part_phone
        )
    ],
},

        fallbacks=[
            CommandHandler("cancel", cancel)
        ]
    )

    app.add_handler(booking)

    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.WEB_APP_DATA,
            web_app_order
        )
    )

    # Oddiy menyu
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    print("🚗 Avtoservis bot ishga tushdi...")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
    )


if __name__ == "__main__":
    main()