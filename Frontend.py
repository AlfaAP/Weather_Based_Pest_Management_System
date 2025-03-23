import logging
import streamlit as st
import requests
import time
from streamlit_lottie import st_lottie

# Configure logging
logging.getLogger("streamlit").setLevel(logging.CRITICAL)

# Hide Streamlit error messages
st.markdown(
    """
    <style>
    .stException { display: none; }
    .stButton>button { background-color: #007bff; color: white; border-radius: 20px; padding: 10px 20px; }
    </style>
    """,
    unsafe_allow_html=True
)

# API URL - Adjust this based on your backend deployment
BASE_URL = "https://final-backend-35fg.onrender.com"

# Load Lottie Animation for better UI experience
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            st.warning("Failed to load animation. Please check the URL.")
    except Exception as e:
        st.error(f"Error loading animation: {e}")
    return None

lottie_plant = load_lottie_url("https://assets7.lottiefiles.com/packages/lf20_dyjyfx6k.json")

# Header Section
st.title("🌱 Fertilizer & Irrigation Monitoring System")

if lottie_plant:
    st_lottie(lottie_plant, height=200)
else:
    st.write("🌿 Animation not available. Please check the URL or network connection.")

# Sidebar Section
st.sidebar.header("📡 Live Sensor Data")

# Function to fetch sensor data
def get_sensor_data():
    try:
        response = requests.get(f"{BASE_URL}/get_sensor_data", timeout=5)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.sidebar.error(f"Failed to fetch sensor data: {e}")
        return None

# Function to fetch irrigation state
def get_irrigation_state():
    try:
        response = requests.get(f"{BASE_URL}/get_irrigation_state", timeout=5)
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.sidebar.error(f"Failed to fetch irrigation state: {e}")
        return None

# Function to toggle irrigation state
def toggle_irrigation(state):
    try:
        response = requests.post(f"{BASE_URL}/set_irrigation_state", json={"state": state}, timeout=5)
        return response.status_code == 200
    except Exception as e:
        st.sidebar.error(f"Failed to toggle irrigation state: {e}")
        return False

# Update Sidebar Data
def update_sidebar():
    sensor_data = get_sensor_data()
    irrigation_data = get_irrigation_state()

    sensor_placeholder = st.sidebar.empty()
    irrigation_placeholder = st.sidebar.empty()
    button_placeholder = st.sidebar.empty()

    sensor_text = (
        f"**🌡 Temperature:** {sensor_data['temperature']} °C  \n"
        f"**💧 Humidity:** {sensor_data['humidity']} %  \n"
        f"**🌿 Soil Moisture:** {sensor_data['soil_moisture']} %"
        if sensor_data else "📊 Sensor Data Unavailable"
    )
    sensor_placeholder.write(sensor_text)

    if irrigation_data:
        irrigation_state = irrigation_data.get("irrigation_state", False)
        status = "💦 ON ✅" if irrigation_state else "❌ OFF"
        irrigation_placeholder.write(f"**🚰 Irrigation System:** {status}")

        toggle_state = "OFF" if irrigation_state else "ON"
        if button_placeholder.button(f"Turn Irrigation {toggle_state}"):
            new_state = not irrigation_state
            if toggle_irrigation(new_state):
                st.sidebar.success(f"🚰 Irrigation system turned {toggle_state}")
                update_sidebar()
    else:
        irrigation_placeholder.write("🚰 Irrigation Status Unavailable")

# Form for Soil & Crop Information
st.header("🌾 Soil & Crop Information")
with st.form("soil_crop_form"):
    nitrogen = st.number_input("🧪 Nitrogen Level", min_value=0, max_value=100, value=10)
    potassium = st.number_input("🧪 Potassium Level", min_value=0, max_value=100, value=10)
    phosphorous = st.number_input("🧪 Phosphorous Level", min_value=0, max_value=100, value=10)
    
    soil_type = st.selectbox("🌱 Soil Type", ["Sandy", "Loamy", "Clayey", "Peaty", "Saline", "Chalky", "Silty"])
    crop_type = st.selectbox("🌾 Crop Type", ["Wheat", "Rice", "Maize", "Barley", "Sugarcane", "Cotton", "Vegetables"])
    
    submitted = st.form_submit_button("🚀 Predict Fertilizer")

# Handle Form Submission
if submitted:
    payload = {
        "nitrogen": nitrogen,
        "potassium": potassium,
        "phosphorous": phosphorous,
        "soilType": soil_type,
        "cropType": crop_type
    }

    try:
        response = requests.post(f"{BASE_URL}/process_data", json=payload, timeout=5)
        if response.status_code == 200:
            result = response.json()
            predicted_fertilizer = result.get("Predicted Fertilizer", "No fertilizer prediction available")
            st.success(f"Predicted Fertilizer: {predicted_fertilizer}")
        else:
            st.error("Error from backend")
    except Exception as e:
        st.error(f"Request failed: {e}")

# Continuous sidebar updates every 3 seconds
while True:
    update_sidebar()
    time.sleep(3)
