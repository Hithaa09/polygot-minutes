import streamlit as st
import requests
from io import BytesIO

# ----------------------------
# 🧠 App Configuration
# ----------------------------
st.set_page_config(
    page_title="Polyglot Minutes",
    page_icon="🧠",
    layout="centered"
)

# Header
st.title("🧠 Polyglot Minutes")
st.markdown("### Multilingual Meeting Summarizer")
st.caption("Developed by Srihitha, Kiran, and Akshaya 💡")

st.divider()

# ----------------------------
# 🎙️ File Upload Section
# ----------------------------
st.subheader("🎧 Upload Meeting Audio")
uploaded_file = st.file_uploader("Choose an audio file", type=["mp3", "wav", "m4a"])

col1, col2 = st.columns(2)
with col1:
    backend_url = st.text_input("🔗 Backend URL", "http://127.0.0.1:8000/notes")
with col2:
    st.info("Ensure FastAPI backend is running on port 8000 before you start.")

st.divider()

# ----------------------------
# 🚀 Process Uploaded Audio
# ----------------------------
if uploaded_file is not None:
    st.success(f"✅ File `{uploaded_file.name}` uploaded successfully!")

    if st.button("🧾 Generate Meeting Notes"):
        with st.spinner("Processing... please wait ⏳"):
            files = {"file": (uploaded_file.name, uploaded_file, "audio/wav")}
            response = requests.post(backend_url, files=files)

            if response.status_code == 200:
                result = response.json()
                st.success("✅ Meeting Notes Generated Successfully!")

                # Layout: 3 sections
                st.markdown("### 📝 Transcript")
                st.write(result.get("transcript", "No transcript found."))

                st.markdown("### 🧩 Summary")
                st.info(result.get("summary_detailed", "Summary unavailable."))

                st.markdown("### 📋 Action Items")
                for action in result.get("actions", []):
                    st.write(f"- **{action['item']}** ({action['priority']})")

                st.divider()
                st.download_button(
                    label="⬇️ Download Full JSON Output",
                    data=BytesIO(bytes(str(result), "utf-8")),
                    file_name="meeting_notes.json",
                    mime="application/json"
                )
            else:
                st.error("❌ Failed to get a response from the backend.")
else:
    st.warning("Please upload an audio file to start.")