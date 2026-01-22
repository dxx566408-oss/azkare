import discord
import os
from flask import Flask
from threading import Thread

# خادم ويب بسيط لـ Render
app = Flask('')
@app.route('/')
def home(): return "<h1>Bot is Listening...</h1>"
def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# استخدام Intents.all() لكسر أي قيود
intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ تم الاتصال بنجاح باسم: {client.user}')
    print(f'✅ أنا الآن موجود في {len(client.guilds)} سيرفر')

@client.event
async def on_message(message):
    # سيطبع في الـ Logs أي رسالة يراها البوت حتى لو كانت من بوت آخر
    print(f"📡 استلمت إشارة: '{message.content}' من {message.author}")
    
    if message.author == client.user:
        return

    # الرد المباشر لتأكيد العمل
    try:
        await message.channel.send(f"أسمعك بوضوح! كتبت: {message.content}")
    except Exception as e:
        print(f"❌ فشلت في الرد بسبب: {e}")

keep_alive()
client.run(os.environ.get('DISCORD_TOKEN'))
