import discord
from discord.ext import commands, tasks
import os, random, requests
from flask import Flask
from threading import Thread

# --- إعداد الويب ---
app = Flask('')
@app.route('/')
def home(): return "Dashboard is Online!"

def keep_alive():
    Thread(target=lambda: app.run(host='0.0.0.0', port=8080)).start()

# --- إعداد البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# رابط API للأذكار (مثال لقاعدة بيانات شاملة)
AZKAR_URL = "https://raw.githubusercontent.com/osamayat/azkar-db/master/azkar.json"

def get_random_thker(category=None):
    try:
        response = requests.get(AZKAR_URL)
        data = response.json()
        if category:
            # فلترة الأذكار حسب الفئة (صباح، مساء، إلخ)
            filtered = [a for a in data if category in a['category']]
            return random.choice(filtered)['content'] if filtered else "لم يتم العثور على ذكر في هذه الفئة."
        return random.choice(data)['content']
    except:
        return "سبحان الله وبحمده" # ذكر احتياطي في حال تعطل الـ API

# --- الأوامر ---

@bot.command(aliases=['ذكر', 'z'])
async def thker(ctx, category: str = None):
    """
    أمر الذكر:
    !z -> ذكر عشوائي
    !z صباح -> ذكر من أذكار الصباح
    """
    msg = get_random_thker(category)
    await ctx.send(f"✨ **{category or 'ذكر'}:**\n> {msg}")

@bot.command()
async def hadith(ctx):
    """جلب حديث نبوي عشوائي"""
    # مثال لـ API أحاديث
    res = requests.get("https://ahadith-api.herokuapp.com/api/ahadith/random/ar")
    if res.status_code == 200:
        data = res.json()
        await ctx.send(f"📖 **حديث شريف:**\n> {data['hadith']['hadith_ar']}")
    else:
        await ctx.send("تعذر جلب حديث حالياً، صلِّ على النبي!")

# --- نظام الجدولة (تلقائي) ---
@tasks.loop(hours=1)
async def auto_athkar():
    # هنا تضع منطق إرسال الأذكار للقنوات المسجلة كما فعلنا سابقاً
    pass

keep_alive()
bot.run(os.environ.get('DISCORD_TOKEN'))
