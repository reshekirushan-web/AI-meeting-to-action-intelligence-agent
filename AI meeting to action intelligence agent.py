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
        "Add GEMINI_API_KEY to your Streamlit Secrets."
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
        Transform your meeting recordings into structured,
        actionable information using AI.
        """
    )

    st.write("---")

    st.subheader("What this system does")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("01", "Tasks")
        st.write("Identifies tasks assigned during the meeting.")

    with col2:
        st.metric("02", "Promises")
        st.write("Detects commitments and promises.")

    with col3:
        st.metric("03", "Deadlines")
        st.write("Extracts important deadlines and dates.")

    st.write("---")

    st.info(
        "Upload a meeting recording and let Gemini AI "
        "extract the important action items."
    )

    if st.button(
        "GET STARTED →",
        type="primary",
        use_container_width=True
    ):
        st.session_state.page = 2
        st.rerun()


# ============================================================
# PAGE 2 - AUDIO UPLOAD & ANALYSIS
# ============================================================

elif st.session_state.page == 2:

    st.title("🎧 LISTEN TO YOUR MEETINGS")

    st.subheader("Upload your audio and let AI do the heavy lifting")

    st.write("---")

    st.progress(0.66)

    st.caption("STEP 2 OF 3")

    st.write("")

    # --------------------------------------------------------
    # AUDIO UPLOADER
    # --------------------------------------------------------

    audio = st.file_uploader(
        "UPLOAD THE VOICE",
        type=["mp3", "wav", "m4a"],
        help="Upload an MP3, WAV, or M4A meeting recording."
    )

    if audio is not None:

        st.session_state.audio_name = audio.name

        st.success(f"Audio uploaded: {audio.name}")

        st.audio(audio)

        st.write("")

        # ----------------------------------------------------
        # AUDIO INFORMATION
        # ----------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "FILE NAME",
                audio.name
            )

        with col2:
            file_size_mb = len(audio.getbuffer()) / (1024 * 1024)

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

                # --------------------------------------------
                # SAVE STREAMLIT UPLOAD TO TEMP FILE
                # --------------------------------------------

                status.info("Preparing your audio...")

                progress.progress(20)

                file_extension = os.path.splitext(
                    audio.name
                )[1]

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

                # --------------------------------------------
                # UPLOAD AUDIO TO GEMINI
                # --------------------------------------------

                status.info(
                    "Uploading meeting audio to Gemini..."
                )

                progress.progress(40)

                audio_file = client.files.upload(
                    file=temp_audio_path
                )

                # --------------------------------------------
                # GEMINI PROMPT
                # --------------------------------------------

                status.info(
                    "AI is analyzing the meeting..."
                )

                progress.progress(60)

                prompt = """
You are an AI Meeting to Action Intelligence Agent.

Analyze the uploaded meeting audio carefully.

Extract the following information:

1. Tasks assigned to people
2. Promises or commitments made by people
3. Deadlines mentioned in the meeting
4. Important decisions made
5. A concise summary of the meeting

Return ONLY valid JSON.

Use exactly this structure:

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

Rules:

- Put assigned work under type "Task".
- Put promises and commitments under type "Promise".
- If a deadline is not mentioned, use "Not specified".
- If the speaker is unknown, use "Unknown".
- Do not invent information.
- Keep the summary concise.
- Return ONLY JSON.
"""

                # --------------------------------------------
                # GEMINI ANALYSIS
                # --------------------------------------------

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[
                        audio_file,
                        prompt
                    ]
                )

                progress.progress(80)

                # --------------------------------------------
                # CLEAN GEMINI RESPONSE
                # --------------------------------------------

                result_text = response.text.strip()

                if result_text.startswith("```json"):
                    result_text = result_text[
                        7:
                    ].strip()

                if result_text.endswith("```"):
                    result_text = result_text[
                        :-3
                    ].strip()

                meeting_data = json.loads(
                    result_text
                )

                # --------------------------------------------
                # SAVE RESULTS
                # --------------------------------------------

                st.session_state.meeting_data = meeting_data

                progress.progress(100)

                status.success(
                    "Meeting analysis completed!"
                )

                st.session_state.page = 3

                st.rerun()

            except json.JSONDecodeError:

                st.error(
                    "Gemini returned an invalid JSON response."
                )

                st.write(
                    "Raw response:"
                )

                st.code(
                    result_text
                    if "result_text" in locals()
                    else "No response"
                )

            except Exception as e:

                st.error(
                    "Something went wrong while analyzing the meeting."
                )

                st.exception(e)

            finally:

                if (
                    temp_audio_path
                    and os.path.exists(temp_audio_path)
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

    st.title("📋 GET TASKS, PROMISES & DEADLINES")

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
    # EXTRACT DATA
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

    tasks = [
        item
        for item in commitments
        if item.get("type", "").lower() == "task"
    ]

    promises = [
        item
        for item in commitments
        if item.get("type", "").lower() == "promise"
    ]

    deadlines = [
        item
        for item in commitments
        if item.get("deadline")
        and item.get("deadline").lower()
        != "not specified"
    ]

    # ========================================================
    # SUMMARY METRICS
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
    # MEETING SUMMARY
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

    st.subheader("🤝 PROMISES & COMMITMENTS")

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
                f"**{index}. {item.get('deadline', 'Not specified')}**"
            )

            st.write(
                f"Related action: {item.get('task', 'Not specified')}"
            )

            st.divider()

    else:

        st.info(
            "No deadlines were identified."
        )

    # ========================================================
    # IMPORTANT DECISIONS
    # ========================================================

    st.subheader("💡 IMPORTANT DECISIONS")

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

    st.subheader("📥 DOWNLOAD RESULTS")

    download_text = "AI MEETING TO ACTION INTELLIGENCE AGENT\n"
    download_text += "=" * 50
    download_text += "\n\n"

    download_text += "MEETING SUMMARY\n"
    download_text += "-" * 30
    download_text += "\n"
    download_text += summary
    download_text += "\n\n"

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

        download_text += "No tasks identified.\n\n"

    download_text += "PROMISES & COMMITMENTS\n"
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

    download_text += "IMPORTANT DECISIONS\n"
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