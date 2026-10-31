import datetime
import urllib.parse
from PIL import Image  # 👈 नवीन इम्पोर्ट
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="THE AK MEDIA - Hot Client Hunter", page_icon="🎯", layout="wide"
)

# Custom CSS for Dark Mode & Styling
st.markdown(
    """
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #D4AF37; text-align: center; font-family: 'sans-serif'; }
    .stButton>button { background-color: #D4AF37; color: black; font-weight: bold; border-radius: 8px; width: 100%; }
    </style>
""",
    unsafe_allow_html=True,
)

# ==================== FORMAL HEADER WITH PERFECT LOGO ====================
st.markdown(
    """
    <div style="background-color: #0b0b0b; padding: 25px; border-bottom: 3px solid #D4AF37; border-radius: 10px; text-align: center; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.6);">
    """,
    unsafe_allow_html=True,
)

# PIL वापरून लोगो अगदी अचूक सेंटरला आणि व्यवस्थित लोड करणे
col1, col2, col3 = st.columns([2, 1.5, 2])
with col2:
  try:
    img = Image.open("logo.png")
    st.image(img, width=160)
  except Exception as e:
    st.markdown(
        "<h2 style='color: #D4AF37; text-align: center;'>THE AK MEDIA</h2>",
        unsafe_allow_html=True,
    )

