import base64
import os
import asyncio
from flask import Flask, request, jsonify
from telethon import TelegramClient
from telethon.tl.functions.messages import CreateChatRequest

# Decode session from env and write to file
session_b64 = os.getenv("SESSION_B64")
if session_b64:
    with open("userbot.session", "wb") as f:
        f.write(base64.b64decode(session_b64))

# Telegram credentials
api_id = 22980967
api_hash = '98bf1fb670bd1fd37f6a77a393f8953a'
session_name = 'userbot'
manager_id = 7354584604

app = Flask(__name__)
client = TelegramClient(session_name, api_id, api_hash)

@app.route('/')
def home():
    return '🤖 Telegram Group Bot is Alive!'

@app.route('/send/<text>')
def send_message(text):
    async def run():
        await client.connect()
        if not await client.is_user_authorized():
            return jsonify({"error": "Client is not authorized"}), 403
        await client.send_message("me", text)
        await client.disconnect()
        return f"✅ Message sent: {text}"
    return asyncio.run(run())

@app.route('/create-group', methods=['POST'])
def create_group():
    data = request.json
    customer_id = int(data['telegram_user_id'])
    customer_name = data['customer_name']
    business = data['business_type']
    volume = data['monthly_volume']

    async def run():
        await client.connect()
        if not await client.is_user_authorized():
            return jsonify({"error": "Client is not authorized"}), 403

        result = await client(CreateChatRequest(
            users=[customer_id, manager_id],
            title=f"Client: {customer_name}"
        ))
        group_id = result.chats[0].id

        welcome = (
            f"👋 Welcome {customer_name}!\n"
            f"📌 Business: {business}\n"
            f"💰 Volume: {volume}\n"
            f"🧑‍💼 A manager will assist you shortly."
        )
        await client.send_message(group_id, welcome)
        await client.disconnect()
        return jsonify({'status': 'success', 'group_id': group_id})

    return asyncio.run(run())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
