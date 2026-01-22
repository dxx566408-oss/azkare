import discord
from discord.ext import commands, tasks
import os, random, requests
from flask import Flask, render_template_string
from threading import Thread

# --- 1. إعداد خادم الويب (لوحة التحكم) ---
app = Flask('')

# واجهة بسيطة للوحة التحكم (HTML)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>لوحة تحكم بوت الأذكار</title>
    <style>
        body { background-color: #1a1a2e; color: white; font-family: sans-serif; text-align: center; padding: 50px; }
        .card { background: #16213e; padding: 20px; border-radius: 15px; display: inline-block; border: 1px solid #0f3460; }
        h1 { color: #e94560; }
        .status { color: #4ee44e; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🌙 بوت أذكار حصن المسلم</h1>
        <p>حالة البوت الآن: <span class="status">متصل (Online)</span></p>
        <hr>
        <p>استخدم الأوامر في ديسكورد للتحكم:</p>
        <ul style="list-style: none; padding: 0;">
            <li><code>!z</code> - ذكر عشوائي</li>
            <li><code>!z 27</code> - أذكار الصباح</li>
            <li><code>!z 28</code> - أذكار المساء</li>
            <li><code>!setup #channel</code> - ضبط القناة التلقائية</li>
        </ul>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. إعداد البوت وربطه بـ API حصن المسلم ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# قاعدة بيانات بسيطة لحفظ قنوات السيرفرات
server_configs = {} 

def get_hisn_data(id):
    """جلب الأذكار من API حصن المسلم بناءً على القسم"""
    try:
        url = f"https://www.hisnmuslim.com/api/ar/{id}.json"
        res = requests.get(url)
        data = res.json()
        # استخراج القائمة من مفتاح القسم (مثل 'أذكار الصباح')
        key = list(data.keys())[0]
        athkar_list = data[key]
        item = random.choice(athkar_list)
        return item['ARABIC_TEXT'], item['TITLE']
    except Exception as e:
        print(f"Error fetching API: {e}")
        return "سبحان الله وبحمده", "ذكر"

@bot.event
async def on_ready():
    print(f'✅ متصل باسم: {bot.user}')
    auto_sender.start()

# --- 3. الأوامر ---

@bot.command(aliases=['ذكر', 'z'])
async def athkar(ctx, section_id: int = None):
    """
    !z -> ذكر عشوائي من الصباح أو المساء
    !z 27 -> أذكار الصباح حصراً
    """
    # إذا لم يحدد ID، يختار عشوائياً بين الصباح (27) والمساء (28)
    s_id = section_id if section_id else random.choice([27, 28])
    text, title = get_hisn_data(s_id)
    
    embed = discord.Embed(title=title, description=text, color=0xe94560)
    embed.set_footer(text="المصدر: حصن المسلم")
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx, channel: discord.TextChannel):
    """ضبط القناة للإرسال التلقائي"""
    server_configs[ctx.guild.id] = channel.id
    await ctx.send(f"✅ تم اختيار {channel.mention} لإرسال أذكار حصن المسلم تلقائياً كل ساعة.")

# --- 4. المهام التلقائية ---
@tasks.loop(hours=1)
async def auto_sender():
    for guild_id, ch_id in server_configs.items():
        channel = bot.get_channel(ch_id)
        if channel:
            text, title = get_hisn_data(random.choice([27, 28]))
            embed = discord.Embed(title=f"🔔 {title}", description=text, color=0x4ee44e)
            await channel.send(embed=embed)

# --- 5. التشغيل النهائي ---
if __name__ == "__main__":
    keep_alive()
    token = os.environ.get('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN في إعدادات رندر")
