import streamlit as st
import os
import json
import tempfile
from google import genai


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Meeting to Action",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# GEMINI API CONFIGURATION
# ============================================================

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

if not api_key:
    st.error("GEMINI_API_KEY is not configured.")
    st.info(
        "Please add GEMINI_API_KEY to your Streamlit Secrets."
    )
    st.stop()


client = genai.Client(api_key=api_key)


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = 1

if "meeting_data" not in st.session_state:
    st.session_state.meeting_data = None

if "audio_name" not in st.session_state:
    st.session_state.audio_name = None


# ============================================================
# PAGE 1 - INTRODUCTION
# ============================================================

if st.session_state.page == 1:

    st.title("🎙️ AI MEETING TO ACTION")
    st.title("INTELLIGENCE AGENT")

    st.subheader("Turn conversations into real actions")

    st.write(
        """
        Transform meeting recordings into structured,
        actionable information using Gemini AI.
        """
    )

    st.write("---")

    st.subheader("What this system does")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("01", "TASKS")
        st.write(
            "Identifies tasks assigned during the meeting."
        )

    with col2:
        st.metric("02", "PROMISES")
        st.write(
            "Detects promises and commitments."
        )

    with col3:
        st.metric("03", "DEADLINES")
        st.write(
            "Extracts deadlines and important dates."
        )

    st.write("---")

    st.info(
        "Upload a meeting recording and let AI convert "
        "the conversation into actionable information."
    )

    if st.button(
        "GET STARTED →",
        type="primary",
        use_container_width=True
    ):
        st.session_state.page = 2
        st.rerun()


# ============================================================
# PAGE 2 - AUDIO UPLOAD
# ============================================================

