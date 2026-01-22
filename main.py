import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# إعداد الويب لـ Render
app = Flask('')
@app.route('/')
def home(): return "<h1>The Bot is Active!</h1>"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# إعدادات البوت
intents = discord.Intents.default()
intents.message_content = True  # تأكد مرة أخرى أنك فعلتها في موقع المطورين
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ تم تشغيل: {bot.user}')
    print(f'✅ البوت موجود في {len(bot.guilds)} سيرفر')

# كود التشخيص: يطبع أي رسالة يراها البوت في الـ Logs
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    print(f"📩 رسالة مستلمة: {message.content} من {message.author}")
    await bot.process_commands(message) # ضروري جداً لتشغيل الأوامر

@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! البوت شغال يا صاحبي.")

# تشغيل الويب والبوت
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('DISCORD_TOKEN')
    bot.run(token)
