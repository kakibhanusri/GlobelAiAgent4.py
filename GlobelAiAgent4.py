import os
import time
import requests
import xml.etree.ElementTree as ET
import re
import threading
from datetime import datetime
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton  
from google import genai  
from difflib import SequenceMatcher
from pymongo import MongoClient
from flask import Flask # 🌐 వెబ్ సర్వీస్ కోసం ఫ్లాస్క్ ముక్క సర్

# --- 🌐 Render Web Service కోసం చిన్న ఫ్లాస్క్ సెటప్ ---
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 AI Market Research Bot is running 24/7 on Render Web Service!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)  

# =====================================================================
# 🌟 Render Environment Variables నుండి కీలను లోడ్ చేసే సెటప్ (🔒 సేఫ్ మోడ్)
# =====================================================================
MY_GEMINI_API_KEY_1 = os.environ.get("MY_GEMINI_API_KEY_1")
MY_GEMINI_API_KEY_2 = os.environ.get("MY_GEMINI_API_KEY_2")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
YOUR_TELEGRAM_CHAT_ID = os.environ.get("YOUR_TELEGRAM_CHAT_ID")

MONGO_URI = os.environ.get("MONGO_URI")

# --- 💾 మొంగోడిబి డేటాబేస్ సెటప్ ---
db = None
news_collection = None

try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
    db = mongo_client["MarketAiBotDB"]        
    news_collection = db["processed_research_news"]    
    mongo_client.server_info()
    print("✅ రీసెర్చ్ క్లౌడ్ డేటాబేస్ (MongoDB Atlas) కనెక్ట్ అయింది సర్!")
except:
    print("ℹ️ మొంగోడిబి ఆఫ్‌లైన్ - బాట్ లోకల్ రామ్ (RAM) బ్యాకప్‌తో నడుస్తోంది సర్.")

# --- 🧠 గూగుల్ అఫీషియల్ జెమిని క్లయింట్ సెటప్ ---
client_key1 = genai.Client(api_key=MY_GEMINI_API_KEY_1)
client_key2 = genai.Client(api_key=MY_GEMINI_API_KEY_2)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
local_processed_news = []
analysis_vault = {}

def get_text_match_percentage(text1, text2):
    return SequenceMatcher(None, text1, text2).ratio() * 100

def clean_main_content(text):
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return " ".join(text.split())

# పెద్ద విశ్లేషణలు పంపేటప్పుడు ముక్కలు చేసే సేఫ్ ఫంక్షన్ సర్
def send_split_message(chat_id, text_to_send):
    try:
        if len(text_to_send) <= 4000:
            bot.send_message(chat_id, text_to_send)
        else:
            for i in range(0, len(text_to_send), 4000):
                bot.send_message(chat_id, text_to_send[i:i+4000])
                time.sleep(1)
    except Exception as telegram_err:
        print(f"⚠️ టెలిగ్రామ్ మెసేజ్ పంపడంలో లోపం: {telegram_err}")

