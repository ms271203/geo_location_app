
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import geocoder
from datetime import datetime

st.set_page_config(page_title="Pro GeoTag Camera", layout="wide")

# ---------- Custom CSS ----------
st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}
.stButton>button {
    background-color: #0066cc;
    color: white;
    border-radius: 10px;
    height: 3em;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

st.title("📸 Pro GeoTag Camera App")
st.markdown("### Capture • Add GPS • Add Logo • Download")

col1, col2 = st.columns(2)

with col1:
    camera_photo = st.camera_input("📷 Capture Image")
    uploaded_logo = st.file_uploader("🖼 Upload Transparent Logo (PNG)", type=["png"])
    logo_size = st.slider("🔍 Logo Size", 50, 300, 150)
    position = st.selectbox("📌 Logo Position", 
                            ["Top-Right", "Top-Left", "Bottom-Right", "Bottom-Left"])

if camera_photo:
    image = Image.open(camera_photo).convert("RGB")
    image = np.array(image)

    # Get Location
    g = geocoder.ip('me')
    lat, lon = g.latlng if g.latlng else ("N/A", "N/A")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Add Text
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, f"Lat: {lat}, Lon: {lon}",
                (20, image.shape[0] - 40),
                font, 0.7, (0, 0, 255), 2)
    cv2.putText(image, f"Date: {now}",
                (20, image.shape[0] - 10),
                font, 0.7, (0, 0, 255), 2)

    # Add Logo
    if uploaded_logo:
        logo = Image.open(uploaded_logo).convert("RGBA")
        logo = np.array(logo)

        scale = logo_size / logo.shape[1]
        logo_height = int(logo.shape[0] * scale)
        logo = cv2.resize(logo, (logo_size, logo_height))

        b, g, r, a = cv2.split(logo)
        overlay = cv2.merge((b, g, r))
        mask = cv2.merge((a, a, a))

        h, w, _ = image.shape

        if position == "Top-Right":
            x, y = w - logo_size - 10, 10
        elif position == "Top-Left":
            x, y = 10, 10
        elif position == "Bottom-Right":
            x, y = w - logo_size - 10, h - logo_height - 10
        else:
            x, y = 10, h - logo_height - 10

        roi = image[y:y+logo_height, x:x+logo_size]
        roi = np.where(mask == 0, roi, overlay)
        image[y:y+logo_height, x:x+logo_size] = roi

    with col2:
        st.image(image, caption="✨ Processed Image", use_container_width=True)

        final_img = Image.fromarray(image)
        st.download_button(
            "⬇ Download Final Image",
            data=final_img.tobytes(),
            file_name="pro_geotag_image.png",
            mime="image/png"
        )

    # Map Preview
    if lat != "N/A":
        st.markdown("### 🌍 Location Preview")
        st.map({"lat": [lat], "lon": [lon]})
