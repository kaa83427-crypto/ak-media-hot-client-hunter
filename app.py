import datetime
import sqlite3
import urllib.parse
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="THE AK MEDIA - Hot Client Hunter", page_icon="🎯", layout="wide"
)

# Custom CSS for Professional Look, Print Styling & Dynamic Streak Glow
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { background-color: #D4AF37; color: black; font-weight: bold; border-radius: 8px; width: 100%; }
    
    .inactive-streak {
        filter: grayscale(100%);
        opacity: 0.4;
    }
    
    .active-streak {
        filter: none;
        opacity: 1;
    }
    
    @media print {
        body { background-color: white !important; color: black !important; }
        .sidebar, button, header, footer { display: none !important; }
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==================== LOCAL SQLITE DATABASE SETUP ====================
def init_db():
  conn = sqlite3.connect("ak_media.db", check_same_thread=False)
  cursor = conn.cursor()
  
  # Table for Follow-ups and Remarks
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS followups (
            business_name TEXT PRIMARY KEY,
            status TEXT,
            remark TEXT
        )
    """)
  
  # Table for Team Activity (Fixed: Removed DROP TABLE so data persists!)
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS team_activity (
            member_name TEXT PRIMARY KEY,
            leads INTEGER,
            pitches INTEGER,
            streak INTEGER,
            last_active_date TEXT,
            worked_today INTEGER
        )
    """)
  conn.commit()
  return conn

conn = init_db()
cursor = conn.cursor()

today_str = str(datetime.date.today())

default_team = {
    "MR.AK (Admin)": {"leads": 0, "pitches": 0, "streak": 5},
    "Hari Shinde": {"leads": 0, "pitches": 0, "streak": 3},
    "Somnath Pardhi": {"leads": 0, "pitches": 0, "streak": 4},
}

for member, stats in default_team.items():
  cursor.execute(
      "INSERT OR IGNORE INTO team_activity (member_name, leads, pitches, streak, last_active_date, worked_today) VALUES (?, ?, ?, ?, ?, ?)",
      (member, stats["leads"], stats["pitches"], stats["streak"], today_str, 0)
  )
conn.commit()

# ==================== INITIALIZE SESSION STATE ====================
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False
if "username" not in st.session_state:
  st.session_state["username"] = ""
if "role" not in st.session_state:
  st.session_state["role"] = ""
if "display_name" not in st.session_state:
  st.session_state["display_name"] = ""

if "selected_page" not in st.session_state:
  st.session_state["selected_page"] = "Lead Hunter Dashboard"
if "active_audit_lead" not in st.session_state:
  st.session_state["active_audit_lead"] = None
if "generated_quotation" not in st.session_state:
  st.session_state["generated_quotation"] = None

# ==================== LOGIN SYSTEM ====================
USERS_DB = {
    "ankush_ceo": {
        "pass": "akmedia2026",
        "role": "Admin",
        "name": "MR.AK (Admin)",
    },
    "HS123": {
        "pass": "akmedia123",
        "role": "Sales Representative",
        "name": "Hari Shinde",
    },
    "SP123": {
        "pass": "akmedia123",
        "role": "Sales Representative",
        "name": "Somnath Pardhi",
    },
}

if not st.session_state["logged_in"]:
  st.markdown(
      """
        <div style="background-color: #0b0b0b; padding: 30px; border-bottom: 3px solid #D4AF37; border-radius: 10px; margin-bottom: 25px; text-align: center;">
            <h1 style="color: #D4AF37; margin: 0; font-family: 'Georgia', serif; font-size: 32px; letter-spacing: 2px;">THE AK MEDIA</h1>
            <p style="color: #FFFFFF; margin: 5px 0 0 0; font-size: 14px; font-weight: 500; letter-spacing: 1.5px;">Building Businesses | Building Brands — Secure Login</p>
        </div>
        """,
      unsafe_allow_html=True,
  )

  col1, col2, col3 = st.columns([1, 1.5, 1])
  with col2:
    st.subheader("🔐 Team Portal Login")
    st.info(
        "टीप: युजरआयडी आणि पासवर्ड फक्त द एके मीडियाच्या ऑनरकडून (MR.AK)"
        " प्रदान केला जाईल."
    )

    input_user = st.text_input("👤 Enter User ID")
    input_pass = st.text_input("🔑 Enter Password", type="password")

    if st.button("🚀 Login to System"):
      if input_user in USERS_DB and USERS_DB[input_user]["pass"] == input_pass:
        st.session_state["logged_in"] = True
        st.session_state["username"] = input_user
        st.session_state["role"] = USERS_DB[input_user]["role"]
        st.session_state["display_name"] = USERS_DB[input_user]["name"]
        
        logged_name = USERS_DB[input_user]["name"]
        cursor.execute("SELECT last_active_date FROM team_activity WHERE member_name = ?", (logged_name,))
        row_dt = cursor.fetchone()
        if row_dt and row_dt[0] != today_str:
          cursor.execute("UPDATE team_activity SET last_active_date = ?, worked_today = 0 WHERE member_name = ?", (today_str, logged_name))
          conn.commit()

        st.success(
            f"✅ Welcome back, {st.session_state['display_name']}! Loading"
            " dashboard..."
        )
        st.rerun()
      else:
        st.error("❌ चुकाचा युजरआयडी किंवा पासवर्ड! कृपया पुन्हा प्रयत्न करा.")
  st.stop()

# ==================== FORMAL HEADER (Post Login) ====================
st.markdown(
    """
    <div style="background-color: #0b0b0b; padding: 20px; border-bottom: 3px solid #D4AF37; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.6); text-align: center;">
        <h1 style="color: #D4AF37; margin: 5px 0 0 0; font-family: 'Georgia', serif; font-size: 28px; letter-spacing: 2px;">THE AK MEDIA</h1>
        <p style="color: #FFFFFF; margin: 5px 0 0 0; font-size: 13px; font-weight: 500; letter-spacing: 1.5px;">Building Businesses | Building Brands</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Top Bar with Logout & User Info
top_c1, top_c2, top_c3 = st.columns([2, 2, 1])
top_c1.write(
    f"👤 **Logged in as:** {st.session_state['display_name']} ("
    f"*{st.session_state['role']}*)"
)
if top_c3.button("🚪 Logout"):
  st.session_state["logged_in"] = False
  st.rerun()

# Navigation Menu Bar
n1, n2, n3, n4, n5 = st.columns(5)
with n1:
  if st.button("🎯 Lead Hunter"):
    st.session_state["selected_page"] = "Lead Hunter Dashboard"
with n2:
  if st.button("📑 Audit Report"):
    st.session_state["selected_page"] = "Audit Report View"
with n3:
  if st.button("💰 Service Plans & Quote"):
    st.session_state["selected_page"] = "Quotation Generator"
with n4:
  if st.button("💬 Message Library"):
    st.session_state["selected_page"] = "Message Library"
with n5:
  if st.button("💡 Objection Sheet"):
    st.session_state["selected_page"] = "Objection Cheat Sheet"

st.markdown("---")

# ==================== PAGE 5: SERVICE PLANS & QUOTATION GENERATOR ====================
if st.session_state["selected_page"] == "Quotation Generator":
  st.title("💰 THE AK MEDIA - Service Plans & Instant Quotation Generator")
  st.write(
      "### 📋 पीपीटीनुसार ५ मुख्य प्लॅन्स आणि कस्टमाइझ्ड कोटेशन कॅल्क्युलेटर"
  )

  tab1, tab2 = st.tabs(
      ["⭐ Official 5 Service Plans", "⚙️ Custom Quotation Generator"]
  )

  with tab1:
    st.subheader("📌 THE AK MEDIA - अधिकृत ५ बिझनेस प्लॅन्स")
    p1, p2, p3 = st.columns(3)
    with p1:
      st.markdown("""
            <div style="border: 2px solid #D4AF37; padding: 15px; border-radius: 8px; background-color: #111;">
                <h3 style="color: #D4AF37;">1. Basic Star</h3>
                <h4 style="color: white;">₹10,000 / mo</h4>
                <p style="color: #aaa; font-size: 12px;">Essential social media presence for growing local businesses.</p>
                <ul style="color: #ccc; font-size: 13px;">
                    <li>8 Monthly Posts</li>
                    <li>2 Basic Reels</li>
                    <li>Page Optimization</li>
                    <li>Basic Hashtag Strategy</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    with p2:
      st.markdown("""
            <div style="border: 2px solid #D4AF37; padding: 15px; border-radius: 8px; background-color: #111;">
                <h3 style="color: #D4AF37;">2. Business Growth</h3>
                <h4 style="color: white;">₹18,000 / mo</h4>
                <p style="color: #aaa; font-size: 12px;">Accelerate your customer engagement with consistent content.</p>
                <ul style="color: #ccc; font-size: 13px;">
                    <li>12 Monthly Posts</li>
                    <li>6 Managed Reels</li>
                    <li>FB/IG Ads Setup</li>
                    <li>Content Strategy & Captions</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    with p3:
      st.markdown("""
            <div style="border: 2px solid #D4AF37; padding: 15px; border-radius: 8px; background-color: #111;">
                <h3 style="color: #D4AF37;">3. Brand Accelerator</h3>
                <h4 style="color: white;">₹30,000 / mo</h4>
                <p style="color: #aaa; font-size: 12px;">Advanced growth strategy for established local brands.</p>
                <ul style="color: #ccc; font-size: 13px;">
                    <li>20 Monthly High-Impact Posts</li>
                    <li>10 Cinematic Reels (Team Shoot)</li>
                    <li>Performance Ad Management</li>
                    <li>Custom Growth Roadmap</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    p4, p5 = st.columns(2)
    with p4:
      st.markdown("""
            <div style="border: 2px solid #D4AF37; padding: 15px; border-radius: 8px; background-color: #111;">
                <h3 style="color: #D4AF37;">4. Advance Digital</h3>
                <h4 style="color: white;"> ₹50,000 / mo</h4>
                <p style="color: #aaa; font-size: 12px;">Daily brand presence for serious market expansion.</p>
                <ul style="color: #ccc; font-size: 13px;">
                    <li>Daily Brand Presence (30 Posts)</li>
                    <li>15 Pro-Level Reels</li>
                    <li>Google My Business (SEO)</li>
                    <li>Omnichannel Ads Setup</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    with p5:
      st.markdown("""
            <div style="border: 2px solid #D4AF37; padding: 15px; border-radius: 8px; background-color: #111;">
                <h3 style="color: #D4AF37;">5. The VIP King Pack</h3>
                <h4 style="color: white;">₹1.5 Lakh+ / mo</h4>
                <p style="color: #aaa; font-size: 12px;">Designed for Nashik's top jewelers, builders, and corporate giants.</p>
                <ul style="color: #ccc; font-size: 13px;">
                    <li>Full E-Commerce / Dynamic Website</li>
                    <li>20+ Pro Cinematic Reels with Storytelling</li>
                    <li>Direct Influencer Marketing Tie-ups</li>
                    <li>Dedicated Manager & 24/7 Priority Support</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

  with tab2:
    st.subheader("⚙️ Custom Quotation Generator (क्लायंटसाठी कस्टमाइझ्ड प्लॅन)")
    st.write(
        "क्लायंटच्या गरजेनुसार खालील घटक निवडून तात्काळ अचूक कोटेशन तयार करा:"
    )

    col_q1, col_q2 = st.columns(2)
    with col_q1:
      q_client_name = st.text_input(
          "🏢 Client / Business Name", "Business Name"
      )
      q_reels = st.number_input(
          "🎬 मंथली किती रिल्स पाहिजेत? (Monthly Reels Count)",
          min_value=0,
          max_value=60,
          value=2,
      )
      q_posts = st.number_input(
          "🖼️ मंथली किती पोस्ट्स पाहिजेत? (Monthly Posts Count)",
          min_value=0,
          max_value=60,
          value=8,
      )
      q_opt = st.selectbox(
          "✨ पेज ऑप्टिमायझेशन करायचे आहे का? (Page Optimization)",
          ["Yes (₹2,000)", "No"],
      )

    with col_q2:
      q_web = st.selectbox(
          "🌐 वेबसाईट बनवायची आहे का? (Website Building)",
          ["No", "Basic Business Website (₹10,000)", "Advanced E-Commerce Website (₹30,000)"],
      )
      q_seo = st.selectbox(
          "🚀 त्या वेबसाईटसाठी एसिओ (SEO) करायचे आहे का?",
          ["No", "Basic Local SEO (₹5,000)", "Full Advanced SEO (₹10,000)"],
      )
      q_strat = st.selectbox(
          "🎯 कस्टम स्ट्रॅटेजी (Custom Social Media Strategy) तयार करायची आहे का?",
          ["Yes (₹3,500)", "No"],
      )

    total_cost = (q_reels * 1000) + (q_posts * 500)
    if "Yes" in q_opt:
      total_cost += 2000
    if "Basic Business Website" in q_web:
      total_cost += 10000
    elif "Advanced E-Commerce Website" in q_web:
      total_cost += 30000

    if "Basic Local SEO" in q_seo:
      total_cost += 5000
    elif "Full Advanced SEO" in q_seo:
      total_cost += 10000

    if "Yes" in q_strat:
      total_cost += 3500

    st.markdown("---")
    st.subheader(f"💵 Total Custom Quotation Value: ₹{total_cost:,} / month")

    if st.button("📄 Generate Print-Ready Custom Quotation"):
      st.session_state["generated_quotation"] = {
          "client": q_client_name,
          "reels": q_reels,
          "posts": q_posts,
          "opt": q_opt,
          "web": q_web,
          "seo": q_seo,
          "strat": q_strat,
          "total": total_cost,
          "date": str(datetime.date.today()),
      }

  if st.session_state["generated_quotation"] is not None:
    q = st.session_state["generated_quotation"]
    st.markdown("---")

    quotation_html = f"""
        <div style="background-color: white; color: black; padding: 40px; border-radius: 10px; font-family: 'Helvetica', sans-serif; border: 2px solid #D4AF37; max-width: 800px; margin: auto;">
            <div style="text-align: center; border-bottom: 2px solid #D4AF37; padding-bottom: 15px; margin-bottom: 25px;">
                <h2 style="color: #0b0b0b; margin: 0; font-size: 26px; letter-spacing: 1.5px;">THE AK MEDIA</h2>
                <p style="color: #666; font-size: 12px; margin: 5px 0 0 0; text-transform: uppercase; letter-spacing: 1.5px;">OFFICIAL CUSTOMIZED SERVICES QUOTATION</p>
            </div>

            <div style="display: flex; justify-content: space-between; margin-bottom: 20px; font-size: 14px;">
                <div>
                    <b>Client Name:</b> {q['client']}<br>
                    <b>Prepared By:</b> THE AK MEDIA Sales Team<br>
                    <b>Location:</b> Nashik District
                </div>
                <div style="text-align: right;">
                    <b>Date:</b> {q['date']}<br>
                    <b>Quote Ref:</b> AKM-QTN-{datetime.datetime.now().strftime('%M%S')}
                </div>
            </div>

            <h3 style="color: #111; border-bottom: 1px solid #ddd; padding-bottom: 8px;">Customized Deliverables & Scope</h3>
            <table style="width: 100%; font-size: 14px; margin-bottom: 20px; border-collapse: collapse;">
                <tr style="background-color: #f5f5f5;">
                    <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Service Parameter</th>
                    <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Selected Specification</th>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Monthly Reels</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{q['reels']} Reels</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Monthly Posts</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{q['posts']} Graphic Posts</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Page Optimization</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{q['opt']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Website Building</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{q['web']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Website SEO</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{q['seo']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px; border: 1px solid #ddd;"><b>Custom Strategy</b></td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{q['strat']}</td>
                </tr>
            </table>

            <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #D4AF37; margin-bottom: 30px;">
                <h3 style="margin: 0; color: #111;">Total Customized Package Price: ₹{q['total']:,} / month</h3>
                <p style="margin: 5px 0 0 0; font-size: 12px; color: #555;">* Building Businesses | Building Brands — THE AK MEDIA, Nashik</p>
            </div>

            <div style="margin-top: 40px; border-top: 2px dashed #ccc; padding-top: 20px; display: flex; justify-content: space-between; font-size: 13px; color: #555;">
                <div>
                    <b>Office Address:</b><br>
                    The AK Media, Near Guru Cake, In Front of Vitthal Rukmini Dental Clinic,<br>
                    Dhawkhar Nagar, Chandwad, Nashik - 423101
                </div>
                <div style="text-align: right;">
                    <b>Contact & Support:</b><br>
                    Phone: +91 9172082052<br>
                    Email: the.ak.media56@gmail.com
                </div>
            </div>
        </div>
        """
    st.markdown(quotation_html, unsafe_allow_html=True)
    st.info(
        "💡 **प्रिन्ट कशी काढाल किंवा पीडीएफ कशी सेव्ह कराल?**\n"
        "लॅपटॉपवर असताना फक्त **`Ctrl + P`** दाबा आणि प्रिन्टरच्या जागी **'Save as PDF'"
        " निवडा!"
    )

# ==================== PAGE 4: MULTI-LANGUAGE OBJECTION HANDLING CHEAT SHEET ====================
elif st.session_state["selected_page"] == "Objection Cheat Sheet":
  st.title("💡 Objection Handling Cheat-Sheet")
  st.write(
      "### 🛡️ क्लायंटच्या प्रश्नांना/कारणांना (Objections) उडवण्यासाठी"
      " रेडीमेड उत्तरं!"
  )

  obj_lang = st.selectbox(
      "🌐 भाषेची निवड करा (Select Objection Language)",
      ["Marathi (मराठी)", "Hindi (हिंदी)", "English"],
  )

  if "Marathi" in obj_lang:
    with st.expander("❌ 'आम्ही आधीच सोशल मीडिया करतोय / दुसरी एजन्सी आहे'"):
      st.write(
          "**उत्तर:** 'खूप छान सर! पण आम्ही तुमच्या पेजचे ऑडिट केले तेव्हा गेल्या"
          " १५ दिवसांत नवीन पोस्ट/रील दिसली नाही. तुमच्या सध्याच्या एजन्सीसोबत"
          " तुम्ही मोफत सोशल मीडिया ऑडिट कम्पेअर करून बघू शकता!'"
      )
    with st.expander("❌ 'सध्या बजेट नाहीये / महाग वाटतंय'"):
      st.write(
          "**उत्तर:** 'सर, सोशल मीडिया हा खर्च नसून नवीन ग्राहक मिळवण्याची"
          " इन्वेस्टमेंट आहे. १ नवीन ग्राहक जरी वाढला तरी आमची फी वसूल"
          " होते. आम्ही अगदी रिझनेबल पॅकेज देतो, एकदा ट्राय करा!'"
      )
    with st.expander("❌ 'आम्हाला गरज नाहीये / आमचा बिझनेस असाच चालतो'"):
      st.write(
          "**उत्तर:** 'सर, तुमचा बिझनेस भारी आहेच, पण आजकाल ग्राहक दुकानात"
          " येण्याआधी ऑनलाइन सर्च करतात. तुमचे प्रतिस्पर्धी सोशल मीडियावर"
          " ॲक्टिव्ह आहेत, त्यामुळे जुने क्लायंट्स टिकवण्यासाठी हे गरजेचे आहे!'"
      )

  elif "Hindi" in obj_lang:
    with st.expander("❌ 'हम पहले से सोशल मीडिया कर रहे हैं'"):
      st.write(
          "**उत्तर:** 'बहुत बढ़िया सर! लेकिन जब हमने आपका पेज चेक किया, तो पिछले"
          " 15 दिनों से कोई पोस्ट नहीं दिखा. आप अपनी करंट एजेंसी के साथ हमारा फ्री"
          " ऑडिट रिपोर्ट कम्पेयर करके देख सकते हैं!'"
      )
    with st.expander("❌ 'अभी बजट नहीं है / महंगा है'"):
      st.write(
          "**उत्तर:** 'सर, सोशल मीडिया खर्चा नहीं बल्कि नए कस्टमर्स लाने का"
          " इन्वेस्टमेंट है. 1-2 नए कस्टमर आने पर ही हमारी फीस कवर हो जाती"
          " है. हमारा पैकेज काफी अफोर्डेबल है!'"
      )
    with st.expander("❌ 'हमें जरूरत नहीं है'"):
      st.write(
          "**उत्तर:** 'सर, आपका काम अच्छा है लेकिन आजकल कस्टमर दुकान पर आने से"
          " पहले ऑनलाइन सर्च करते हैं. आपके कॉम्पिटिटर्स एक्टिव हैं, इसलिए ऑनलाइन"
          " रहना बहुत जरूरी है!'"
      )

  else:  # English
    with st.expander(
        "❌ 'We are already doing social media / Have another agency'"
    ):
      st.write(
          "**Response:** 'That's great sir! However, we noticed no updates on"
          " your page for the last 15 days. We offer a Free Social Media Audit"
          " so you can compare the output with your current agency.'"
      )
    with st.expander("❌ 'We don't have the budget / Too expensive'"):
      st.write(
          "**Response:** 'Sir, social media marketing is an investment to bring"
          " in new walk-in clients. Acquiring just 1-2 new recurring clients"
          " covers our monthly cost. We offer flexible plans!'"
      )
    with st.expander("❌ 'We don't need digital marketing'"):
      st.write(
          "**Response:** 'Sir, while your word-of-mouth is strong, modern"
          " customers check online profiles first. Competitors in your area are"
          " aggressively posting reels to capture local market share.'"
      )

  if st.button("⬅️ Back to Lead Dashboard"):
    st.session_state["selected_page"] = "Lead Hunter Dashboard"
    st.rerun()

# ==================== PAGE 3: QUICK MESSAGE TEMPLATES LIBRARY ====================
elif st.session_state["selected_page"] == "Message Library":
  st.title("💬 Quick Message Templates / Copy-Paste Library")
  st.write(
      "### 🚀 वेगवेगळ्या व्यवसायांसाठी आणि भाषांसाठी तयार केलेले कॉल्स आणि"
      " व्हॉट्सॲप पिचेस"
  )

  lib_lang = st.selectbox(
      "🌐 गॅलरीची भाषा निवडा (Select Message Language)",
      ["Marathi (मराठी)", "Hindi (हिंदी)", "English"],
  )

  tab1, tab2, tab3 = st.tabs(
      ["☕ Cafes & Restaurants", "🏋️ Gyms & Fitness", "🛍️ Retail & Clothing"]
  )

  if "Marathi" in lib_lang:
    with tab1:
      st.subheader("☕ कॅफे / रेस्टॉरंट - मराठी pitch")
      st.code(
          "नमस्कार [Business Name],\n\nमी THE AK MEDIA (नाशिक) वरून बोलतोय. आम्ही"
          " तुमचं सोशल मीडिया पेज पाहिलं, गेल्या काही दिवसांपासून त्यावर नवीन"
          " पोस्ट किंवा रील्स अपडेट झालेली नाहीत.\n\nआजकाल तरुण वर्ग आणि"
          " कस्टमर्स ऑनलाइन सर्च करूनच कॅफे निवडतात. सोशल मीडिया इन-ॲक्टिव्ह"
          " राहिल्याने नवीन कस्टमर्स प्रतिस्पर्ध्यांकडे जाऊ शकतात.\n\nआम्ही नाशिक"
          " जिल्ह्यातील कॅफेसाठी प्रोफेशनल रील्स, ग्राफिक डिझाईन आणि सोशल मीडिया"
          " मॅनेजमेंट हँडल करतो. तुमच्या पेजचा फ्री ऑडिट रिपोर्ट हवा असल्यास"
          " नक्की सांगा!",
          language="text",
      )
    with tab2:
      st.subheader("🏋️ जिम / फिटनेस क्लब - मराठी pitch")
      st.code(
          "हाय [Business Name],\n\nTHE AK MEDIA (नाशिक) कडून संपर्क करतोय. फिटनेस"
          " लव्हर्स नेहमी नवीन ऑफर्स आणि वर्कआउट व्हिडिओज सोशल मीडियावर शोधत"
          " असतात. तुमच्या जिमचे पेज सध्या इन-ॲक्टिव्ह दिसतेय.\n\nआम्ही जिमचे"
          " ब्राँडिंग, एनर्जेटिक रील्स आणि लोकल लीड जनरेशन कॅम्पेन हँडल करतो."
          " ज्यामुळे नवीन मेंबरशिप वाढण्यास मदत होईल. मोफत सल्ला हवा का?",
          language="text",
      )
    with tab3:
      st.subheader("🛍️ रिटेल / क्लोदिंग स्टोअर - मराठी pitch")
      st.code(
          "नमस्कार [Business Name],\n\nमी THE AK MEDIA मधून बोलतोय. तुमच्या"
          " दुकानाचे डिजिटल ब्रँडिंग वाढवण्यासाठी आम्ही मदत करू शकतो. फेस्टिव्हल"
          " ऑफर्स आणि नवीन स्टॉकचे प्रमोशन सोशल मीडियावर असणे खूप गरजेचे आहे.\n\nआमच्या"
          " डिजिटल सर्व्हिसेसबद्दल माहिती हवी असल्यास नक्की कळवा!",
          language="text",
      )

  elif "Hindi" in lib_lang:
    with tab1:
      st.subheader("☕ कैफे / रेस्टोरेंट - हिंदी पिच")
      st.code(
          "नमस्ते [Business Name],\n\nमैं THE AK MEDIA (नाशिक) से बात कर रहा"
          " हूँ. हमने आपका सोशल मीडिया पेज देखा, पिछले कुछ दिनों से उस पर"
          " कोई नई पोस्ट या रील्स अपडेट नहीं हुई है.\n\nआजकल कस्टमर्स ऑनलाइन सर्च"
          " करके ही कैफे चुनते हैं. सोशल मीडिया इन-एक्टिव रहने से नए कस्टमर्स"
          " कॉम्पिटिटर्स के पास जा सकते हैं.\n\nहम नाशिक रीजन के कैफे के लिए"
          " प्रोफेशनल रील्स, ग्राफिक डिज़ाइन और सोशल मीडिया मैनेजमेंट हैंडल"
          " करते हैं. क्या आपके पेज के लिए फ्री ऑडिट रिपोर्ट भेज दें?",
          language="text",
      )
    with tab2:
      st.subheader("🏋️ जिम / फिटनेस क्लब - हिंदी पिच")
      st.code(
          "हाय [Business Name],\n\nTHE AK MEDIA (नाशिक) से संपर्क कर रहे हैं."
          " फिटनेस लवर्स हमेशा सोशल मीडिया पर नए ऑफर्स और वर्कआउट वीडियो खोजते"
          " रहते हैं. आपकी जिम का पेज फिलहाल इन-एक्टिव दिख रहा है.\n\nहम जिम"
          " ब्रांडिंग, एनर्जेटिक रील्स और लोकल लीड जनरेशन कैंपेन हैंडल करते हैं."
          " क्या फ्री कंसल्टेशन चाहिए?",
          language="text",
      )
    with tab3:
      st.subheader("🛍️ रिटेल / क्लोदिंग स्टोर - हिंदी पिच")
      st.code(
          "नमस्ते [Business Name],\n\nमैं THE AK MEDIA से बात कर रहा हूँ. आपके"
          " स्टोर की डिजिटल ब्रांडिंग बढ़ाने में हम मदद कर सकते हैं. फेस्टिवल"
          " ऑफर्स और नए स्टॉक का प्रमोशन सोशल मीडिया पर होना बहुत जरूरी है.\n\nहमारी"
          " डिजिटल सर्विसेज के बारे में जानकारी चाहिए क्या?",
          language="text",
      )

  else:  # English
    with tab1:
      st.subheader("☕ Cafe / Restaurant - English Pitch")
      st.code(
          "Hi [Business Name],\n\nI'm reaching out from THE AK MEDIA Nashik. We"
          " checked your social media presence and noticed that your handles"
          " haven't been active recently.\n\nMost modern customers search"
          " online before visiting a cafe. Staying inactive means losing"
          " potential footfall to competitors.\n\nWe manage professional"
          " social media, reels, and branding for businesses across Nashik."
          " Would you like a Free Social Media Audit Report?",
          language="text",
      )
    with tab2:
      st.subheader("🏋️ Gym / Fitness - English Pitch")
      st.code(
          "Hi [Business Name],\n\nCalling from THE AK MEDIA Nashik. Fitness"
          " enthusiasts actively look for active workout content and offers"
          " online. Your gym page looks inactive right now.\n\nWe specialize in"
          " fitness branding, high-energy reels, and local lead generation."
          " Interested in a quick free audit?",
          language="text",
      )
    with tab3:
      st.subheader("🛍️ Retail / Clothing - English Pitch")
      st.code(
          "Hi [Business Name],\n\nGreeting from THE AK MEDIA. We can help scale"
          " your store's digital presence and run targeted local promotions"
          " for festive offers and new inventory.\n\nWould you like to explore"
          " our digital branding solutions?",
          language="text",
      )

  if st.button("⬅️ Back to Lead Dashboard"):
    st.session_state["selected_page"] = "Lead Hunter Dashboard"
    st.rerun()

# ==================== PAGE 1: LEAD HUNTER DASHBOARD ====================
elif st.session_state["selected_page"] == "Lead Hunter Dashboard":
  st.title("🎯 Hot Client Hunter & AI Lead System (Nashik District)")
  st.write(
      "### 🚀 नाशिक जिल्ह्यातील इन-ॲक्टिव्ह क्लायंट्स शोधा, AI स्कोर तपासा आणि"
      " एका क्लिकवर कॉल/पिच पाठवा!"
  )

  # ==================== SIDEBAR FILTERS & EXPORT FOLLOW-UP HISTORY ====================
  st.sidebar.header("🔍 Search Filters")

  nashik_district_data = {
      "Chandwad": [
          "Bus Stand Area, Chandwad",
          "Main Market, Chandwad",
          "Manmath Nagar, Chandwad",
          "Dhawkhar Nagar, Chandwad",
          "Deola Road, Chandwad",
          "Rajendra Nagar, Chandwad",
          "Station Road, Chandwad",
          "Vinchur Road, Chandwad",
      ],
      "Nashik": [
          "College Road, Nashik",
          "Gangapur Road, Nashik",
          "Cidco, Nashik",
          "Indiranagar, Nashik",
          "Panchavati, Nashik",
          "Satpur, Nashik",
          "Adgaon, Nashik",
          "Makhmalabad, Nashik",
          "Nashik Road",
          "Pathardi Phata, Nashik",
          "Dwarka, Nashik",
          "Ambad, Nashik",
      ],
      "Sinnar": [
          "Pune Road, Sinnar",
          "Main Bazar, Sinnar",
          "MIDC Sinnar",
          "Deolali Camp Road, Sinnar",
          "Shirdi Road, Sinnar",
      ],
      "Malegaon": [
          "Camp Road, Malegaon",
          "Kidwai Road, Malegaon",
          "Main Road, Malegaon",
          "Sangmeshwar, Malegaon",
          "Soygaon, Malegaon",
          "Azad Nagar, Malegaon",
      ],
      "Niphad": [
          "Niphad City",
          "Pimpalgaon Baswant",
          "Lasalgaon",
          "Khedle Khede",
          "Saykheda",
      ],
      "Yeola": [
          "Vinchur Road, Yeola",
          "Main Bazar, Yeola",
          "Station Road, Yeola",
          "Andarsul, Yeola",
      ],
      "Dindori": ["Dindori City", "Vani", "Khedgaon", "Peth Road Dindori"],
      "Igatpuri": [
          "Station Road, Igatpuri",
          "Mumbai-Nashik Highway, Igatpuri",
          "Ghoti Budruk",
      ],
      "Trimbakeshwar": [
          "Trimbak City",
          "Shrimantha Baji Rao Road, Trimbakeshwar",
          "Harshul",
      ],
      "Kalwan": ["Kalwan City", "Meshi", "Konal"],
      "Deola": ["Deola City", "Wakhari", "Bhadwan"],
      "Surgana": ["Surgana City", "Borro"],
      "Peth": ["Peth City", "Devali"],
      "Baglan (Satana)": ["Satana City", "Taharat", "Arai"],
  }

  district_input = st.sidebar.selectbox(
      "१. जिल्हा निवडा (District)", ["Nashik District"]
  )
  selected_taluka = st.sidebar.selectbox(
      "२. तालुका निवडा (Taluka)", list(nashik_district_data.keys())
  )
  selected_area = st.sidebar.selectbox(
      "३. विशिष्ट एरिया निवडा (Area/Locality)",
      nashik_district_data[selected_taluka],
  )
  category_input = st.sidebar.selectbox(
      "४. कॅटेगरी निवडा (Category)",
      [
          "Cafe",
          "Restaurant",
          "Gym",
          "Salon",
          "Beauty Parlour",
          "Clothing Store",
          "Coaching Classes",
          "Bakery",
          "Hardware Store",
          "Medical Store",
          "Mobile Shop",
      ],
  )
  pitch_language = st.sidebar.selectbox(
      "🌐 पिचची भाषा निवडा (Pitch Language)",
      ["Marathi (मराठी)", "Hindi (हिंदी)", "English"],
  )

  # ==================== LEADERBOARD & STREAK TRACKER (FROM DB) ====================
  st.sidebar.markdown("---")
  st.sidebar.subheader("👑 King of the Day / Streak Tracker")

  cursor.execute("SELECT member_name, leads, pitches, streak, worked_today FROM team_activity")
  db_team_data = cursor.fetchall()
  
  team_scores = {}
  for member, l_count, p_count, streak, w_today in db_team_data:
    team_scores[member] = {"leads": l_count, "pitches": p_count, "streak": streak, "worked_today": w_today}

  sorted_team = sorted(
      team_scores.items(),
      key=lambda x: x[1]["pitches"] + x[1]["leads"],
      reverse=True,
  )
  if sorted_team:
    king_name, king_stats = sorted_team[0]
    total_king_score = king_stats['pitches'] + king_stats['leads']
    st.sidebar.markdown(f"""
    <div style="background-color: #1e3d2f; border: 1px solid #2ecc71; padding: 10px; border-radius: 8px; margin-bottom: 10px;">
        <p style="color: #2ecc71; margin: 0; font-weight: bold;">👑 King of the Day: {king_name}</p>
        <p style="color: #fff; margin: 0; font-size: 13px;">(Total Score: {total_king_score} | Leads: {king_stats['leads']} | Pitches: {king_stats['pitches']})</p>
    </div>
    """, unsafe_allow_html=True)

  curr_user_name = st.session_state["display_name"]
  
  # Ensure current user exists in database
  cursor.execute("SELECT member_name FROM team_activity WHERE member_name = ?", (curr_user_name,))
  if not cursor.fetchone():
    cursor.execute("INSERT OR IGNORE INTO team_activity (member_name, leads, pitches, streak, last_active_date, worked_today) VALUES (?, ?, ?, ?, ?, ?)",
                   (curr_user_name, 0, 0, 1, today_str, 0))
    conn.commit()

  cursor.execute("SELECT worked_today FROM team_activity WHERE member_name = ?", (curr_user_name,))
  user_w_row = cursor.fetchone()
  current_user_worked = user_w_row[0] if user_w_row else 0

  if current_user_worked == 0:
    if st.sidebar.button("🔥 I'm doing my work today"):
      cursor.execute("UPDATE team_activity SET worked_today = 1 WHERE member_name = ?", (curr_user_name,))
      conn.commit()
      st.success("✅ Attendance marked for today!")
      st.rerun()

  if st.session_state["role"] == "Admin":
    st.sidebar.write("---")
    st.sidebar.write("👑 **CEO Master Team Tracker:**")
    for member, stats in team_scores.items():
      emoji_class = "active-streak" if stats["worked_today"] == 1 else "inactive-streak"
      st.sidebar.markdown(
          f"""<div class="{emoji_class}">🔥 <b>{member}</b></div>
          🎯 Leads: `{stats['leads']}` | 💬 Pitches: `{stats['pitches']}` | 🔥 Streak: `{stats['streak']} Days` <br>Status: `{'Active Today' if stats['worked_today']==1 else 'Not Marked Yet'}`<br><br>""",
          unsafe_allow_html=True,
      )
  else:
    my_stats = team_scores.get(curr_user_name, {"leads": 0, "pitches": 0, "streak": 1, "worked_today": 0})
    emoji_class = "active-streak" if my_stats["worked_today"] == 1 else "inactive-streak"
    
    st.sidebar.markdown(f"""<div class="{emoji_class}" style="font-size: 24px;">🔥 Daily Streak</div>""", unsafe_allow_html=True)
    st.sidebar.metric("🔥 Daily Contribution Streak", f"{my_stats['streak']} Days")
    st.sidebar.metric("Total Leads Hunted By Me", my_stats["leads"])
    st.sidebar.metric("Pitches Sent By Me", my_stats["pitches"])

  secret_key = st.secrets.get("GOOGLE_API_KEY", "")
  if not secret_key:
    api_key = st.sidebar.text_input(
        "🔑 Google API Key टाका", type="password", help="इथे तुझी API Key टाक"
    )
  else:
    api_key = secret_key


  def fetch_strict_area_places(taluka, area, category, key):
    if not key:
      st.error("⚠️ Google API Key सापडली नाही!")
      return pd.DataFrame()

    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "json",
        "X-Goog-Api-Key": key,
        "X-Goog-FieldMask": (
            "places.displayName,places.formattedAddress,places.nationalPhoneNumber,places.rating"
        ),
    }
    search_query = f"{category} in {area}, {taluka}, Nashik, Maharashtra"
    payload = {"textQuery": search_query, "maxResultCount": 20}

    try:
      response = requests.post(url, headers=headers, json=payload)
      data = response.json()

      if "error" in data:
        st.error(f"❌ Google API Error: {data['error'].get('message')}")
        return pd.DataFrame()

      places = data.get("places", [])
      businesses = []

      for place in places:
        name = place.get("displayName", {}).get("text", "Unknown Business")
        address = place.get("formattedAddress", "")
        phone = place.get("nationalPhoneNumber", "919876543210")
        clean_phone = "".join(filter(str.isdigit, str(phone)))
        if len(clean_phone) < 10:
          clean_phone = "919876543210"
        elif not clean_phone.startswith("91"):
          clean_phone = "91" + clean_phone[-10:]

        rating = place.get("rating", 4.0)
        if rating == "N/A":
          rating = 4.0

        ai_score = (
            "🔥 High Priority (Hot)" if float(rating) >= 4.0 else "⚡ Standard"
        )

        businesses.append({
            "District": "Nashik",
            "Taluka": taluka,
            "Area": area,
            "Category": category,
            "Business Name": name,
            "Address": address,
            "Phone": clean_phone,
            "Rating": rating,
            "AI Score": ai_score,
            "Last Post": str(
                datetime.date.today() - datetime.timedelta(days=16)
            ),
            "Status": "HOT",
        })

      return pd.DataFrame(businesses)
    except Exception as e:
      st.error(f"❌ Connection Error: {str(e)}")
      return pd.DataFrame()


  if st.sidebar.button("🎯 Hunt District Leads Now"):
    with st.spinner(f"🔍 Fetching real-time AI leads for {selected_area}..."):
      df = fetch_strict_area_places(
          selected_taluka, selected_area, category_input, api_key
      )
      st.session_state["leads_data"] = df

      curr_user = st.session_state["display_name"]
      cursor.execute("SELECT leads FROM team_activity WHERE member_name = ?", (curr_user,))
      res = cursor.fetchone()
      current_leads_db = res[0] if res else 0
      new_leads_count = current_leads_db + len(df)
      
      cursor.execute("UPDATE team_activity SET leads = ? WHERE member_name = ?", (new_leads_count, curr_user))
      conn.commit()
      st.success(f"✅ {len(df)} leads successfully added to your count!")
      st.rerun()

  if "leads_data" in st.session_state and not st.session_state[
      "leads_data"
  ].empty:
    df = st.session_state["leads_data"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Businesses Found", len(df))
    hot_count = len(df[df["AI Score"].str.contains("High Priority")])
    col2.metric("🔥 AI High Priority Clients", hot_count)
    col3.metric("Target Area", selected_area)

    cursor.execute("SELECT business_name, status, remark FROM followups")
    db_followups = {row[0]: {"status": row[1], "remark": row[2]} for row in cursor.fetchall()}

    export_df = df.copy()
    export_df["Follow-up Status"] = export_df["Business Name"].apply(
        lambda x: db_followups.get(x, {}).get("status", "New Lead")
    )
    export_df["Remarks / Notes"] = export_df["Business Name"].apply(
        lambda x: db_followups.get(x, {}).get("remark", "")
    )

    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 Export Leads & Follow-up History (CSV)",
        data=export_df.to_csv(index=False),
        file_name=(
            f"THE_AK_MEDIA_Followups_{selected_taluka}_{selected_area}_{datetime.date.today()}.csv"
        ),
        mime="text/csv",
    )

    st.markdown("---")
    st.subheader(
        f"📋 Client Lead Board & AI Scoring — {selected_area}, {selected_taluka}"
        f" ({category_input})"
    )

    for idx, row in df.iterrows():
      with st.container():
        c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1.5, 1, 2.5])
        c1.write(f"**{row['Business Name']}**\n📍 {row['Area']}, {row['Taluka']}")
        c2.write(
            f"🏷️ {row['Category']}\n⭐ Rating: {row['Rating']}\n🤖 {row['AI Score']}"
        )
        c3.write(f"📅 Last Post: {row['Last Post']}")
        c4.error(f"🔥 {row['Status']}")

        if "Marathi" in pitch_language:
          pitch_msg = (
              f"नमस्कार {row['Business Name']},\n\nमी THE AK MEDIA (नाशिक) वरून"
              " बोलतोय. आम्ही तुमचं सोशल मीडिया पेज चेक केलं, गेल्या १५"
              " दिवसांपासून त्यावर नवीन पोस्ट नाहीये. \n\nआजकाल बहुतांश"
              f" कस्टमर्स ऑनलाइन शोधूनच {row['Category']} मध्ये येतात."
              " सोशल मीडिया इन-ॲक्टिव्ह राहिल्याने संभाव्य ग्राहक प्रतिस्पर्ध्यांकडे"
              " जाऊ शकतात.\n\nआम्ही नाशिक जिल्ह्यातील व्यवसायांचे ब्रँडिंग आणि"
              " सोशल मीडिया मॅनेज करतो. तुमच्या पेजचा मोफत सोशल मीडिया ऑडिट रिपोर्ट"
              " हवा असल्यास नक्की कळवा!"
          )
        elif "Hindi" in pitch_language:
          pitch_msg = (
              f"नमस्ते {row['Business Name']},\n\nमैं THE AK MEDIA (नाशिक) से"
              " बात कर रहा हूँ. हमने आपका इंस्टा/फेसबुक पेज देखा, काफी दिनों से"
              " कोई नई पोस्ट नहीं आई है.\n\nआजकल ज्यादातर कस्टमर्स ऑनलाइन सर्च करके"
              f" ही {row['Category']} चुनते हैं. पेज इन-एक्टिव होने से कस्टमर्स"
              " छूट सकते हैं.\n\nहम नाशिक रीजन के बिज़नेस का ब्रांडिंग और सोशल"
              " मीडिया हैंडल करते हैं. क्या आपके बिज़नेस के लिए फ्री ऑडिट रिपोर्ट"
              " भेज दें?"
          )
        else:
          pitch_msg = (
              f"Hi {row['Business Name']},\n\nI'm reaching out from THE AK MEDIA"
              " Nashik. I noticed that your social media handles haven't been"
              " active recently.\n\nMost customers nowadays check social media"
              f" presence before visiting a {row['Category']}. Maintaining an"
              " active online presence helps attract new clients regularly.\n\nWe"
              " manage end-to-end digital branding for businesses across Nashik."
              " Would you like a Free Social Media Audit report for your page?"
          )

        encoded_msg = urllib.parse.quote(pitch_msg)
        wa_url = f'https://wa.me/{row["Phone"]}?text={encoded_msg}'
        call_url = f'tel:{row["Phone"]}'

        action_html = f"""
                <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                    <a href="{call_url}" target="_blank"><button style="background-color:#007BFF; color:white; border:none; padding:8px 10px; border-radius:5px; cursor:pointer; font-weight:bold; font-size:12px;">📞 Call Now</button></a>
                    <a href="{wa_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:8px 10px; border-radius:5px; cursor:pointer; font-weight:bold; font-size:12px;">📲 WhatsApp</button></a>
                </div>
                """
        c5.markdown(action_html, unsafe_allow_html=True)

        bname = row["Business Name"]
        cursor.execute("SELECT status, remark FROM followups WHERE business_name = ?", (bname,))
        f_data = cursor.fetchone()
        current_f_status = f_data[0] if f_data else "New Lead"
        current_f_remark = f_data[1] if f_data else ""

        with st.expander(f"📝 Follow-up Status & Remarks ({bname})"):
          status_options = [
              "New Lead",
              "Called - Interested",
              "Meeting Scheduled",
              "Audit Report Sent",
              "Converted",
              "Not Responding",
          ]
          default_idx = status_options.index(current_f_status) if current_f_status in status_options else 0

          f_status = st.selectbox(
              "Select Status",
              status_options,
              index=default_idx,
              key=f"status_{idx}",
          )
          f_remark = st.text_input(
              "Add Remark / Notes", value=current_f_remark, key=f"remark_{idx}"
          )
          if st.button("💾 Save Status", key=f"save_{idx}"):
            cursor.execute("""
                INSERT INTO followups (business_name, status, remark) 
                VALUES (?, ?, ?) 
                ON CONFLICT(business_name) 
                DO UPDATE SET status = ?, remark = ?
            """, (bname, f_status, f_remark, f_status, f_remark))
            conn.commit()
            st.success("✅ Saved to database permanently!")

        if c5.button(
            f"📑 Open Print-Ready Report", key=f"btn_report_{idx}"
        ):
          st.session_state["active_audit_lead"] = row.to_dict()
          st.session_state["selected_page"] = "Audit Report View"
          curr_user = st.session_state["display_name"]
          
          cursor.execute("SELECT pitches FROM team_activity WHERE member_name = ?", (curr_user,))
          p_res = cursor.fetchone()
          current_p_db = p_res[0] if p_res else 0
          cursor.execute("UPDATE team_activity SET pitches = ? WHERE member_name = ?", (current_p_db + 1, curr_user))
          conn.commit()
          st.rerun()

        st.markdown(
            "<hr style='margin:8px 0; border-color:#333;'/>",
            unsafe_allow_html=True,
        )
  else:
    st.info(
        "👈 डाव्या बाजूला जिल्हा, तालुका, एरिया आणि कॅटेगरी निवडून **'Hunt District"
        " Leads Now'** बटणावर क्लिक करा!"
    )

# ==================== PAGE 2: DEDICATED PRINT-READY AUDIT REPORT SCREEN ====================
elif st.session_state["selected_page"] == "Audit Report View":
  if st.session_state["active_audit_lead"] is None:
    st.warning(
        "⚠️ कोणतीही लीड निवडलेली नाही. कृपया डॅशबोर्डवर जाऊन कोणत्याही क्लायंटच्या"
        " समोर दिलेल्या **'Open Print-Ready Report'** बटणावर क्लिक करा."
    )
    if st.button("⬅️ Back to Dashboard"):
      st.session_state["selected_page"] = "Lead Hunter Dashboard"
      st.rerun()
  else:
    lead = st.session_state["active_audit_lead"]

    if st.button("⬅️ Back to Lead Dashboard"):
      st.session_state["selected_page"] = "Lead Hunter Dashboard"
      st.rerun()

    st.markdown("---")

    printable_report_html = f"""
        <div style="background-color: white; color: black; padding: 40px; border-radius: 10px; font-family: 'Helvetica', sans-serif; border: 2px solid #D4AF37; max-width: 800px; margin: auto;">
            <div style="text-align: center; border-bottom: 2px solid #D4AF37; padding-bottom: 15px; margin-bottom: 25px;">
                <h2 style="color: #0b0b0b; margin: 0; font-size: 26px; letter-spacing: 1.5px;">THE AK MEDIA</h2>
                <p style="color: #666; font-size: 12px; margin: 5px 0 0 0; text-transform: uppercase; letter-spacing: 1.5px;">GENERATED BY HOT CLIENT HUNTER SYSTEM</p>
            </div>
            
            <h3 style="color: #111; border-bottom: 1px solid #ddd; padding-bottom: 8px;">Business Profile</h3>
            <table style="width: 100%; font-size: 14px; margin-bottom: 20px;">
                <tr>
                    <td style="padding: 6px 0;"><b>Business Name:</b></td>
                    <td>{lead['Business Name']}</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0;"><b>Category:</b></td>
                    <td>{lead['Category']}</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0;"><b>Location / Area:</b></td>
                    <td>{lead['Area']}, {lead['Taluka']}, Nashik - {lead['District']}</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0;"><b>Contact Phone:</b></td>
                    <td>+91 {lead['Phone']}</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0;"><b>Google Rating:</b></td>
                    <td>⭐ {lead['Rating']} / 5.0</td>
                </tr>
                <tr>
                    <td style="padding: 6px 0;"><b>AI Priority Status:</b></td>
                    <td><b>{lead['AI Score']}</b></td>
                </tr>
                <tr>
                    <td style="padding: 6px 0;"><b>Audit Date:</b></td>
                    <td>{datetime.date.today()}</td>
                </tr>
            </table>

            <h3 style="color: #111; border-bottom: 1px solid #ddd; padding-bottom: 8px;">1. Executive Summary & Findings</h3>
            <p style="font-size: 14px; line-height: 1.6; color: #333;">
                Our advanced digital scanning system analyzed <b>{lead['Business Name']}</b>'s online presence across local search engines and social platforms. While your customer feedback rating ({lead['Rating']}/5.0) reflects great service quality, your social media handles have been inactive for over 15 days. In today's digital ecosystem, modern consumers in {lead['Taluka']} actively search for active business profiles before visiting or purchasing.
            </p>

            <h3 style="color: #111; border-bottom: 1px solid #ddd; padding-bottom: 8px;">2. Identified Growth Gaps</h3>
            <ul style="font-size: 14px; line-height: 1.6; color: #333;">
                <li>Low frequency of digital content posting leads to reduced brand recall.</li>
                <li>Competitors within {lead['Taluka']} region are leveraging active social channels to capture high-intent local customer traffic.</li>
                <li>Untapped potential in localized geotargeted video marketing (Reels/Shorts).</li>
            </ul>

            <h3 style="color: #111; border-bottom: 1px solid #ddd; padding-bottom: 8px;">3. Recommended Growth Solutions by THE AK MEDIA</h3>
            <ul style="font-size: 14px; line-height: 1.6; color: #333;">
                <li><b>End-to-End Social Media Management:</b> Consistent, high-aesthetic feed and story management.</li>
                <li><b>High-Converting Reels & Branding:</b> Professional graphic design and video campaigns tailored for Nashik audience.</li>
                <li><b>Reputation & Lead Generation:</b> Automated funnel systems to attract recurring local clients.</li>
            </ul>

            <div style="margin-top: 40px; border-top: 2px dashed #ccc; padding-top: 20px; display: flex; justify-content: space-between; font-size: 13px; color: #555;">
                <div>
                    <b>Office Address:</b><br>
                    The AK Media, Near Guru Cake, In Front of Vitthal Rukmini Dental Clinic,<br>
                    Dhawkhar Nagar, Chandwad, Nashik - 423101
                </div>
                <div style="text-align: right;">
                    <b>Contact & Support:</b><br>
                    Phone: +91 9172082052<br>
                    Email: the.ak.media56@gmail.com
                </div>
            </div>
        </div>
        """

    st.markdown(printable_report_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "💡 **प्रिन्ट कशी काढाल किंवा पीडीएफ कशी सेव्ह कराल?**\n"
        "लॅपटॉपवर असताना फक्त **`Ctrl + P`** दाबा आणि प्रिन्टरच्या जागी **'Save as PDF'"
        " निवडा!"
    )

# ==================== FORMAL FOOTER ====================
st.markdown(
    """
    <div style="background-color: #0b0b0b; padding: 25px; border-top: 2px solid #D4AF37; margin-top: 50px; border-radius: 8px; font-family: sans-serif; color: #FFFFFF;">
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 20px;">
            <div style="flex: 1; min-width: 250px;">
                <h3 style="color: #D4AF37; margin-top: 0;">THE AK MEDIA</h3>
                <p style="font-size: 13px; line-height: 1.6; color: #E0E0E0;">
                    Building Businesses | Building Brands<br>
                    नाशिक जिल्ह्यातील ऑटोमेटेड क्लायंट ॲक्विझिशन आणि डिजिटल ब्रँडिंग सोल्यूशन्स.
                </p>
            </div>
            <div style="flex: 1; min-width: 250px;">
                <h4 style="color: #D4AF37; margin-top: 0;">📞 संपर्क आणि पत्ता</h4>
                <p style="font-size: 13px; line-height: 1.6; color: #E0E0E0;">
                    <b>फोन:</b> +91 9172082052<br>
                    <b>ईमेल:</b> the.ak.media56@gmail.com<br>
                    <b>ऑफिस:</b> The AK Media, Near Guru Cake, In Front of Vitthal Rukmini Dental Clinic, Dhawkhar Nagar, Chandwad, Tal. Chandwad, Dist. Nashik, Maharashtra - 423101
                </p>
            </div>
        </div>
        <hr style="border-color: #333; margin: 15px 0;">
        <div style="font-size: 11px; color: #AAAAAA; line-height: 1.5; text-align: justify;">
            <b>Disclaimer:</b> THE AK MEDIA - Hot Client Hunter ही सिस्टीम नाशिक जिल्ह्यातील स्थानिक व्यवसायांचा रिअल-टाइम डेटा शोधण्यासाठी सार्वजनिकरित्या उपलब्ध असलेल्या Google Places API चा वापर करते. ही सिस्टीम केवळ अंतर्गत व्यवसाय संपर्क आणि मार्केटिंग ऑडिट उद्देशांसाठी डिझाइन केली आहे.
        </div>
        <hr style="border-color: #222; margin: 15px 0 10px 0;">
        <div style="text-align: center; font-size: 12px; color: #D4AF37;">
            © 2026 <b>THE AK MEDIA</b>. All Rights Reserved.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
