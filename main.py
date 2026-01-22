import discord
from discord.ext import commands, tasks
from quart import Quart, render_template, request, session, redirect
import os
import asyncio
import random

# --- إعداد الموقع (Dashboard) ---
app = Quart(__name__)
app.secret_key = "secret_key_for_session" # غير هذا لاحقاً

# --- إعداد البوت ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# بيانات افتراضية (يفضل ربطها بـ MongoDB لاحقاً)
db_data = {} 

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    send_auto_athkar.start()

# --- أوامر الديسكورد ---
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx, channel: discord.TextChannel):
    """أمر اختيار القناة كما في بروبوت"""
    db_data[ctx.guild.id] = {"channel": channel.id, "type": "all"}
    await ctx.send(f"✅ تم ضبط قناة الأذكار على: {channel.mention}")

@bot.command()
async def thker(ctx):
    """أمر إرسال ذكر فوري"""
    athkar = ["سبحان الله", "الحمد لله", "لا إله إلا الله"]
    await ctx.send(random.choice(athkar))

# --- نظام الجدولة (إرسال تلقائي) ---
@tasks.loop(minutes=30)
async def send_auto_athkar():
    for guild_id, settings in db_data.items():
        channel = bot.get_channel(settings['channel'])
        if channel:
            await channel.send("💡 ذكر تلقائي: سبحان الله وبحمده")

# --- مسارات الموقع (Dashboard Routes) ---
@app.route('/')
async def index():
    return "<h1>Azkar Bot Dashboard</h1><p>الموقع قيد التطوير...</p>"

@app.route('/settings/<int:guild_id>', methods=['POST'])
async def update_settings(guild_id):
    # هنا يتم استقبال البيانات من الموقع لتغيير نوع الأذكار أو القناة
    data = await request.form
    db_data[guild_id]['type'] = data.get('athkar_type')
    return "تم التحديث بنجاح!"

# --- تشغيل الموقع والبوت معاً ---
@bot.event
async def on_resumed():
    print("Bot resumed")

async def main():
    # تشغيل البوت والموقع في نفس الوقت
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start(os.getenv("DISCORD_TOKEN")))
    await app.run_task(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    asyncio.run(main())