elif st.session_state.page == 2:

    st.title("🎧 LISTEN TO YOUR MEETINGS")

    st.subheader(
        "Upload your audio and let AI do the heavy lifting"
    )

    st.write("---")

    st.progress(0.66)

    st.caption("STEP 2 OF 3")

    st.write("")

    # --------------------------------------------------------
    # AUDIO UPLOAD
    # --------------------------------------------------------

    audio = st.file_uploader(
        "UPLOAD THE VOICE",
        type=["mp3", "wav", "m4a"],
        help="Upload an MP3, WAV, or M4A meeting recording."
    )

    if audio is not None:

        st.session_state.audio_name = audio.name

        st.success(
            f"Audio uploaded successfully: {audio.name}"
        )

        st.audio(audio)

        st.write("---")

        # ----------------------------------------------------
        # FILE INFORMATION
        # ----------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "FILE NAME",
                audio.name
            )

        with col2:
            file_size_mb = len(
                audio.getbuffer()
            ) / (1024 * 1024)

            st.metric(
                "FILE SIZE",
                f"{file_size_mb:.2f} MB"
            )

        st.write("---")

        # ----------------------------------------------------
        # ANALYZE BUTTON
        # ----------------------------------------------------

        if st.button(
            "✨ ANALYZE MEETING",
            type="primary",
            use_container_width=True
        ):

            progress = st.progress(0)

            status = st.empty()

            temp_audio_path = None

            try:

                # ==================================================
                # STEP 1 - SAVE AUDIO FILE
                # ==================================================

                status.info(
                    "Preparing your audio..."
                )

                progress.progress(15)

                file_extension = os.path.splitext(
                    audio.name
                )[1].lower()

                if not file_extension:
                    file_extension = ".mp3"

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=file_extension
                ) as temp_audio:

                    temp_audio.write(
                        audio.getbuffer()
                    )

                    temp_audio_path = temp_audio.name

                # ==================================================
                # DETERMINE MIME TYPE
                # ==================================================

                mime_types = {
                    ".mp3": "audio/mpeg",
                    ".wav": "audio/wav",
                    ".m4a": "audio/mp4"
                }

                mime_type = mime_types.get(
                    file_extension,
                    "audio/mpeg"
                )

                # ==================================================
                # STEP 2 - UPLOAD AUDIO TO GEMINI
                # ==================================================

                status.info(
                    "Uploading meeting audio to Gemini..."
                )

                progress.progress(30)

                uploaded_file = client.files.upload(
                    file=temp_audio_path
                )

                # ==================================================
                # STEP 3 - ANALYZE AUDIO
                # ==================================================

                status.info(
                    "Gemini is listening to your meeting..."
                )

                progress.progress(45)

                prompt = """
You are an AI Meeting to Action Intelligence Agent.

Carefully analyze the uploaded meeting audio.

Your job is to identify actionable information from
the conversation.

Extract:

1. Tasks assigned to people
2. Promises and commitments made by people
3. Deadlines mentioned
4. Important decisions
5. A concise meeting summary

IMPORTANT:

- Do NOT invent information.
- Only include information actually present in the audio.
- If the speaker is unknown, use "Unknown".
- If a deadline is not mentioned, use "Not specified".
- Keep the summary concise.
- Distinguish tasks from promises.
- Return ONLY valid JSON.
- Do not include Markdown.
- Do not use ```json.
- Do not include any explanation outside the JSON.

Use exactly this JSON structure:

{
  "summary": "Short summary of the meeting",

  "commitments": [
    {
      "speaker": "Speaker 1",
      "task": "Complete the database module",
      "deadline": "Friday",
      "type": "Task"
    },
    {
      "speaker": "Speaker 2",
      "task": "Send the presentation",
      "deadline": "Tomorrow",
      "type": "Promise"
    }
  ],

  "decisions": [
    "Decision made during the meeting"
  ]
}

If there are no tasks or promises, return an empty commitments array.

If there are no important decisions, return an empty decisions array.
"""

                # ==================================================
                # INTERACTIONS API
                # ==================================================

                interaction = client.interactions.create(
                    model="gemini-3.6-flash",
                    input=[
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "audio",
                            "uri": uploaded_file.uri,
                            "mime_type": uploaded_file.mime_type
                        }
                    ]
                )

                progress.progress(75)

                status.info(
                    "Processing AI results..."
                )

                # ==================================================
                # GET GEMINI RESPONSE
                # ==================================================

                result_text = interaction.output_text.strip()

                # ==================================================
                # CLEAN RESPONSE
                # ==================================================

                if result_text.startswith("```json"):

                    result_text = result_text[
                        7:
                    ].strip()

                elif result_text.startswith("```"):

                    result_text = result_text[
                        3:
                    ].strip()

                if result_text.endswith("```"):

                    result_text = result_text[
                        :-3
                    ].strip()

                # ==================================================
                # CONVERT JSON
                # ==================================================

                meeting_data = json.loads(
                    result_text
                )

                # ==================================================
                # VALIDATE DATA
                # ==================================================

                if "summary" not in meeting_data:
                    meeting_data["summary"] = (
                        "No summary available."
                    )

                if "commitments" not in meeting_data:
                    meeting_data["commitments"] = []

                if "decisions" not in meeting_data:
                    meeting_data["decisions"] = []

                # ==================================================
                # SAVE RESULTS
                # ==================================================

                st.session_state.meeting_data = meeting_data

                progress.progress(100)

                status.success(
                    "Meeting analysis completed successfully!"
                )

                # ==================================================
                # GO TO RESULTS PAGE
                # ==================================================

                st.session_state.page = 3

                st.rerun()

            # ======================================================
            # JSON ERROR
            # ======================================================

            except json.JSONDecodeError:

                st.error(
                    "Gemini returned a response that was "
                    "not valid JSON."
                )

                st.write("Gemini response:")

                st.code(
                    result_text
                    if "result_text" in locals()
                    else "No response received."
                )

            # ======================================================
            # GENERAL ERROR
            # ======================================================

            except Exception as e:

                st.error(
                    "An error occurred while analyzing the audio."
                )

                st.write(
                    "Please check your Gemini API key, "
                    "audio file and Gemini API access."
                )

                st.exception(e)

            # ======================================================
            # DELETE TEMP FILE
            # ======================================================

            finally:

                if (
                    temp_audio_path
                    and os.path.exists(
                        temp_audio_path
                    )
                ):

                    os.remove(
                        temp_audio_path
                    )

    else:

        st.warning(
            "Please upload a meeting audio file to continue."
        )

    st.write("---")

    # --------------------------------------------------------
    # BACK BUTTON
    # --------------------------------------------------------

    if st.button("← BACK"):

        st.session_state.page = 1

        st.rerun()


