import os
import time
from binance.client import Client
import requests
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)


api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")
client = Client(api_key, api_secret)

telegram_token = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("CHAT_ID")

# Simpan data harga terakhir untuk setiap koin
last_prices = {}

# Daftar perubahan harga yang akan dikirim
price_changes = []

# Fungsi untuk mengirim pesan ke Telegram
def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.spo(url, data=data)
    if response.status_code != 200:
        print('Gagal mengirim pesan ke Telegram')

# Fungsi untuk memeriksa perubahan harga pada semua koin futures
def check_price_changes():
    prices = client.futures_ticker()

    for price in prices:
        symbol = price['symbol']
        last_price = last_prices.get(symbol)
        current_price = float(price['lastPrice'])

        if last_price is not None and last_price != current_price:
            # Hitung perubahan persentase
            change_percentage = ((current_price - last_price) / last_price) * 100

            message = f'{symbol}: {current_price} ({change_percentage:.2f}%)'
            price_changes.append(message)

        last_prices[symbol] = current_price

    # Cek apakah ada perubahan harga yang perlu dikirim
    if price_changes:
        joined_message = '\n'.join(price_changes)
        send_telegram_message(joined_message)
        price_changes.clear()

# Rute untuk halaman utama
@app.route('/')
def home():
    return 'Welcome to the Flask app!'

# Rute untuk menerima webhook dari Binance
@app.route('/webhook', methods=['POST'])
def webhook():
    return 'OK'

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_price_changes, trigger='interval', seconds=60)
    scheduler.start()

    app.run()
