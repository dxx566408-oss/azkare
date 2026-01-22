import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- إعداد الويب لـ Render ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- إعداد البوت ---
# ملاحظة: تأكد من تفعيل MESSAGE CONTENT من موقع المطورين
intents = discord.Intents.all() # سنستخدم 'all' هذه المرة لضمان تشغيل كل شيء

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ سجلت الدخول باسم: {bot.user}')

# هذا الحدث سيرد على أي رسالة ترسلها مهما كان محتواها للتجربة
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # إذا كتبت أي شيء، سيرد عليك البوت لتأكيد أنه "يسمعك"
    if message.content:
        print(f"وصلتني رسالة: {message.content}")
        # await message.channel.send(f"لقد استلمت رسالتك: {message.content}") # جرب تفعيل هذا السطر لاحقاً

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

# --- التشغيل ---
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('DISCORD_TOKEN')
    bot.run(token)