# ============================================================
# PAGE 3 - RESULTS
# ============================================================

elif st.session_state.page == 3:

    st.title(
        "📋 GET TASKS, PROMISES & DEADLINES"
    )

    st.subheader(
        "Your meeting has been converted into actionable information."
    )

    st.write("---")

    st.progress(1.0)

    st.caption("STEP 3 OF 3")

    meeting_data = st.session_state.meeting_data

    if meeting_data is None:

        st.warning(
            "No meeting analysis is available."
        )

        if st.button("← GO BACK"):

            st.session_state.page = 2

            st.rerun()

        st.stop()

    # ========================================================
    # GET DATA
    # ========================================================

    summary = meeting_data.get(
        "summary",
        "No summary available."
    )

    commitments = meeting_data.get(
        "commitments",
        []
    )

    decisions = meeting_data.get(
        "decisions",
        []
    )

    # ========================================================
    # SEPARATE TASKS AND PROMISES
    # ========================================================

    tasks = []

    promises = []

    for item in commitments:

        item_type = str(
            item.get("type", "")
        ).lower()

        if item_type == "task":

            tasks.append(item)

        elif item_type == "promise":

            promises.append(item)

    # ========================================================
    # DEADLINES
    # ========================================================

    deadlines = []

    for item in commitments:

        deadline = item.get(
            "deadline",
            "Not specified"
        )

        if deadline:

            if str(deadline).lower() != "not specified":

                deadlines.append(item)

    # ========================================================
    # OVERVIEW
    # ========================================================

    st.subheader("📊 MEETING OVERVIEW")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "TASKS",
            len(tasks)
        )

    with col2:

        st.metric(
            "PROMISES",
            len(promises)
        )

    with col3:

        st.metric(
            "DEADLINES",
            len(deadlines)
        )

    st.write("---")

    # ========================================================
    # SUMMARY
    # ========================================================

    st.subheader("📝 MEETING SUMMARY")

    st.info(summary)

    st.write("---")

    # ========================================================
    # TASKS
    # ========================================================

    st.subheader("✅ TASKS")

    if tasks:

        for index, task in enumerate(
            tasks,
            start=1
        ):

            with st.container():

                st.write(
                    f"### Task {index}"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        "**Assigned to:**"
                    )

                    st.write(
                        task.get(
                            "speaker",
                            "Unknown"
                        )
                    )

                with col2:

                    st.write(
                        "**Deadline:**"
                    )

                    st.write(
                        task.get(
                            "deadline",
                            "Not specified"
                        )
                    )

                st.write(
                    "**Task:**"
                )

                st.write(
                    task.get(
                        "task",
                        "No task description"
                    )
                )

                st.divider()

    else:

        st.info(
            "No tasks were identified."
        )

    # ========================================================
    # PROMISES
    # ========================================================

    st.subheader(
        "🤝 PROMISES & COMMITMENTS"
    )

    if promises:

        for index, promise in enumerate(
            promises,
            start=1
        ):

            with st.container():

                st.write(
                    f"### Promise {index}"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.write(
                        "**Person:**"
                    )

                    st.write(
                        promise.get(
                            "speaker",
                            "Unknown"
                        )
                    )

                with col2:

                    st.write(
                        "**Deadline:**"
                    )

                    st.write(
                        promise.get(
                            "deadline",
                            "Not specified"
                        )
                    )

                st.write(
                    "**Commitment:**"
                )

                st.write(
                    promise.get(
                        "task",
                        "No commitment description"
                    )
                )

                st.divider()

    else:

        st.info(
            "No promises or commitments were identified."
        )

    # ========================================================
    # DEADLINES
    # ========================================================

    st.subheader("⏰ DEADLINES")

    if deadlines:

        for index, item in enumerate(
            deadlines,
            start=1
        ):

            st.write(
                f"### {index}. "
                f"{item.get('deadline', 'Not specified')}"
            )

            st.write(
                f"Related action: "
                f"{item.get('task', 'Not specified')}"
            )

            st.divider()

    else:

        st.info(
            "No deadlines were identified."
        )

    # ========================================================
    # DECISIONS
    # ========================================================

    st.subheader(
        "💡 IMPORTANT DECISIONS"
    )

    if decisions:

        for index, decision in enumerate(
            decisions,
            start=1
        ):

            st.write(
                f"**{index}.** {decision}"
            )

    else:

        st.info(
            "No important decisions were identified."
        )

    st.write("---")

    # ========================================================
    # DOWNLOAD REPORT
    # ========================================================

    st.subheader(
        "📥 DOWNLOAD RESULTS"
    )

    download_text = ""

    download_text += (
        "AI MEETING TO ACTION "
        "INTELLIGENCE AGENT\n"
    )

    download_text += "=" * 50
    download_text += "\n\n"

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    download_text += "MEETING SUMMARY\n"
    download_text += "-" * 30
    download_text += "\n"
    download_text += summary
    download_text += "\n\n"

    # --------------------------------------------------------
    # TASKS
    # --------------------------------------------------------

    download_text += "TASKS\n"
    download_text += "-" * 30
    download_text += "\n"

    if tasks:

        for index, task in enumerate(
            tasks,
            start=1
        ):

            download_text += (
                f"{index}. "
                f"{task.get('task', 'N/A')}\n"
            )

            download_text += (
                f"   Person: "
                f"{task.get('speaker', 'Unknown')}\n"
            )

            download_text += (
                f"   Deadline: "
                f"{task.get('deadline', 'Not specified')}\n\n"
            )

    else:

        download_text += (
            "No tasks identified.\n\n"
        )

    # --------------------------------------------------------
    # PROMISES
    # --------------------------------------------------------

    download_text += (
        "PROMISES & COMMITMENTS\n"
    )

    download_text += "-" * 30
    download_text += "\n"

    if promises:

        for index, promise in enumerate(
            promises,
            start=1
        ):

            download_text += (
                f"{index}. "
                f"{promise.get('task', 'N/A')}\n"
            )

            download_text += (
                f"   Person: "
                f"{promise.get('speaker', 'Unknown')}\n"
            )

            download_text += (
                f"   Deadline: "
                f"{promise.get('deadline', 'Not specified')}\n\n"
            )

    else:

        download_text += (
            "No promises identified.\n\n"
        )

    # --------------------------------------------------------
    # DECISIONS
    # --------------------------------------------------------

    download_text += (
        "IMPORTANT DECISIONS\n"
    )

    download_text += "-" * 30
    download_text += "\n"

    if decisions:

        for index, decision in enumerate(
            decisions,
            start=1
        ):

            download_text += (
                f"{index}. {decision}\n"
            )

    else:

        download_text += (
            "No important decisions identified.\n"
        )

    # --------------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------------

    st.download_button(
        label="⬇️ DOWNLOAD TASKS & PROMISES",
        data=download_text,
        file_name="meeting_tasks_and_promises.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.write("---")

    # ========================================================
    # ANALYZE ANOTHER MEETING
    # ========================================================

    if st.button(
        "🎙️ ANALYZE ANOTHER MEETING",
        type="primary",
        use_container_width=True
    ):

        st.session_state.page = 2
        st.session_state.meeting_data = None
        st.session_state.audio_name = None

        st.rerun()