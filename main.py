import discord
from discord.ext import commands, tasks
import os
import random
from flask import Flask
from threading import Thread

# --- 1. إعداد الويب لضمان الاستمرارية (Keep Alive) ---
app = Flask('')
@app.route('/')
def home(): return "<h1>Azkar Bot is Running!</h1>"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. إعدادات البوت والـ Intents ---
intents = discord.Intents.default()
intents.message_content = True  # ضروري جداً لكي يستجيب البوت للأوامر
intents.guilds = True

# تعريف البوت مع إمكانية استخدام اختصارات (Prefixes)
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# قاعدة بيانات بسيطة (في الذاكرة) - ستفقد البيانات عند إعادة تشغيل رندر
# لتجنب ذلك مستقبلاً سنحتاج لربط MongoDB
server_settings = {} 

# أذكار متنوعة
azkar_db = {
    "صباح": ["أصبحنا وأصبح الملك لله", "اللهم بك أصبحنا وبك أمسينا"],
    "مساء": ["أمسينـا وأمسى الملك لله", "اللهم بك أمسينا وبك أصبحنا"],
    "تسبيح": ["سبحان الله وبحمده", "سبحان الله العظيم", "لا حول ولا قوة إلا بالله"],
    "صلاة": ["اللهم صل وسلم على نبينا محمد", "اللهم أعني على ذكرك وشكرك وحسن عبادتك"]
}

@bot.event
async def on_ready():
    print(f'✅ {bot.user} متصل وبإمكانه رؤية الرسائل!')
    auto_sender.start() # تشغيل مؤقت الأذكار التلقائي

# --- 3. الأوامر (Commands) ---

# أمر Ping للتجربة
@bot.command()
async def ping(ctx):
    await ctx.send(f"🏓 Pong! (Latency: {round(bot.latency * 1000)}ms)")

# أمر ضبط القناة (مثل بروبوت)
@bot.command(aliases=['ضبط', 'set'])
@commands.has_permissions(administrator=True)
async def setup(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    server_settings[ctx.guild.id] = {
        "channel_id": channel.id,
        "interval": 60, # افتراضي كل ساعة
        "type": "الكل"
    }
    await ctx.send(f"✅ تم تحديد القناة {channel.mention} لإرسال الأذكار تلقائياً.")

# أمر إرسال ذكر فوري مع اختصارات
@bot.command(aliases=['ذكر', 'z', 'athkar'])
async def thker(ctx):
    # دمج كل الأذكار واختيار واحد عشوائي
    all_lists = [item for sublist in azkar_db.values() for item in sublist]
    await ctx.send(f"✨ **ذكر فوري:** {random.choice(all_lists)}")

# --- 4. نظام الإرسال التلقائي ---
@tasks.loop(minutes=60)
async def auto_sender():
    for guild_id in server_settings:
        config = server_settings[guild_id]
        channel = bot.get_channel(config["channel_id"])
        if channel:
            # اختيار ذكر عشوائي من أي قائمة
            category = random.choice(list(azkar_db.keys()))
            message = random.choice(azkar_db[category])
            await channel.send(f"🔔 **أذكار تلقائية ({category}):**\n> {message}")

# --- 5. التشغيل ---
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('DISCORD_TOKEN')
    bot.run(token)
