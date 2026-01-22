import discord
from discord.ext import commands, tasks
import os, random
from flask import Flask
from threading import Thread

# --- إعداد الويب لـ Render ---
app = Flask('')
@app.route('/')
def home(): return "Dashboard is Running!"

def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# --- إعداد البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# تخزين القنوات (ملاحظة: للحفاظ عليها للأبد سنحتاج MongoDB لاحقاً)
server_channels = {}

azkar_db = {
    "صباح": ["أصبحنا وأصبح الملك لله", "اللهم بك أصبحنا"],
    "مساء": ["أمسينـا وأمسى الملك لله", "اللهم بك أمسينا"],
    "تسبيح": ["سبحان الله وبحمده", "سبحان الله العظيم"],
    "حديث": ["قال ﷺ: خيركم من تعلم القرآن وعلمه"]
}

@bot.event
async def on_ready():
    print(f'✅ {bot.user} جاهز للعمل!')
    auto_athkar.start()

# --- الأوامر المباشرة ---

@bot.command(aliases=['ذكر', 'z'])
async def thker(ctx):
    """أمر ذكر فوري باختصارات !z أو !ذكر"""
    category = random.choice(list(azkar_db.keys()))
    await ctx.send(f"✨ **{category}:** {random.choice(azkar_db[category])}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx, channel: discord.TextChannel):
    """تحديد قناة معينة للأذكار تلقائياً !setup #channel"""
    server_channels[ctx.guild.id] = channel.id
    await ctx.send(f"✅ تم ضبط قناة الأذكار على {channel.mention}")

# --- نظام الإرسال التلقائي كل ساعة ---
@tasks.loop(hours=1)
async def auto_athkar():
    for guild_id, ch_id in server_channels.items():
        channel = bot.get_channel(ch_id)
        if channel:
            category = random.choice(list(azkar_db.keys()))
            await channel.send(f"🔔 **أذكار تلقائية:**\n> {random.choice(azkar_db[category])}")

keep_alive()
bot.run(os.environ.get('DISCORD_TOKEN'))