# =====================================================================
# 📰 Continuous Macro & Sector Surveillance Team (లైవ్ అలర్ట్స్ విత్ ఇన్‌లైన్ బటన్)
# =====================================================================
def live_research_surveillance_worker():
    global local_processed_news, analysis_vault
    print("🕵️‍♂️ Live Research Team నిరంతర నిఘా యాక్టివ్‌గా ఉంది సర్...")
    
    macro_feeds = [
        ("ET_Markets_Global", "https://economictimes.indiatimes.com/markets/rssfeeds/2146842.cms"),
        ("Moneycontrol_Economy", "https://www.moneycontrol.com/rss/economy.xml"),
        ("Investing_Analysis", "https://in.investing.com/rss/news_286.rss")
    ]
    
    while True:
        try:
            collected_news = []
            headers = {"User-Agent": "Mozilla/5.0"}
            
            for source_name, url in macro_feeds:
                try:
                    response = requests.get(url, headers=headers, timeout=6)
                    if response.status_code == 200:
                        root = ET.fromstring(response.content)
                        items = root.findall('.//item')
                        for item in items[:8]:
                            title = item.find('title').text or ""
                            desc = item.find('description').text or ""
                            clean_desc = re.sub('<[^<]+?>', '', desc)
                            full_text = f"{title} {clean_desc}".strip()
                            if full_text: collected_news.append((source_name, title, full_text))
                except: continue

            if not collected_news:
                time.sleep(180)
                continue

            for source, raw_title, news_text in collected_news:
                current_clean_content = clean_main_content(news_text)
                
                is_duplicate = False
                if news_collection is not None:
                    try:
                        db_news = list(news_collection.find().sort("_id", -1).limit(200))
                        for old_news in db_news:
                            if get_text_match_percentage(current_clean_content, old_news["content"]) >= 90.0:
                                is_duplicate = True
                                break
                    except:
                        is_duplicate = any(get_text_match_percentage(current_clean_content, old) >= 90.0 for old in local_processed_news)
                else:
                    is_duplicate = any(get_text_match_percentage(current_clean_content, old) >= 90.0 for old in local_processed_news)
                
                if is_duplicate: continue
                
                if news_collection is not None:
                    try: news_collection.insert_one({"content": current_clean_content, "time": datetime.now()})
                    except: pass
                local_processed_news.append(current_clean_content)
                if len(local_processed_news) > 300: local_processed_news.pop(0)
                
                time.sleep(1.5) # మీ ఐడియా గ్యాప్ సర్ 🌟
                
                prompt = f"""nuvvu oka Senior Global Research Analyst vi. 
                ఈ పరిణామాన్ని విశ్లేషించు: {news_text}
                ఇది సాధారణ కంపెనీ వార్త లేదా చిన్న కదలిక అయితే 'NOT_IMPORTANT' అని రాయి. 
                ఒకవేళ ఇది గ్లోబల్ మేక్రో, సెక్టార్ రొటేషన్ లేదా పాలసీలను శాసించగల హై-క్వాలిటీ విషయం అయితే... 
                ముందుగా [ONE_LINE] అనే టాగ్ పెట్టి కేవలం ఒకే ఒక్క లైన్ లో క్విక్ విశ్లేషణ రాయి. 
                ఆ తర్వాత [DEEP_ANALYSIS] అనే టాగ్ పెట్టి, ఒక బిగ్ ఇన్వెస్టర్ మైండ్‌సెట్ తో దీని వెనుక ఉన్న అసలు కారణం ఏంటి, మార్కెట్ పై దీని దీర్ఘకాలిక ప్రభావం ఎలా ఉంటుంది అనేది చాలా అద్భుతమైన, సుదీర్ఘమైన పూర్తి తెలుగు విశ్లేషణను కింద వివరించు సర్."""
                
                try:
                    response = client_key1.models.generate_content(model='gemini-2.5-flash', contents=prompt)
                    agent_output = response.text.strip()
                except Exception as api_err:
                    time.sleep(5)
                    continue
                
                if "NOT_IMPORTANT" not in agent_output and "[DEEP_ANALYSIS]" in agent_output:
                    parts = agent_output.split("[DEEP_ANALYSIS]")
                    one_line_part = parts[0].replace("[ONE_LINE]", "").replace("HIGH_IMPACT", "").strip()
                    deep_analysis_part = parts[1].strip()
                    
                    msg_id = f"macro_{int(time.time())}"
                    analysis_vault[msg_id] = {
                        "title": raw_title,
                        "source": source,
                        "content": deep_analysis_part
                    }
                    
                    markup = InlineKeyboardMarkup()
                    view_btn = InlineKeyboardButton(text="🔎 పూర్తి విశ్లేషణ చదవండి (Read Full View)", callback_data=msg_id)
                    markup.add(view_btn)
                    
                    short_telegram_msg = f"📢 **రీసెర్చ్ టీమ్ లైవ్ అలర్ట్**\n\n" \
                                         f"🗞️ **వార్త శీర్షిక:** {raw_title}\n" \
                                         f"🌐 **మూలం:** {source}\n" \
                                         f"💡 **క్విక్ వ్యూ:** {one_line_part}"
                                         
                    bot.send_message(YOUR_TELEGRAM_CHAT_ID, short_telegram_msg, reply_markup=markup)
                    time.sleep(2)
                    
            print(f"📡 నిరంతర నిఘా లూప్ ముగిసింది. బాట్ అలర్ట్‌గా రన్ అవుతోంది సర్...")
            
        except Exception as e:
            print(f"⚠️ Live Research లూప్‌లో చిన్న అంతరాయం: {e}")
            
        time.sleep(180)

