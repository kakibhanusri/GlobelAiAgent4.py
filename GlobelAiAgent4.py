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
from flask import Flask 

# --- 🌐 Render Web Service కోసం చిన్న ఫ్లాస్క్ సెటప్ ---
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 AI Master Local RAM Smart Bot with Detailed Logs is running 24/7 on Render!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)  

# =====================================================================
# 🌟 Render Environment Variables నుండి కీలను లోడ్ చేసే సెటప్ (🔒 సేఫ్ అండ్ ఫాస్ట్ మోడ్)
# =====================================================================
MY_GEMINI_API_KEY_1 = os.environ.get("MY_GEMINI_API_KEY_1")
MY_GEMINI_API_KEY_2 = os.environ.get("MY_GEMINI_API_KEY_2")

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
YOUR_TELEGRAM_CHAT_ID = os.environ.get("YOUR_TELEGRAM_CHAT_ID")    

# --- 🧠 గూగుల్ అఫీషియల్ జెమిని క్లయింట్ సెటప్ ---
client_key1 = genai.Client(api_key=MY_GEMINI_API_KEY_1)
client_key2 = genai.Client(api_key=MY_GEMINI_API_KEY_2)

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# 💾 కేవలం లోకల్ ర్యామ్ (RAM) మెమొరీ మాత్రమే
local_processed_news = []
analysis_vault = {}

def get_text_match_percentage(text1, text2):
    return SequenceMatcher(None, text1, text2).ratio() * 100

def clean_main_content(text):
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    return " ".join(text.split())

# 🌟 టెలిగ్రామ్ ఎర్రర్ రాకుండా టెక్స్ట్ క్లీన్ చేసే సేఫ్ HTML ఫంక్షన్
def clean_for_html(text):
    if not text:
        return ""
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    return text

# విశ్లేషణలు ముక్కలు చేసే సేఫ్ ఫంక్షన్ (HTML మోడ్‌లో)
def send_split_message(chat_id, text_to_send):
    try:
        safe_text = clean_for_html(text_to_send)
        if len(safe_text) <= 4000:
            bot.send_message(chat_id, safe_text, parse_mode="HTML")
        else:
            for i in range(0, len(safe_text), 4000):
                bot.send_message(chat_id, safe_text[i:i+4000], parse_mode="HTML")
                time.sleep(1)
    except Exception as telegram_err:
        print(f"⚠️ టెలిగ్రామ్ మెసేజ్ పంపడంలో లోపం: {telegram_err}")

