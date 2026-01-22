import discord
from discord.ext import commands, tasks
import os, random, requests, json
from flask import Flask
from threading import Thread

# --- إعداد الويب ---
app = Flask('')
@app.route('/')
def home(): return "<h1>Azkar Bot: All-in-One API Active</h1>"

def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- إعداد البوت ---
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

# قاعدة بيانات القنوات
server_channels = {}

# وظيفة لجلب "كل" فهرس الأبواب من حصن المسلم
def get_all_sections():
    try:
        url = "https://www.hisnmuslim.com/api/ar/husn_ar.json"
        res = requests.get(url, timeout=10)
        return res.json()['العربية'] # يعيد قائمة بكل الأبواب (ID واسم الباب)
    except:
        return []

def get_athkar_by_id(s_id):
    try:
        url = f"https://www.hisnmuslim.com/api/ar/{s_id}.json"
        res = requests.get(url, timeout=10)
        data = res.json()
        key = list(data.keys())[0]
        return data[key] # يعيد قائمة الأذكار داخل هذا الباب
    except:
        return []

@bot.event
async def on_ready():
    print(f'✅ {bot.user} متصل ويشمل كامل الـ API')
    auto_sender.start()

# --- الأوامر الجديدة ---

@bot.command(name="الأبواب", aliases=['sections', 'categories'])
async def list_sections(ctx):
    """عرض قائمة ببعض أبواب حصن المسلم المتاحة"""
    sections = get_all_sections()
    # سنعرض أول 20 باباً كمثال لعدم إطالة الرسالة
    text = "\n".join([f"**{s['ID']}** - {s['TITLE']}" for s in sections[:20]])
    embed = discord.Embed(title="📚 فهرس حصن المسلم (أمثلة)", description=text, color=0x3498db)
    embed.set_footer(text="استخدم !z مع رقم الباب لعرض أذكاره")
    await ctx.send(embed=embed)

@bot.command(aliases=['ذكر', 'z'])
async def thker(ctx, section_id: int = None):
    """
    !z -> ذكر عشوائي تماماً من أي باب في الكتاب
    !z 27 -> أذكار الصباح
    """
    if section_id is None:
        # اختيار باب عشوائي من كل الأبواب المتاحة في الـ API
        sections = get_all_sections()
        section_id = random.choice(sections)['ID']
    
    athkar_list = get_athkar_by_id(section_id)
    if athkar_list:
        item = random.choice(athkar_list)
        embed = discord.Embed(title=item['TITLE'], description=item['ARABIC_TEXT'], color=0xe94560)
        if item['TRANSLITERATION']:
            embed.add_field(name="ملاحظة", value=item['NOTES'] or "لا يوجد", inline=False)
        embed.set_footer(text=f"المصدر: حصن المسلم | رقم الباب: {section_id}")
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ عذراً، لم أتمكن من جلب البيانات لهذا القسم.")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx, channel: discord.TextChannel):
    server_channels[str(ctx.guild.id)] = channel.id
    await ctx.send(f"✅ تم بنجاح ضبط {channel.mention} للإرسال التلقائي الشامل.")

@tasks.loop(minutes=60)
async def auto_sender():
    for guild_id, ch_id in server_channels.items():
        channel = bot.get_channel(ch_id)
        if channel:
            # اختيار عشوائي حقيقي من كامل الكتاب
            sections = get_all_sections()
            s_id = random.choice(sections)['ID']
            athkar = get_athkar_by_id(s_id)
            if athkar:
                item = random.choice(athkar)
                embed = discord.Embed(title=f"🔔 {item['TITLE']}", description=item['ARABIC_TEXT'], color=0x2ecc71)
                await channel.send(embed=embed)

if __name__ == "__main__":
    keep_alive()
    bot.run(os.environ.get('DISCORD_TOKEN'))
