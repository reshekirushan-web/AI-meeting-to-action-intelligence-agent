
import streamlit as st
from google import genai
import os
import json
import tempfile


# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="Meeting AI",
    page_icon="🎤",
    layout="wide"
)

st.title("🎤 Meeting AI")
st.write("Detect tasks, promises and deadlines from meetings")


# --------------------------------------------------
# GEMINI API
# --------------------------------------------------

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"]
)


# --------------------------------------------------
# AUDIO UPLOAD
# --------------------------------------------------

audio = st.file_uploader(
    "Upload meeting recording",
    type=["mp3", "wav", "m4a"]
)


# --------------------------------------------------
# ANALYZE MEETING
# --------------------------------------------------

if audio:

    st.audio(audio)

    if st.button("🔍 Analyze Meeting"):

        with st.spinner("Analyzing meeting..."):

            # Create temporary file
            suffix = os.path.splitext(audio.name)[1]

            temp_audio_path = None

            try:

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix
                ) as temp_audio:

                    temp_audio.write(audio.getbuffer())
                    temp_audio_path = temp_audio.name

                # Upload audio file to Gemini
                audio_file = client.files.upload(
                    file=temp_audio_path
                )

                # Gemini prompt
                prompt = """
You are an AI meeting assistant.

Analyze this meeting recording carefully.

Identify:

1. Speakers
2. Tasks assigned
3. Promises or commitments
4. Deadlines
5. Important decisions

Return ONLY valid JSON in this exact format:

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
- If there is no deadline, use null.
- If the speaker cannot be identified, use Speaker 1,
  Speaker 2, etc.
- Include both tasks and promises.
- Keep the task description clear and concise.
"""

                # Send audio to Gemini
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        audio_file,
                        prompt
                    ]
                )

                result_text = response.text

                # Remove markdown formatting if Gemini adds it
                result_text = result_text.replace(
                    "```json",
                    ""
                ).replace(
                    "```",
                    ""
                ).strip()

                # Convert Gemini response to JSON
                meeting_data = json.loads(result_text)

                # Save results in session
                st.session_state["meeting_data"] = meeting_data

                st.success("✅ Meeting analyzed successfully!")

            except json.JSONDecodeError:

                st.error(
                    "Gemini returned an invalid response. "
                    "Please try again."
                )

            except Exception as e:

                st.error(
                    f"An error occurred: {str(e)}"
                )

            finally:

                # Delete temporary file
                if (
                    temp_audio_path
                    and os.path.exists(temp_audio_path)
                ):

                    os.remove(temp_audio_path)


# --------------------------------------------------
# DISPLAY RESULTS
# --------------------------------------------------

if "meeting_data" in st.session_state:

    meeting_data = st.session_state["meeting_data"]

    commitments = meeting_data.get(
        "commitments",
        []
    )

    summary = meeting_data.get(
        "summary",
        "No summary available."
    )


    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    st.subheader("📝 Meeting Summary")

    st.write(summary)


    # --------------------------------------------------
    # TASKS & PROMISES
    # --------------------------------------------------

    st.subheader("✅ Tasks & Promises")

    if commitments:

        for index, item in enumerate(
            commitments,
            start=1
        ):

            speaker = item.get(
                "speaker",
                "Unknown"
            )

            task = item.get(
                "task",
                "Not specified"
            )

            deadline = item.get(
                "deadline"
            )

            if deadline is None:
                deadline = "No deadline"

            commitment_type = item.get(
                "type",
                "Task"
            )

            st.markdown(
                f"""
### {index}. {commitment_type}

👤 **Person:** {speaker}

📌 **Task / Promise:** {task}

📅 **Deadline:** {deadline}

---
"""
            )

    else:

        st.info(
            "No tasks or promises were detected."
        )


    # --------------------------------------------------
    # CREATE TXT FILE
    # --------------------------------------------------

    download_text = ""

    download_text += (
        "MEETING TASKS & PROMISES\n"
    )

    download_text += (
        "=" * 45 + "\n\n"
    )


    # Summary
    download_text += (
        "MEETING SUMMARY\n"
    )

    download_text += (
        "-" * 45 + "\n"
    )

    download_text += (
        summary + "\n\n"
    )


    # Commitments
    download_text += (
        "TASKS & PROMISES\n"
    )

    download_text += (
        "-" * 45 + "\n\n"
    )


    if commitments:

        for index, item in enumerate(
            commitments,
            start=1
        ):

            speaker = item.get(
                "speaker",
                "Unknown"
            )

            task = item.get(
                "task",
                "Not specified"
            )

            deadline = item.get(
                "deadline"
            )

            if deadline is None:
                deadline = "No deadline"

            commitment_type = item.get(
                "type",
                "Task"
            )

            download_text += (
                f"{index}. {commitment_type}\n"
            )

            download_text += (
                f"Person: {speaker}\n"
            )

            download_text += (
                f"Task / Promise: {task}\n"
            )

            download_text += (
                f"Deadline: {deadline}\n\n"
            )

    else:

        download_text += (
            "No tasks or promises were detected.\n"
        )


    # --------------------------------------------------
    # DOWNLOAD BUTTON
    # --------------------------------------------------

    st.subheader("📥 Download Results")

    st.download_button(
        label="⬇️ Download Tasks & Promises",
        data=download_text,
        file_name="meeting_tasks_and_promises.txt",
        mime="text/plain"
    )
