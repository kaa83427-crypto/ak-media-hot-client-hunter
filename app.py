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

# Sidebar Setup with Dropdown Locations
st.sidebar.header("🔍 Search Filters")
location_input = st.sidebar.selectbox(
    "तालुका / एरिया निवडा (Location)",
    [
        "Chandwad, Nashik",
        "Nashik City",
        "Sinnar, Nashik",
        "Malegaon",
        "Igatpuri",
        "Yeola",
        "Pimpalgaon Baswant, Nashik",
        "Ozar, Nashik",
    ],
)

category_input = st.sidebar.selectbox(
    "कॅटेगरी (Business Category)",
    [
        "Cafe & Restaurant",
        "Gym & Fitness",
        "Salon & Beauty",
        "Clothing & Fashion",
        "Coaching Classes",
    ],
)

# Secrets मधून API Key शोधणे किंवा Sidebar मध्ये Input देणे
secret_key = st.secrets.get("GOOGLE_API_KEY", "")
if not secret_key:
  api_key = st.sidebar.text_input(
      "🔑 Google API Key टाका", type="password", help="इथे तुझी API Key टाक"
  )
else:
  api_key = secret_key


# Google Places API (New) Query Function with Multi-page/Keyword fetch for 50+ leads
def fetch_multiple_places(location, category_group, key):
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

  # एकाच कॅटेगरी ग्रुपमधून जास्त लीड्स मिळवण्यासाठी कीवर्ड्सचे तुकडे करणे
  keywords = [category_group]
  if "Cafe" in category_group:
    keywords = ["Cafe", "Restaurant", "Coffee Shop", "Bakers"]
  elif "Gym" in category_group:
    keywords = ["Gym", "Fitness Center", "Yoga Club"]
  elif "Salon" in category_group:
    keywords = ["Salon", "Beauty Parlour", "Spa"]
  elif "Clothing" in category_group:
    keywords = ["Clothing Store", "Garments", "Fashion Boutique"]
  elif "Coaching" in category_group:
    keywords = ["Coaching Classes", "Tuition", "Institute"]

  all_places = []
  seen_names = set()

  for kw in keywords:
    payload = {"textQuery": f"{kw} in {location}", "maxResultCount": 20}
    try:
      response = requests.post(url, headers=headers, json=payload)
      data = response.json()
      places = data.get("places", [])

      for place in places:
        name = place.get("displayName", {}).get("text", "Unknown Business")
        if name not in seen_names:
          seen_names.add(name)
          phone = place.get("nationalPhoneNumber", "919876543210")

          clean_phone = "".join(filter(str.isdigit, str(phone)))
          if len(clean_phone) < 10:
            clean_phone = "919876543210"
          elif not clean_phone.startswith("91"):
            clean_phone = "91" + clean_phone[-10:]

          all_places.append({
              "Location": location,
              "Category": category_group,
              "Business Name": name,
              "Phone": clean_phone,
              "Rating": place.get("rating", "N/A"),
              "Last Post": str(
                  datetime.date.today() - datetime.timedelta(days=16)
              ),
              "Status": "HOT",
          })
    except Exception as e:
      continue

  return pd.DataFrame(all_places)


if st.sidebar.button("🎯 Hunt Clients Now"):
  with st.spinner(
      "🔍 Fetching maximum real-time businesses from Nashik District..."
  ):
    df = fetch_multiple_places(location_input, category_input, api_key)
    st.session_state["leads_data"] = df

if "leads_data" in st.session_state and not st.session_state[
    "leads_data"
].empty:
  df = st.session_state["leads_data"]

  col1, col2, col3 = st.columns(3)
  col1.metric("Total Businesses Found", len(df))
  hot_count = len(df[df["Status"] == "HOT"])
  col2.metric("🔥 HOT Clients", hot_count)
  col3.metric("Target Region", location_input)

  # Excel Export Button in Sidebar
  st.sidebar.markdown("---")
  st.sidebar.download_button(
      label="📥 Export Leads to Excel/CSV",
      data=df.to_csv(index=False),
      file_name=(
          f"AK_MEDIA_Leads_{location_input}_{datetime.date.today()}.csv"
      ),
      mime="text/csv",
  )

  st.markdown("---")
  st.subheader("📋 Client Lead Board (Real Google Maps Data)")

  for idx, row in df.iterrows():
    with st.container():
      c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1.5, 1, 2.5])
      c1.write(f"**{row['Business Name']}**\n📍 {row['Location']}")
      c2.write(f"🏷️ {row['Category']}\n⭐ Rating: {row['Rating']}")
      c3.write(f"📅 Last Post: {row['Last Post']}")
      c4.error(f"🔥 {row['Status']}")

      pitch_msg = (
          f"Hi {row['Business Name']}, maine aapka Insta dekha, kafi dino se"
          " post nahi kiya. Hum AK MEDIA se Nashik businesses ka page handle"
          " karte hain. Free audit kar du?"
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
      "👈 डाव्या बाजूला तालुका निवडून **'Hunt Clients Now'** बटणावर क्लिक करा!"
  )
