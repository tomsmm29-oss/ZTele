import telebot
import time
import threading,cloudscraper
from telebot import types
import requests, random, os, pickle, time, re
from bs4 import BeautifulSoup
# توكن البوت
token = os.getenv("TG_BOT_VISA")
bot = telebot.TeleBot(token, parse_mode="HTML")

#ايدي حسابك
# ايديات الادمن (List of int)
admin = [6945645009, 8241311871]

# ايديات خاصة (List of int)
myid = [6052713305, 8241311871] 
stop = {}
user_gateways = {}
stop_flags = {} 
stopuser = {}
command_usage = {}

mes = types.InlineKeyboardMarkup()
mes.add(types.InlineKeyboardButton(text="Start Checking", callback_data="start"))


@bot.message_handler(commands=["start"])
def handle_start(message):
    sent_message = bot.send_message(chat_id=message.chat.id, text="💥 Starting...")
    time.sleep(1)
    name = message.from_user.first_name
    bot.edit_message_text(chat_id=message.chat.id,
                          message_id=sent_message.message_id,
                          text=f"Hi {name}, Welcome To Saoud Checker (Stripe Auth)",
                          reply_markup=mes)

@bot.callback_query_handler(func=lambda call: call.data == 'start')
def handle_start_button(call):
    name = call.from_user.first_name

    bot.send_message(call.message.chat.id, 
        '''- مرحباً بك في بوت فحص OTP And Passed ✅


للفحص اليدوي(OTP) [/otp] و للكومبو فقط ارسل الملف.

للفحص اليدوي(Passed) [/vbv] و للكومبو فقط ارسل الملف.

اختر نوع الفحص وسيبدأ البوت بأعطائك افضل النتائج مع علاوي الاسطوره @B11HB''')


    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f"Hi {name}, Welcome To Saoud Checker (Brantree LookUp)",
                          reply_markup=mes)