# =====================================================================
# 📰 Continuous Macro & Sector Surveillance Team (🔒 లైవ్ లాగ్స్ సిస్టమ్ తో)
# =====================================================================
def live_research_surveillance_worker():
    global local_processed_news, analysis_vault
    print("\n🕵️‍♂️ [START] Live Research Team నిరంతర నిఘా లూప్ ప్రారంభమైంది సర్...")
    
    macro_feeds = [
        ("ET_Markets_Global", "https://economictimes.indiatimes.com/markets/rssfeeds/2146842.cms"),
        ("Moneycontrol_Economy", "https://www.moneycontrol.com/rss/economy.xml"),
        ("Investing_Analysis", "https://in.investing.com/rss/news_286.rss")
    ]
    
    while True:
        try:
            collected_news = []
            headers = {"User-Agent": "Mozilla/5.0"}
            
            print(f"\n🔄 [{datetime.now().strftime('%H:%M:%S')}] RSS ფీడ్స్ నుండి వార్తలను సేకరిస్తున్నాను...")
            for source_name, url in macro_feeds:
                try:
                    response = requests.get(url, headers=headers, timeout=6)
                    if response.status_code == 200:
                        root = ET.fromstring(response.content)
                        items = root.findall('.//item')
                        feed_count = 0
                        for item in items[:8]:
                            title = item.find('title').text or ""
                            desc = item.find('description').text or ""
                            clean_desc = re.sub('<[^<]+?>', '', desc)
                            full_text = f"{title} {clean_desc}".strip()
                            if full_text: 
                                collected_news.append((source_name, title, full_text))
                                feed_count += 1
                        print(f"📥 {source_name} నుండి {feed_count} వార్తలు సేకరించాను.")
                except Exception as feed_err: 
                    print(f"❌ {source_name} ఫీడ్ కనెక్ట్ చేయడంలో లోపం: {feed_err}")
                    continue

            print(f"📊 మొత్తం సేకరించిన రా (Raw) వార్తల సంఖ్య: {len(collected_news)}")

            if not collected_news:
                print("💤 వార్తలు ఏవీ దొరకలేదు సర్. 3 నిమిషాల గ్యాప్ తీసుకుంటున్నాను...")
                time.sleep(180)
                continue

            # --- వార్తలను ప్రాసెస్ చేసే మెయిన్ లూప్ సర్ ---
            for source, raw_title, news_text in collected_news:
                print(f"\n📰 [ప్రాసెస్ అవుతోంది] శీర్షిక: {raw_title[:60]}... ({source})")
                current_clean_content = clean_main_content(news_text)
                
                # 🔒 100% లోకల్ ర్యామ్ (RAM) డూప్లికేట్ చెక్ లాజిక్
                is_duplicate = any(get_text_match_percentage(current_clean_content, old) >= 90.0 for old in local_processed_news)
                
                if is_duplicate: 
                    print(f"⏩ [SKIP] ఈ వార్త ఇప్పటికే ప్రాసెస్ చేయబడింది (Duplicate Found). వదిలేస్తున్నాను.")
                    continue
                
                # 🌟 మీరు అడిగిన 10 సెకండ్ల సేఫ్టీ గ్యాప్ ఇక్కడ పెట్టాను సర్!
                print(f"⏳ రేట్ లిమిట్ (Rate Limit) రాకుండా ఉండటానికి 10 సెకన్లు ఆగుతున్నాను సర్...")
                time.sleep(10)
                
                print(f"✅ [NEW NEWS] జెమిని AI విశ్లేషణకు పంపుతున్నాను...")
                
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
                    print(f"❌ [GEMINI ERROR] జెమిని తో కనెక్ట్ అవ్వడంలో లోపం: {api_err}")
                    time.sleep(5)
                    continue
                
                if "NOT_IMPORTANT" in agent_output:
                    print(f"📉 [AI REJECTED] జెమిని ఈ వార్తను 'NOT_IMPORTANT' అని రిజెక్ట్ చేసింది సర్.")
                    local_processed_news.append(current_clean_content)
                    if len(local_processed_news) > 300: local_processed_news.pop(0)
                    continue

                if "[DEEP_ANALYSIS]" in agent_output:
                    print(f"🚀 [HIGH IMPACT] అద్భుతమైన వార్త దొరికింది! టెలిగ్రామ్‌కు అలర్ట్ జనరేట్ చేస్తున్నాను...")
                    
                    local_processed_news.append(current_clean_content)
                    if len(local_processed_news) > 300: local_processed_news.pop(0)

                    parts = agent_output.split("[DEEP_ANALYSIS]")
                    one_line_part = parts[0].replace("[ONE_LINE]", "").replace("HIGH_IMPACT", "").strip()
                    deep_analysis_part = parts[1].strip()
                    
                    # HTML సేఫ్ క్లీనింగ్
                    safe_title = clean_for_html(raw_title)
                    safe_source = clean_for_html(source)
                    safe_one_line = clean_for_html(one_line_part)
                    safe_deep = clean_for_html(deep_analysis_part)
                    
                    unique_id = int(time.time() * 1000)
                    msg_id = f"view_{unique_id}"
                    part2_id = f"pt2_{unique_id}"
                    back_id = f"back_{unique_id}"
                    
                    short_telegram_msg = f"📢 <b>రీసెర్చ్ టీమ్ లైవ్ అలర్ట్</b>\n\n" \
                                         f"🗞️ <b>వార్త శీర్షిక:</b> {safe_title}\n" \
                                         f"🌐 <b>మూలం:</b> {safe_source}\n" \
                                         f"💡 <b>క్విక్ వ్యూ:</b> {safe_one_line}"

                    part1_text = safe_deep
                    part2_text = ""
                    if len(safe_deep) > 3500:
                        part1_text = safe_deep[:3500] + "\n\n...(ఇంకా ఉంది సర్, కింద ఉన్న 'Next Part' బటన్ నొక్కండి)..."
                        part2_text = "...(మునుపటి భాగం కొనసాగింపు)...\n\n" + safe_deep[3500:]

                    analysis_vault[msg_id] = {
                        "title": safe_title,
                        "source": safe_source,
                        "part1": part1_text,
                        "part2": part2_text,
                        "original_text": short_telegram_msg,
                        "part2_key": part2_id,
                        "back_key": back_id
                    }
                    analysis_vault[part2_id] = msg_id
                    analysis_vault[back_id] = msg_id
                    
                    markup = InlineKeyboardMarkup()
                    view_btn = InlineKeyboardButton(text="🔎 పూర్తి విశ్లేషణ చదవండి (Read Full View)", callback_data=msg_id)
                    markup.add(view_btn)
                                                         
                    bot.send_message(YOUR_TELEGRAM_CHAT_ID, short_telegram_msg, reply_markup=markup, parse_mode="HTML")
                    print(f"📤 [TELEGRAM SENT] టెలిగ్రామ్‌కు అలర్ట్ విజయవంతంగా పంపబడింది సర్.")
                    time.sleep(2)
                    
                else:
                    print(f"⚠️ [FORMAT MISMATCH] జెమిని నుండి రెస్పాన్స్ వచ్చింది కానీ సరైన టాగ్స్ ([DEEP_ANALYSIS]) లేవు.")
                    
            print(f"\n📡📡 నిరంతర నిఘా లూప్ ముగిసింది. మళ్లీ 3 నిమిషాల తర్వాత చెక్ చేస్తుంది సర్...")
            
        except Exception as e:
            print(f"⚠️ [LOOP EXCEPTION] Live Research లూప్‌లో అంతరాయం: {e}")
            
        time.sleep(180)

