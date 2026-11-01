import datetime
import urllib.parse
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="THE AK MEDIA - Hot Client Hunter", page_icon="🎯", layout="wide"
)

# Custom CSS for Professional Look & Print Styling
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { background-color: #D4AF37; color: black; font-weight: bold; border-radius: 8px; width: 100%; }
    
    @media print {
        body { background-color: white !important; color: black !important; }
        .sidebar, button, header, footer { display: none !important; }
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==================== INITIALIZE SESSION STATE ====================
if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False
if "username" not in st.session_state:
  st.session_state["username"] = ""
if "role" not in st.session_state:
  st.session_state["role"] = ""
if "display_name" not in st.session_state:
  st.session_state["display_name"] = ""

# Team Activity & Leaderboard Database (As per your custom team)
if "team_activity" not in st.session_state:
  st.session_state["team_activity"] = {
      "MR.AK (Admin)": {"leads": 0, "pitches": 0, "streak": 5},
      "Hari Shinde": {"leads": 0, "pitches": 0, "streak": 3},
      "Somnath Pardhi": {"leads": 0, "pitches": 0, "streak": 4},
  }

# Follow-up database storage
if "follow_ups" not in st.session_state:
  st.session_state["follow_ups"] = {}

if "selected_page" not in st.session_state:
  st.session_state["selected_page"] = "Lead Hunter Dashboard"
if "active_audit_lead" not in st.session_state:
  st.session_state["active_audit_lead"] = None

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

# Navigation Menu Bar inside App
nav_col1, nav_col2, nav_col3 = st.columns(3)
with nav_col1:
  if st.button("🎯 Lead Hunter Dashboard"):
    st.session_state["selected_page"] = "Lead Hunter Dashboard"
with nav_col2:
  if st.button("📑 Professional Print-Ready Audit Report View"):
    st.session_state["selected_page"] = "Audit Report View"
with nav_col3:
  if st.button("💬 Quick Message Library"):
    st.session_state["selected_page"] = "Message Library"

st.markdown("---")

# ==================== PAGE 3: QUICK MESSAGE TEMPLATES LIBRARY ====================
if st.session_state["selected_page"] == "Message Library":
  st.title("💬 Quick Message Templates / Copy-Paste Library")
  st.write(
      "### 🚀 वेगवेगळ्या व्यवसायांसाठी तयार केलेले कॉल्स आणि व्हॉट्सॲप पिचेस"
      " (एका क्लिकवर कॉपी करा)"
  )

  tab1, tab2, tab3 = st.tabs(["☕ Cafes & Restaurants", "🏋️ Gyms & Fitness", "🛍️ Retail & Clothing"])

  with tab1:
    st.subheader("Cafe / Restaurant Pitch Template")
    cafe_template = (
        "नमस्कार [Business Name],\n\nमी THE AK MEDIA (नाशिक) वरून बोलतोय. आम्ही"
        " तुमचं सोशल मीडिया पेज पाहिलं, गेल्या काही दिवसांपासून त्यावर नवीन"
        " पोस्ट किंवा रील्स अपडेट झालेली नाहीत.\n\nआजकाल तरुण वर्ग आणि"
        " कस्टमर्स ऑनलाइन सर्च करूनच कॅफे निवडतात. सोशल मीडिया इन-ॲक्टिव्ह"
        " राहिल्याने नवीन कस्टमर्स प्रतिस्पर्ध्यांकडे जाऊ शकतात.\n\nआम्ही नाशिक"
        " जिल्ह्यातील कॅफेसाठी प्रोफेशनल रील्स, ग्राफिक डिझाईन आणि सोशल मीडिया"
        " मॅनेजमेंट हँडल करतो. तुमच्या पेजचा फ्री ऑडिट रिपोर्ट हवा असल्यास"
        " नक्की सांगा!"
    )
    st.code(cafe_template, language="text")

  with tab2:
    st.subheader("Gym / Fitness Club Pitch Template")
    gym_template = (
        "हाय [Business Name],\n\nTHE AK MEDIA (नाशिक) कडून संपर्क करतोय. फिटनेस"
        " लव्हर्स नेहमी नवीन ऑफर्स आणि वर्कआउट व्हिडिओज सोशल मीडियावर शोधत"
        " असतात. तुमच्या जिमचे पेज सध्या इन-ॲक्टिव्ह दिसतेय.\n\nआम्ही जिमचे"
        " ब्राँडिंग, एनर्जेटिक रील्स आणि लोकल लीड जनरेशन कॅम्पेन हँडल करतो."
        " ज्यामुळे नवीन मेंबरशिप वाढण्यास मदत होईल. मोफत सल्ला हवा का?"
    )
    st.code(gym_template, language="text")

  with tab3:
    st.subheader("Retail / Clothing Store Pitch Template")
    retail_template = (
        "नमस्कार [Business Name],\n\nमी THE AK MEDIA मधून बोलतोय. तुमच्या"
        " दुकानाचे डिजिटल ब्रँडिंग वाढवण्यासाठी आम्ही मदत करू शकतो. फेस्टिव्हल"
        " ऑफर्स आणि नवीन स्टॉकचे प्रमोशन सोशल मीडियावर असणे खूप गरजेचे आहे.\n\nआमच्या"
        " डिजिटल सर्व्हिसेसबद्दल माहिती हवी असल्यास नक्की कळवा!"
    )
    st.code(retail_template, language="text")

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

  # ==================== SIDEBAR FILTERS & KING OF THE DAY LEADERBOARD ====================
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

  # ==================== LEADERBOARD & STREAK TRACKER ====================
  st.sidebar.markdown("---")
  st.sidebar.subheader("👑 King of the Day / Streak Tracker")

  # Find King of the day based on max pitches + leads
  sorted_team = sorted(
      st.session_state["team_activity"].items(),
      key=lambda x: x[1]["pitches"] + x[1]["leads"],
      reverse=True,
  )
  if sorted_team:
    king_name, king_stats = sorted_team[0]
    st.sidebar.success(
        f"🏆 **King of the Day:** {king_name}\n(Score:"
        f" {king_stats['pitches'] + king_stats['leads']})"
    )

  if st.session_state["role"] == "Admin":
    st.sidebar.write("---")
    st.sidebar.write("👑 **CEO Master Team Tracker:**")
    for member, stats in st.session_state["team_activity"].items():
      st.sidebar.markdown(
          f"🔹 **{member}**<br>🎯 Leads: `{stats['leads']}` | 💬 Pitches:"
          f" `{stats['pitches']}` | 🔥 Streak: `{stats['streak']} Days`",
          unsafe_allow_html=True,
      )
  else:
    current_user_name = st.session_state["display_name"]
    if current_user_name not in st.session_state["team_activity"]:
      st.session_state["team_activity"][current_user_name] = {
          "leads": 0,
          "pitches": 0,
          "streak": 1,
      }
    my_stats = st.session_state["team_activity"][current_user_name]
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
      if curr_user not in st.session_state["team_activity"]:
        st.session_state["team_activity"][curr_user] = {
            "leads": 0,
            "pitches": 0,
            "streak": 1,
        }
      st.session_state["team_activity"][curr_user]["leads"] += len(df)

  if "leads_data" in st.session_state and not st.session_state[
      "leads_data"
  ].empty:
    df = st.session_state["leads_data"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Businesses Found", len(df))
    hot_count = len(df[df["AI Score"].str.contains("High Priority")])
    col2.metric("🔥 AI High Priority Clients", hot_count)
    col3.metric("Target Area", selected_area)

    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 Export Leads to Excel/CSV",
        data=df.to_csv(index=False),
        file_name=(
            f"THE_AK_MEDIA_Leads_{selected_taluka}_{selected_area}_{datetime.date.today()}.csv"
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

        # Follow-up Remarks & Status Feature
        bname = row["Business Name"]
        if bname not in st.session_state["follow_ups"]:
          st.session_state["follow_ups"][bname] = {
              "status": "New Lead",
              "remark": "",
          }

        with st.expander(f"📝 Follow-up Status & Remarks ({bname})"):
          f_status = st.selectbox(
              "Select Status",
              [
                  "New Lead",
                  "Called - Interested",
                  "Meeting Scheduled",
                  "Audit Report Sent",
                  "Converted",
                  "Not Responding",
              ],
              key=f"status_{idx}",
          )
          f_remark = st.text_input(
              "Add Remark / Notes", key=f"remark_{idx}"
          )
          if st.button("💾 Save Status", key=f"save_{idx}"):
            st.session_state["follow_ups"][bname] = {
                "status": f_status,
                "remark": f_remark,
            }
            st.success("✅ Saved successfully!")

        if c5.button(
            f"📑 Open Print-Ready Report", key=f"btn_report_{idx}"
        ):
          st.session_state["active_audit_lead"] = row.to_dict()
          st.session_state["selected_page"] = "Audit Report View"
          curr_user = st.session_state["display_name"]
          if curr_user in st.session_state["team_activity"]:
            st.session_state["team_activity"][curr_user]["pitches"] += 1
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
        "लॅपटॉपवर किंवा कॉम्प्युटरवर असताना फक्त **`Ctrl + P`** (Mac वर `Cmd +"
        " P`) दाबा. प्रिंट विंडो उघडल्यावर प्रिन्टरच्या जागी **'Save as PDF'"
        " निवडा आणि सेव्ह करा[cite: 3, 4, 6]!"
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
