import streamlit as st
from google import genai
import os

st.set_page_config(page_title="Meeting AI")

st.title("🎤 Meeting AI")
st.write("Detect tasks, promises and deadlines from meetings")

# Gemini API
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

audio = st.file_uploader(
    "Upload meeting recording",
    type=["mp3", "wav", "m4a"]
)

if audio:

    st.audio(audio)

    if st.button("Analyze Meeting"):

        with st.spinner("Analyzing meeting..."):

            # Upload audio to Gemini
            audio_file = client.files.upload(
                file=audio
            )

            prompt = """
You are an AI meeting assistant.

Analyze this meeting recording.

Identify:
1. Who is speaking
2. Tasks assigned
3. Promises or commitments
4. Deadlines
5. Important decisions

Return the result as JSON:

{
  "commitments": [
    {
      "speaker": "Speaker 1",
      "task": "Complete database module",
      "deadline": "Friday",
      "type": "promise"
    }
  ]
}

Do NOT invent information.
If there is no deadline, use null.
"""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    audio_file,
                    prompt
                ]
            )

        st.subheader("📋 Meeting Results")

        st.write(response.text)