# =====================================================================
# 🚀 మాస్టర్ కమాండ్ సెంటర్ - కమాండ్ లిస్ట్ మరియు చాట్ లాజిక్
# =====================================================================
if __name__ == "__main__":
    start_msg = "🤖 **బిగ్ ఇన్వెస్టర్ AI రీసెర్చ్ & ఆల్ఫా స్టాక్ టీమ్ సిద్ధం సర్!**\n\n" \
                "💡 **ముఖ్య గమనిక:** కమాండ్స్ అన్నీ గుర్తుపెట్టుకోవడం కష్టమైతే చాట్‌లో `/help` అని టైప్ చేయండి సర్. మన బాట్ కమాండ్స్ లిస్ట్ మొత్తం పంపుతుంది."
    
    print(start_msg)
    try: bot.send_message(YOUR_TELEGRAM_CHAT_ID, start_msg)
    except: pass
    
    # 1. 🌐 Flask వెబ్ సర్వర్‌ను ఒక విడి థ్రెడ్‌లో స్టార్ట్ చేస్తున్నాం సర్ (Render Web Service కోసం)
    threading.Thread(target=run_flask, daemon=True).start()

    threading.Thread(target=live_research_surveillance_worker, daemon=True).start()

    # 📋 1. కమాండ్ లిస్ట్ కోసం ప్రత్యేకమైన హ్యాండ్లర్ సర్
    @bot.message_handler(commands=['help', 'start'])
    def send_command_list(message):
        help_text = "📋 **AI రీసెర్చ్ బాట్ కమాండ్స్ లిస్ట్ సర్:**\n\n" \
                    "కింద ఉన్న పదాల మీద ఒక్కసారి టచ్ (Touch/Click) చేయండి సర్, అది ఆటోమేటిక్‌గా కాపీ అయిపోతుంది. దాన్ని కింద పేస్ట్ చేసి పంపేయండి:\n\n" \
                    "🌍 **మార్కెట్ ముఖ్య విషయాల కోసం:**\n" \
                    "`eeroju market updates`\n\n" \
                    "🎯 **ఆల్ఫా స్టాక్ పిక్స్ కోసం:**\n" \
                    "`eeroju stock picks`\n\n" \
                    "ℹ️ _గమనిక: మీరు వాట్సాప్ లాగా ఇంగ్లీష్ అక్షరాలతో టైప్ చేసినా బాట్ అర్థం చేసుకుంటుంది సర్!_"
        bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

    # 🌟 బటన్ క్లిక్ చేసినప్పుడు పూర్తి విశ్లేషణను పంపే లాజిక్
    @bot.callback_query_handler(func=lambda call: True)
    def callback_listener(call):
        global analysis_vault
        msg_key = call.data
        if msg_key in analysis_vault:
            bot.answer_callback_query(call.id, text="🧠 పూర్తి విశ్లేషణను లోడ్ చేస్తున్నాను సర్...")
            vault_data = analysis_vault[msg_key]
            full_report = f"📊 **పూర్తి రీసెర్చ్ నివేదిక (Detailed Insights)**\n" \
                          f"🗞 *వార్త:* {vault_data['title']}\n" \
                          f"🌐 *మూలం:* {vault_data['source']}\n" \
                          f"--------------------------------------------------\n\n" \
                          f"{vault_data['content']}"
            send_split_message(call.message.chat.id, full_report)
        else:
            bot.answer_callback_query(call.id, text="❌ ఈ విశ్లేషణ పాతదవడం వల్ల మెమొరీ నుండి డిలీట్ అయింది సర్.")

    # 💬 యూజర్ అడిగినప్పుడు ఆన్-డిమాండ్ స్పందించే లాజిక్
    @bot.message_handler(func=lambda message: True)
    def handle_user_research_query(message):
        user_query = message.text
        bot.reply_to(message, f"🧠 ఓకే సర్, మన రీసెర్చ్ టీమ్ హెడ్ (Chief Analyst) రంగంలోకి దిగి మొత్తం మార్కెట్ డేటాను విశ్లేషిస్తున్నారు సర్...")
        
        analysis_prompt = f"""nuvvu oka leading global hedge fund ki 'Chief Portfolio Manager' mariyu 'Research Head' vi. 
        ಯూజర్ అడిగిన ప్రశ్న/విషయం: {user_query}
        
        ఒకవేళ యూజర్ ఈరోజు మార్కెట్ ప్రత్యేకతలు లేదా స్టాక్ పిక్స్ (Stock Picks) గురించి అడిగితే... రోజువారీ ముడి వార్తలు, గ్లోబల్ మేక్రో ట్రెండ్స్ మరియు సెక్టార్ రొటేషన్స్ అన్నింటినీ విశ్లేషించి:
        
        1. భవిష్యత్తులో (Future లో) తిరుగులేని వృద్ధి సాధించగల, మల్టీబ్యాగర్ అవ్వగల గరిష్టంగా '1 లేదా 2 స్టాక్స్' మాత్రమే ఏరి కోరి సెలెక్ట్ చేయి.
        2. ఆ సెలెక్ట్ చేసిన స్టాక్స్ కి సంబంధించి ఈ కింది 5 పరామితులను చాలా లోతుగా, పక్కా విశ్లేషణతో తెలుగులో వివరించు సర్:
           - (A) ఫండమెంటల్స్ (Financial Strength & Margin)
           - (B) టెక్నికల్స్ (Chart Structure & Breakout)
           - (C) సెక్టారియల్ వ్యూ (Sector Growth & Demand)
           - (D) మేనేజ్‌మెంట్ & బిజినెస్ మోడల్ (Management Quality)
           - (E) ఫ్యూチャー కాటలిస్ట్ (Future Growth & Orders)
           
        3. ఒకవేళ ఈరోజు మార్కెట్ కండిషన్స్ ప్రకారం అంతటి క్వాలిటీ, నూటికి నూరు పాళ్ళు నమ్మకమైన స్టాక్ ఏదీ దొరకకపోతే... 'సార్, ఈరోజు అంతటి బలమైన, తిరుగులేని స్టాక్ ఏదీ రీసెర్చ్ టీమ్‌కు దొరకలేదు సర్' అని చాలా స్పష్టంగా ఒకే ముక్కలో సమాధానం చెప్పు. అనవసరమైన నార్మల్ స్టాక్స్ అస్సలు రికమండ్ చేయొద్దు. క్వాలిటీ ముఖ్యం."""
        
        try:
            response = client_key2.models.generate_content(model='gemini-2.5-flash', contents=analysis_prompt)
            send_split_message(message.chat.id, response.text)
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ ఎర్రర్: {e}")

    bot.infinity_polling()