import datetime
import urllib.parse
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="AK MEDIA - Hot Client Hunter", page_icon="🎯", layout="wide"
)

st.title("🎯 AK MEDIA - Hot Client Hunter (Nashik District)")
st.write(
    "### 🚀 नाशिक जिल्ह्यातील इन-ॲक्टिव्ह क्लायंट्स शोधा आणि एका क्लिकवर व्हॉट्सॲप"
    " पिच पाठवा!"
)

# Sidebar Setup with Hierarchical Filters
st.sidebar.header("🔍 Search Filters")

# 1. Taluka Selection
taluka_options = {
    "Chandwad": [
        "Bus Stand Area, Chandwad",
        "Main Market, Chandwad",
        "Manmath Nagar, Chandwad",
        "Deola Road, Chandwad",
    ],
    "Nashik City": [
        "College Road, Nashik",
        "Gangapur Road, Nashik",
        "Cidco, Nashik",
        "Indiranagar, Nashik",
        "Panchavati, Nashik",
        "Satpur, Nashik",
    ],
    "Sinnar": [
        "Pune Road, Sinnar",
        "Main Bazar, Sinnar",
        "MIDC Sinnar",
    ],
    "Malegaon": [
        "Camp Road, Malegaon",
        "Kidwai Road, Malegaon",
        "Main Road, Malegaon",
    ],
    "Igatpuri": [
        "Station Road, Igatpuri",
        "Mumbai-Nashik Highway, Igatpuri",
    ],
    "Yeola": [
        "Vinchur Road, Yeola",
        "Main Bazar, Yeola",
    ],
}

selected_taluka = st.sidebar.selectbox(
    "१. तालुका निवडा (Taluka)", list(taluka_options.keys())
)

# 2. Area Selection
selected_area = st.sidebar.selectbox(
    "२. विशिष्ट एरिया निवडा (Area)", taluka_options[selected_taluka]
)

# 3. Category Selection
category_input = st.sidebar.selectbox(
    "३. कॅटेगरी निवडा (Category)",
    [
        "Cafe",
        "Restaurant",
        "Gym",
        "Salon",
        "Beauty Parlour",
        "Clothing Store",
        "Coaching Classes",
        "Bakery",
    ],
)

# 4. Multi-Language Pitch Selection (नवी सोय)
pitch_language = st.sidebar.selectbox(
    "🌐 पिचची भाषा निवडा (Pitch Language)",
    ["Marathi (मराठी)", "Hindi (हिंदी)", "English"],
)

# Secrets मधून API Key शोधणे किंवा Sidebar मध्ये Input देणे
secret_key = st.secrets.get("GOOGLE_API_KEY", "")
if not secret_key:
  api_key = st.sidebar.text_input(
      "🔑 Google API Key टाका", type="password", help="इथे तुझी API Key टाक"
  )
else:
  api_key = secret_key


# Google Places API (New) Query Function
def fetch_strict_area_places(taluka, area, category, key):
  if not key:
    st.error(
        "⚠️ Google API Key सापडली नाही! डाव्या बाजूला 'Google API Key' टाका किंवा"
        " Streamlit Secrets मध्ये सेट करा."
    )
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
      st.error(
          f"❌ Google API Error: {data['error'].get('status')} - "
          f"{data['error'].get('message')}"
      )
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


if st.sidebar.button("🎯 Hunt Area Leads Now"):
  with st.spinner(
      f"🔍 Fetching real-time leads specifically for {selected_area}..."
  ):
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
  hot_count = len(df[df["Status"] == "HOT"])
  col2.metric("🔥 HOT Clients", hot_count)
  col3.metric("Target Area", selected_area)

  # Excel Export Button
  st.sidebar.markdown("---")
  st.sidebar.download_button(
      label="📥 Export Leads to Excel/CSV",
      data=df.to_csv(index=False),
      file_name=(
          f"AK_MEDIA_Leads_{selected_area}_{datetime.date.today()}.csv"
      ),
      mime="text/csv",
  )

  st.markdown("---")
  st.subheader(f"📋 Client Lead Board — {selected_area} ({category_input})")

  for idx, row in df.iterrows():
    with st.container():
      c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1.5, 1, 2.5])
      c1.write(f"**{row['Business Name']}**\n📍 {row['Area']}")
      c2.write(f"🏷️ {row['Category']}\n⭐ Rating: {row['Rating']}")
      c3.write(f"📅 Last Post: {row['Last Post']}")
      c4.error(f"🔥 {row['Status']}")

      # Dynamic Multi-language Pitch logic
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
      "👈 डाव्या बाजूला तालुका, एरिया, कॅटेगरी आणि **भाषा** निवडून **'Hunt Area"
      " Leads Now'** बटणावर क्लिक करा!"
  )