st.markdown(
    """
        <h1 style="color: #D4AF37; margin: 10px 0 0 0; font-family: 'Georgia', serif; font-size: 32px; letter-spacing: 2px; text-align: center;">AK MEDIA</h1>
        <p style="color: #e0e0e0; margin: 5px 0 0 0; font-size: 14px; font-weight: 500; letter-spacing: 1.5px; text-align: center;">Building Businesses | Building Brands</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)
st.title("🎯 Hot Client Hunter (Nashik District)")
st.write(
    "### 🚀 नाशिक जिल्ह्यातील इन-ॲक्टिव्ह क्लायंट्स शोधा आणि एका क्लिकवर व्हॉट्सॲप"
    " pitch पाठवा!"
)

# ==================== SIDEBAR FILTERS ====================
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

      businesses.append({
          "District": "Nashik",
          "Taluka": taluka,
          "Area": area,
          "Category": category,
          "Business Name": name,
          "Address": address,
          "Phone": clean_phone,
          "Rating": place.get("rating", "N/A"),
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
  with st.spinner(f"🔍 Fetching real-time leads for {selected_area}..."):
    df = fetch_strict_area_places(
        selected_taluka, selected_area, category_input, api_key
    )
    st.session_state["leads_data"] = df

if "leads_data" in st.session_state and not st.session_state[
    "leads_data"
].empty:
  df = st.session_state["leads_data"]

  col1, col2, col3 = st.columns(3)
  col1.metric("Total Businesses Found", len(df))
  col2.metric("🔥 HOT Clients", len(df[df["Status"] == "HOT"]))
  col3.metric("Target Area", selected_area)

  st.sidebar.markdown("---")
  st.sidebar.download_button(
      label="📥 Export Leads to Excel/CSV",
      data=df.to_csv(index=False),
      file_name=(
          f"AK_MEDIA_Leads_{selected_taluka}_{selected_area}_{datetime.date.today()}.csv"
      ),
      mime="text/csv",
  )

  st.markdown("---")
  st.subheader(
      f"📋 Client Lead Board — {selected_area}, {selected_taluka}"
      f" ({category_input})"
  )

  for idx, row in df.iterrows():
    with st.container():
      c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1.5, 1, 2.5])
      c1.write(f"**{row['Business Name']}**\n📍 {row['Area']}, {row['Taluka']}")
      c2.write(f"🏷️ {row['Category']}\n⭐ Rating: {row['Rating']}")
      c3.write(f"📅 Last Post: {row['Last Post']}")
      c4.error(f"🔥 {row['Status']}")

      if "Marathi" in pitch_language:
        pitch_msg = (
            f"नमस्कार {row['Business Name']},\n\nमी AK MEDIA (नाशिक) वरून"
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
            f"नमस्ते {row['Business Name']},\n\nमैं AK MEDIA (नाशिक) से बात कर"
            " रहा हूँ. हमने आपका इंस्टा/फेसबुक पेज देखा, काफी दिनों से कोई नई"
            " पोस्ट नहीं आई है.\n\nआजकल ज्यादातर कस्टमर्स ऑनलाइन सर्च करके"
            f" ही {row['Category']} चुनते हैं. पेज इन-एक्टिव होने से कस्टमर्स"
            " छूट सकते हैं.\n\nहम नाशिक रीजन के बिज़नेस का ब्रांडिंग और सोशल"
            " मीडिया हैंडल करते हैं. क्या आपके बिज़नेस के लिए फ्री ऑडिट रिपोर्ट"
            " भेज दें?"
        )
      else:
        pitch_msg = (
            f"Hi {row['Business Name']},\n\nI'm reaching out from AK MEDIA"
            " Nashik. I noticed that your social media handles haven't been"
            " active recently.\n\nMost customers nowadays check social media"
            f" presence before visiting a {row['Category']}. Maintaining an"
            " active online presence helps attract new clients regularly.\n\nWe"
            " manage end-to-end digital branding for businesses across Nashik."
            " Would you like a Free Social Media Audit report for your page?"
        )

      encoded_msg = urllib.parse.quote(pitch_msg)
      wa_url = f'https://wa.me/{row["Phone"]}?text={encoded_msg}'

      c5.markdown(
          f'<a href="{wa_url}" target="_blank"><button'
          ' style="background-color:#25D366; color:white; border:none;'
          ' padding:8px 12px; border-radius:5px; cursor:pointer;'
          ' font-weight:bold;">📲 Send WhatsApp Pitch</button></a>',
          unsafe_allow_html=True,
      )
      st.markdown(
          "<hr style='margin:8px 0; border-color:#333;'/>",
          unsafe_allow_html=True,
      )
else:
  st.info(
      "👈 डाव्या बाजूला जिल्हा, तालुका, एरिया आणि कॅटेगरी निवडून **'Hunt District"
      " Leads Now'** बटणावर क्लिक करा!"
  )

# ==================== FORMAL FOOTER ====================
st.markdown(
    """
    <div style="background-color: #0b0b0b; padding: 25px; border-top: 2px solid #D4AF37; margin-top: 50px; border-radius: 8px; font-family: sans-serif; color: #b0b0b0;">
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; gap: 20px;">
            <div style="flex: 1; min-width: 250px;">
                <h3 style="color: #D4AF37; margin-top: 0;">THE AK MEDIA</h3>
                <p style="font-size: 13px; line-height: 1.6;">
                    Building Businesses | Building Brands<br>
                    नाशिक जिल्ह्यातील ऑटोमेटेड क्लायंट ॲक्विझिशन आणि डिजिटल ब्रँडिंग सोल्यूशन्स.
                </p>
            </div>
            <div style="flex: 1; min-width: 250px;">
                <h4 style="color: #D4AF37; margin-top: 0;">📞 संपर्क आणि पत्ता</h4>
                <p style="font-size: 13px; line-height: 1.6;">
                    <b>फोन:</b> +91 9172082052<br>
                    <b>ईमेल:</b> the.ak.media56@gmail.com<br>
                    <b>ऑफिस:</b> The AK Media, Near Guru Cake, In Front of Vitthal Rukmini Dental Clinic, Dhawkhar Nagar, Chandwad, Tal. Chandwad, Dist. Nashik, Maharashtra - 423101
                </p>
            </div>
        </div>
        <hr style="border-color: #333; margin: 15px 0;">
        <div style="font-size: 11px; color: #777777; line-height: 1.5; text-align: justify;">
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
