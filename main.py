import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# خادم وهمي لـ Render
app = Flask('')
@app.route('/')
def home(): return "I am alive!"

def run(): app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# إعداد البوت
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is online!')

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! 🏓")

# التشغيل
if __name__ == "__main__":
    keep_alive() # تشغيل الويب أولاً
    token = os.environ.get('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ Token not found!")