# =====================================================================
# 🚀 మాస్టర్ కమాండ్ సెంటర్ - కమాండ్ లిస్ట్ మరియు చాట్ లాజిక్
# =====================================================================
if __name__ == "__main__":
    start_msg = "🤖 <b>AI స్మార్ట్ డ్యూయల్-సిస్టమ్ బాట్ విత్ లైవ్ లాగ్స్ సిస్టమ్ రెడీ సర్!</b>\n\n" \
                "🎯 <b>100% ఇన్‌లైన్ రీప్లేస్ సిస్టమ్:</b> వార్త ఎంత పెద్దదైనా సరే, కింద కొత్త మెసేజ్‌లు రావు. అంతా ఒకే బాక్స్‌లో పార్ట్‌ల రూపంలో రీప్లేస్ అవుతూ బ్యాక్ వెళ్ళే సదుపాయం ఉంటుంది సర్!"
    
    print(start_msg)
    try: bot.send_message(YOUR_TELEGRAM_CHAT_ID, start_msg, parse_mode="HTML")
    except: pass
    
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=live_research_surveillance_worker, daemon=True).start()

    @bot.message_handler(commands=['help', 'start'])
    def send_command_list(message):
        help_text = "📋 <b>AI రీసెర్చ్ బాట్ కమాండ్స్ లిస్ట్ సర్:</b>\n\n" \
                    "కింద ఉన్న పదాల మీద ఒక్కసారి టచ్ చేయండి సర్, ఆటోమేటిక్‌గా కాపీ అవుతుంది:\n\n" \
                    "🌍 <b>మల్టీ-డైమెన్షనల్ మార్కెట్ అప్‌డేట్స్:</b>\n" \
                    "<code>eeroju market updates</code>\n\n" \
                    "🎯 <b>డ్యూయల్ ఆల్ఫా స్టాక్ పిక్స్:</b>\n" \
                    "<code>eeroju stock picks</code>"
        bot.send_message(message.chat.id, help_text, parse_mode="HTML")

    # 🌟 4000 క్యారెక్టర్లు దాటినా కూడా ఒకే బాక్స్‌లో రీప్లేస్ చేసే అల్టిమేట్ బటన్ లాజిక్ సర్!
    @bot.callback_query_handler(func=lambda call: True)
    def callback_listener(call):
        global analysis_vault
        msg_key = call.data
        
        if msg_key in analysis_vault:
            # 1. మొదటిసారి '🔎 పూర్తి విశ్లేషణ చదవండి' నొక్కినప్పుడు (Part 1 లోడ్ అవుతుంది)
            if msg_key.startswith("view_"):
                bot.answer_callback_query(call.id, text="🧠 విశ్లేషణ పార్ట్-1 లోడ్ చేస్తున్నాను సర్...")
                vault_data = analysis_vault[msg_key]
                
                full_report = f"📊 <b>పూర్తి రీసెర్చ్ నివేదిక - Part 1</b>\n" \
                              f"🗞 <i>వార్త:</i> {vault_data['title']}\n" \
                              f"🌐 <i>మూలం:</i> {vault_data['source']}\n" \
                              f"--------------------------------------------------\n\n" \
                              f"{vault_data['part1']}"
                
                markup = InlineKeyboardMarkup()
                if vault_data['part2'] != "":
                    next_btn = InlineKeyboardButton(text="➡️ మిగిలిన భాగం (Next Part)", callback_data=vault_data['part2_key'])
                    markup.add(next_btn)
                back_btn = InlineKeyboardButton(text="⬅️ వెనక్కి వెళ్ళండి (Back to Alert)", callback_data=vault_data['back_key'])
                markup.add(back_btn)
                
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=full_report, reply_markup=markup, parse_mode="HTML")

            # 2. '➡️ మిగిలిన భాగం (Next Part)' బటన్ నొక్కినప్పుడు
            elif msg_key.startswith("pt2_"):
                view_key = analysis_vault[msg_key]
                vault_data = analysis_vault[view_key]
                bot.answer_callback_query(call.id, text="🧠 విశ్లేషణ... పార్ట్-2 లోడ్ చేస్తున్నాను సర్...")
                
                part2_report = f"📊 <b>పూర్తి రీసెర్చ్ నివేదిక - Part 2 (చివరి భాగం)</b>\n" \
                               f"🗞 <i>వార్త:</i> {vault_data['title']}\n" \
                               f"--------------------------------------------------\n\n" \
                               f"{vault_data['part2']}"
                
                markup = InlineKeyboardMarkup()
                first_part_btn = InlineKeyboardButton(text="⬅️ మొదటి భాగం చదవండి (Part 1)", callback_data=view_key)
                back_btn = InlineKeyboardButton(text="⬅️ వెనక్కి వెళ్ళండి (Back to Alert)", callback_data=vault_data['back_key'])
                markup.add(first_part_btn, back_btn)
                
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=part2_report, reply_markup=markup, parse_mode="HTML")

            # 3. '⬅️ వెనక్కి వెళ్ళండి' బటన్ నొక్కినప్పుడు
            elif msg_key.startswith("back_"):
                bot.answer_callback_query(call.id, text="⬅️ పాత అలర్ట్ కి తిరిగి వెళ్తున్నాము సర్...")
                view_key = analysis_vault[msg_key]
                vault_data = analysis_vault[view_key]
                
                original_markup = InlineKeyboardMarkup()
                view_btn = InlineKeyboardButton(text="🔎 పూర్తి విశ్లేషణ చదవండి (Read Full View)", callback_data=view_key)
                original_markup.add(view_btn)
                
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=vault_data['original_text'], reply_markup=original_markup, parse_mode="HTML")
        else:
            bot.answer_callback_query(call.id, text="❌ ఈ విశ్లేషణ పాతదవడం వల్ల మెమొరీ నుండి డిలీట్ అయింది సర్.")

    @bot.message_handler(func=lambda message: True)
    def handle_user_research_query(message):
        user_query = message.text.lower().strip()
        
        # 🌍 కమాండ్ 1: మార్కెట్ అప్‌డేట్స్
        if "market updates" in user_query or "market visheshalu" in user_query:
            bot.reply_to(message, f"🌍 సర్, మన రీసెర్చ్ టీమ్ మల్టీ-డైమెన్షనల్ మార్కెట్ నివేదికను సిద్ధం చేస్తున్నారు సర్...")
            
            market_prompt = """nuvvu oka leading global hedge fund ki 'Chief Research Analyst' vi. Eeroju market parinamala pai oka samagramaina nivedikanu ee krindi vibhagaluga vidividiga telugulo vivarinchu sir:
            
            1. [INDEX VIEW]: Nifty, Sensex mariyu keelaka index la kadalikala venuka unna asalu karanalu.
            2. [GLOBAL CORRELATION]: Antarjatiya marketlu (US Fed, global events, geopolitics) mana market nu ela prabhavitam chesayi.
            3. [NATIONAL & POLICY VIEW]: Mana deshiya arthikabhivruddhi, prabhutvam teesukunna policy nirnayalu leda macro data prabhavam.
            4. [SECTORIAL ANALYSIS]: Eeroju eye ranganalu enduku balanga nilichayi, evi balahinapaddayi (sector rotation trends).
            5. [STOCK SPECIFIC ACTION]: Market kadalikalaku karanamaina keelakamaina large/mid cap stocks vishleshana.
            6. [MASTER OVERVIEW & SYNTHESIS]: Chivaraga, paina perkonna anni konalanu (Index, Global, National, Sector, Stock) okadanikokati link chestu, raboye rojulalo oka big investor elanti vyoohamto adugulu veyalo oka master samagra vivarana ivvandi sir. Sadharana varthalla kakunda chala high-quality insights undali."""
            
            try:
                response = client_key2.models.generate_content(model='gemini-2.5-flash', contents=market_prompt)
                send_split_message(message.chat.id, response.text)
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ ఎర్రర్: {e}")
                
        # 🎯 కమాండ్ 2: స్టాక్ పిక్స్
        elif "stock picks" in user_query or "stocks selection" in user_query:
            bot.reply_to(message, f"🎯 సర్, మన చీఫ్ పోర్ట్‌ఫోలియో మేнеజర్ డ్యూయల్-సిస్టమ్ రీసెర్చ్ ఆన్ చేశారు. 2 ప్రత్యేక ఆల్ఫా స్టాక్స్ ఎంచుకుంటున్నారు సర్...")
            
            dual_stock_prompt = """nuvvu oka successful 'Chief Portfolio Manager' vi. Nee AI research team shekarinchina data points nundi eeroju 'khachitanga 2 ververu high-quality stocks' enchuko sir. Okadanikokati sambandham leni rendu ververu paddhatulalo undali:

            ----------------==================================----------------
            📌 **Stock 1: Pakka Fundamental & Financial Numbers Stock (First Code Method)**
            Deeniki sambandhinchina vishleshanalo ee krindi pointlu khachitamaina original numberlato undali sir:
            1. Company peru & Core Conviction
            2. FUNDAMENTALS (With Exact Numbers): Matalo kakunda ee krindivi numberlato saha undali:
               - Gatha 3 nundi 5 samvatsarala sales mariyu profit growth (CAGR %).
               - Operating mariyu net profit margins (Margin %).
               - Return on Equity (ROE %) mariyu Return on Capital Employed (ROCE %).
               - Debt-to-Equity mariyu promoter holding pledging (Pledging %) vivaralu.
            3. TECHNICALS & SECTORIAL OPPORTUNITY: Chart structure mariyu sector demand.
            4. MANAGEMENT, BUSINESS MODEL & LEGAL CHALLENGES: Execution record mariyu court/legal savallu emaina unnaya leda clean ga unda ane vishayam.

            ----------------==================================----------------
            📌 **Stock 2: Hidden Future Growth & Turnaround Stock (Second Code Method)**
            Ee stock empika poorthiga bhinnanga undali sir:
            - Idi already viparithంగా perigipoyi, momentum ayipoyina stock assalu kakoodadu.
            - Ippudippude turnaround avuthunna, kottha vyapara avakashalu vasthunna, bhavishyathulo bhariga edige capacity undi, investor konte baga upayogapade thiruguleni vriddhi gala 'High-Conviction Alpha Stock' ayi vendi.
            Deeniki sambandhinchi ee krindi 5 paramithalanu lothuga vishleshinchu sir:
               - (A) Fundamentals (Financial Strength & Margin)
               - (B) Technicals (Chart Structure & Breakout)
               - (C) Sectorial View (Sector Growth & Demand)
               - (D) Management & Business Model (Management Quality)
               - (E) Future Catalyst (Future Growth & New Orders)

            ⚠️ Gamanika: Okavela marketlo anthati patishtamaina quality stocks evi dorakakapothe, sootiga 'sar, eeroju anthati balamaina, thiruguleni vriddhi gala stock edi research team ku dorakaledu sir' ani cheppey. Normal stocks assalu vaddu. Mottham nivedikanu chala spashtanga vidividiga telugulo vivarinchu sir."""
            
            try:
                response = client_key2.models.generate_content(model='gemini-2.5-flash', contents=dual_stock_prompt)
                send_split_message(message.chat.id, response.text)
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ ఎర్రర్: {e}")
                
        # సాధారణ చాట్ ప్రశ్నలు
        else:
            bot.reply_to(message, f"🧠 ఓకే సర్, మీ ప్రశ్నకు సమాధానాన్ని మన రీసెర్చ్ టీమ్ సిద్ధం చేస్తోంది...")
            try:
                response = client_key2.models.generate_content(model='gemini-2.5-flash', contents=user_query)
                send_split_message(message.chat.id, response.text)
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ ఎర్రర్: {e}")

    bot.infinity_polling()
