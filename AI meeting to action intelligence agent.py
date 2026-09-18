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
           import tempfile
import os

# Save Streamlit uploaded file temporarily
suffix = os.path.splitext(audio.name)[1]

with tempfile.NamedTemporaryFile(
    delete=False,
    suffix=suffix
) as temp_audio:

    temp_audio.write(audio.getbuffer())
    temp_audio_path = temp_audio.name

 try:

            # Upload the actual file path to Gemini
            audio_file = client.files.upload(
                file=temp_audio_path
            )

            prompt = """
You are an AI meeting assistant.

Analyze this meeting recording.

Identify:

1. Speakers
2. Tasks assigned
3. Promises or commitments
4. Deadlines
5. Important decisions

Return ONLY valid JSON:

{
    "commitments": [
        {
            "speaker": "Speaker 1",
            "task": "Complete database module",
            "deadline": "Friday",
            "type": "Task"
        }
    ],
    "summary": "Short summary of the meeting"
}

Rules:
- Do not invent information.
- If no deadline is mentioned, use null.
- If the speaker cannot be identified, use Speaker 1, Speaker 2, etc.
- Include both tasks and promises.
"""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    audio_file,
                    prompt
                ]
            )

            result_text = response.text

        finally:

            # Delete temporary local file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)