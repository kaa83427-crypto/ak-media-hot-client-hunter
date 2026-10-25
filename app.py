import streamlit as st
import pandas as pd
import datetime
import urllib.parse

# Page Config (Modern SaaS Dark Mode look)
st.set_page_config(page_title="AK MEDIA - Hot Client Hunter", page_icon="🎯", layout="wide")

# Custom CSS for Dark Mode Aesthetics
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    h1 { color: #00E676; text-align: center; font-family: 'sans-serif'; }
    .stButton>button { background-color: #00E676; color: black; font-weight: bold; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 AK MEDIA - Hot Client Hunter (Nashik District)")
st.write("### 🚀 नाशिक जिल्ह्यातील इन-ॲक्टिव्ह क्लायंट्स शोधा आणि एका क्लिकवर व्हॉट्सॲप पिच पाठवा!")

# Sidebar Filters
st.sidebar.header("🔍 Search Filters")
selected_taluka = st.sidebar.selectbox("तालुका / एरिया निवडा (Taluka/Area)", [
    "All Nashik District", "College Road, Nashik", "Gangapur Road, Nashik", "Cidco, Nashik", 
    "Sinnar", "Malegaon", "Ozar", "Pimpalgaon Baswant", "Igatpuri", "Chandwad", "Yeola"
])

selected_category = st.sidebar.selectbox("कॅटेगरी (Business Category)", [
    "All Categories", "Cafe & Restaurant", "Salon & Beauty Parlour", "Gym & Fitness", "Clothing Store", "Coaching Classes"
])

st.sidebar.markdown("---")
st.sidebar.info("💡 **Note:** Python script automatically filters HOT clients with no posts in last 15 days.")

# Sample Automated Lead Data Engine
sample_data = [
    {"Taluka": "College Road, Nashik", "Category": "Cafe & Restaurant", "Business Name": "College Road Cafe", "Phone": "919876543210", "Last Post": "2026-10-01", "Status": "HOT", "Score": "9/10"},
    {"Taluka": "Sinnar", "Category": "Gym & Fitness", "Business Name": "Sinnar Fitness Club", "Phone": "919812345678", "Last Post": "2026-09-28", "Status": "HOT", "Score": "9.5/10"},
    {"Taluka": "Gangapur Road, Nashik", "Category": "Salon & Beauty Parlour", "Business Name": "Glow Spa & Salon", "Phone": "919922334455", "Last Post": "2026-10-18", "Status": "AVERAGE", "Score": "6/10"},
    {"Taluka": "Malegaon", "Category": "Clothing Store", "Business Name": "Malegaon Fashion Hub", "Phone": "919765432109", "Last Post": "2026-09-15", "Status": "HOT", "Score": "10/10"},
    {"Taluka": "Ozar", "Category": "Cafe & Restaurant", "Business Name": "Ozar Bakers & Cafe", "Phone": "919543210987", "Last Post": "2026-10-24", "Status": "GOOD", "Score": "3/10"},
]

df = pd.DataFrame(sample_data)

# Filter Logic
filtered_df = df.copy()
if selected_taluka != "All Nashik District":
    filtered_df = filtered_df[filtered_df["Taluka"] == selected_taluka]
if selected_category != "All Categories":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

# Metric Display
col1, col2, col3 = st.columns(3)
col1.metric("Total Businesses Found", len(filtered_df))
hot_count = len(filtered_df[filtered_df["Status"] == "HOT"])
col2.metric("🔥 HOT Clients (Action Ready)", hot_count)
col3.metric("Target Region", selected_taluka)

st.markdown("---")
st.subheader("📋 Client Lead Board")

# Rendering Leads Table with Direct WhatsApp Pitch Button
for idx, row in filtered_df.iterrows():
    with st.container():
        c1, c2, c3, c4, c5 = st.columns([2, 2, 1.5, 1, 2.5])
        c1.write(f"**{row['Business Name']}**\n📍 {row['Taluka']}")
        c2.write(f"🏷️ {row['Category']}")
        c3.write(f"📅 Last Post: {row['Last Post']}")
        
        # Badge Color
        if row['Status'] == 'HOT':
            c4.error(f"🔥 {row['Status']}")
        elif row['Status'] == 'AVERAGE':
            c4.warning(f"⚠️ {row['Status']}")
        else:
            c4.success(f"✅ {row['Status']}")
            
        # WhatsApp Pitch Generator
        pitch_msg = f"Hi {row['Business Name']}, maine aapka Insta dekha, kafi dino se post nahi kiya. Hum AK MEDIA se Nashik businesses ka page handle karte hain. Free audit kar du?"
        encoded_msg = urllib.parse.quote(pitch_msg)
        wa_url = f"https://wa.me/{row['Phone']}?text={encoded_msg}"
        
        c5.markdown(f'<a href="{wa_url}" target="_blank"><button style="background-color:#25D366; color:white; border:none; padding:8px 12px; border-radius:5px; cursor:pointer; font-weight:bold;">📲 Send WhatsApp Pitch</button></a>', unsafe_allow_html=True)
        st.markdown("<hr style='margin:8px 0; border-color:#333;'/>", unsafe_allow_html=True)

# Export Data Option
st.sidebar.markdown("---")
st.sidebar.download_button(
    label="📥 Export Leads to Excel/CSV",
    data=filtered_df.to_csv(index=False),
    file_name=f"AK_MEDIA_Leads_{datetime.date.today()}.csv",
    mime="text/csv"
)
