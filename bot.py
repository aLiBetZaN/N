from pyrogram import Client, idle
from pyrogram.filters import create, command, text
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup as Keyboard, InlineKeyboardButton as Button
from divar import Divar


TOKEN = "6801409072:AAFEYNGDzjifGZL1axVU5oCqw248lRh4OTs"
CHAT_ID = 6924550705
APP_ID = 15072666
API_KEY = "07743de0d77d50b6b939892044f60b63"

app = Client("main", APP_ID, API_KEY, bot_token=TOKEN)

steps = {}
divar = {}

def step(s):
    return create(lambda _, __, m: steps.get(m.from_user.id) == s)

filter_chat = create(lambda _, __, m: m.chat.id == CHAT_ID)

# Buttons 🔙❌🔎👥
start_b = Keyboard(
    [
        [Button("🔎 Leech 🔎", "Leech")],
        [Button("❌ Close Panel ❌", "Close")]
    ]
)
back_b = Keyboard(
    [
        [Button("🔙 Back", "Back")]
    ]
)
open_b = Keyboard(
    [
        [Button("⇢ open ⇠", "open")]
    ]
)

def delete_t(li):
    li_2 = []
    for l in li:
        li_2.append(l) if l not in li_2 else None
    return li_2
    
@app.on_message(~filter_chat|~text)
def none(_, __): pass

@app.on_message(command("start"))
def start(_, m: Message):
    user_id = m.from_user.id
    steps[user_id] = "start"
    m.reply(f"**Hello, {m.from_user.mention}**", reply_markup=start_b)

@app.on_message(step("leech:get_phone_number"))
def get_phone_number(_, m: Message):
    user_id = m.from_user.id
    divar[user_id] = Divar(m.text)
    send = divar[user_id].send_code()
    if send:
        steps[user_id] = "leech:get_code"
        m.reply("**✅ Code Was sent successfully\n\nSend code:**")
    else:
        m.reply("**❌phone number is wrong**", reply_markup=back_b)

@app.on_message(step("leech:get_code"))
def get_code(_, m: Message):
    user_id = m.from_user.id
    code = divar[user_id].login(m.text)
    if code:
        steps[user_id] = "leech:get_city"
        m.reply("**✅ Loged in successfully\n\nSend City for leech:**")
    else:
        m.reply("**❌ Code is wrong**")


@app.on_message(step("leech:get_city"))
def get_city(_, m: Message):
    user_id = m.from_user.id
    city = m.text
    p = 0
    while True:
        users = divar[user_id].get_users_token(city, p)
        if users:
            steps[user_id] = "start"
            phones = divar[user_id].get_users_phone(users)
            if phones:
                nums = "\n".join(delete_t(phones))
                m.reply(f"`{(nums)}`")
                p += 1
            else:
                m.reply("**You are limited ☹️**")
                break
            
        else:
            m.reply(f"**`({city})`, City not found**")
            break

@app.on_callback_query()
def call(_, q: CallbackQuery):
    data = q.data
    user_id = q.from_user.id
    m: Message = q.message
    q.answer()    
    if data == "Leech":
        steps[user_id] = "leech:get_phone_number"
        m.reply("**send your phone number**")

    elif data == "Back":
        steps[user_id] = "start"
        m.edit("**⇢ Main Menu**", reply_markup=start_b)

    elif data == "Close":
        steps[user_id] = "start"
        m.edit("**Menu Closed**", reply_markup=open_b)
    
    elif data == "open":
        steps[user_id] = "start"
        m.edit("**⇢ Menu Opened**", reply_markup=start_b)

    
app.start(), print("Started..."), idle(), app.stop()