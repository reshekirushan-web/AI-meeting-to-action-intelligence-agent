import streamlit as st
import os
import json
import tempfile
from google import genai


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="The Tarnished Archive",
    page_icon="⚔️",
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
    st.error("⚠️ The Sacred Key is missing.")
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
# PAGE 1 — THE ARCHIVE
# ============================================================

if st.session_state.page == 1:

    st.title("⚔️ THE TARNISHED ARCHIVE")

    st.subheader(
        "AI MEETING TO ACTION INTELLIGENCE"
    )

    st.write(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    st.markdown(
        """
        ### 🕯️ Chronicle the words. Reveal the actions.

        Transform meeting recordings into structured intelligence.

        The Archive listens to the voices within your meeting and
        uncovers **tasks, promises, deadlines and decisions** hidden
        within the conversation.
        """
    )

    st.write("")

    # ========================================================
    # MAIN FEATURES
    # ========================================================

    st.subheader("𒀭 WHAT THE ARCHIVE SHALL REVEAL")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            label="⚔️ TASKS",
            value="01"
        )

        st.write(
            "Assignments spoken during the meeting."
        )

    with col2:

        st.metric(
            label="🤝 OATHS",
            value="02"
        )

        st.write(
            "Promises and commitments made by speakers."
        )

    with col3:

        st.metric(
            label="⌛ DEADLINES",
            value="03"
        )

        st.write(
            "Dates and time-bound obligations."
        )

    st.write("")

    # ========================================================
    # ARCHIVE DESCRIPTION
    # ========================================================

    with st.container():

        st.subheader("📜 THE PURPOSE")

        st.info(
            "Upload a meeting recording. "
            "The intelligence agent shall examine the conversation "
            "and forge it into actionable information."
        )

    st.write("")

    # ========================================================
    # JOURNEY
    # ========================================================

    st.subheader("🗺️ THE JOURNEY")

    journey1, journey2, journey3 = st.columns(3)

    with journey1:

        st.write("### I")
        st.write("🎙️ **OFFER THE RECORDING**")
        st.caption(
            "Provide the meeting voice to the Archive."
        )

    with journey2:

        st.write("### II")
        st.write("👁️ **THE ARCHIVE LISTENS**")
        st.caption(
            "Gemini examines the spoken conversation."
        )

    with journey3:

        st.write("### III")
        st.write("⚔️ **CLAIM THE INTELLIGENCE**")
        st.caption(
            "Tasks, promises and deadlines are revealed."
        )

    st.write("")

    if st.button(
        "⚔️ ENTER THE ARCHIVE",
        type="primary",
        use_container_width=True
    ):

        st.session_state.page = 2
        st.rerun()


# ============================================================
# PAGE 2 — AUDIO CHAMBER
# ============================================================

elif st.session_state.page == 2:

    st.title("🎙️ THE CHAMBER OF VOICES")

    st.subheader(
        "Offer your meeting recording to the Archive"
    )

    st.write(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    # ========================================================
    # JOURNEY PROGRESS
    # ========================================================

    st.progress(0.66)

    st.caption(
        "⚔️ JOURNEY — II / III"
    )

    st.write("")

    # ========================================================
    # AUDIO UPLOAD
    # ========================================================

    st.subheader("📜 PRESENT THE RECORDING")

    audio = st.file_uploader(
        "Choose a meeting recording",
        type=["mp3", "wav", "m4a"],
        help="Supported formats: MP3, WAV and M4A."
    )

    if audio is not None:

        st.session_state.audio_name = audio.name

        st.success(
            f"✓ The recording has been accepted: {audio.name}"
        )

        st.write("")

        # ====================================================
        # AUDIO PLAYER
        # ====================================================

        st.subheader("🔊 THE VOICE")

        st.audio(audio)

        st.write("")

        # ====================================================
        # RECORDING INFORMATION
        # ====================================================

        st.subheader("🛡️ RECORDING INSCRIPTION")

        file_size_mb = (
            len(audio.getbuffer()) /
            (1024 * 1024)
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "📜 FILE",
                audio.name
            )

        with col2:

            st.metric(
                "💾 SIZE",
                f"{file_size_mb:.2f} MB"
            )

        with col3:

            st.metric(
                "🎧 FORMAT",
                audio.name.split(".")[-1].upper()
            )

        st.write("")

        # ====================================================
        # ANALYSIS SECTION
        # ====================================================

        with st.expander(
            "🕯️ What will the Archive seek?",
            expanded=True
        ):

            st.write(
                "The intelligence agent will search the recording for:"
            )

            st.write("⚔️ Tasks assigned to people")
            st.write("🤝 Promises and commitments")
            st.write("⌛ Deadlines")
            st.write("💡 Important decisions")
            st.write("📜 A concise meeting summary")

        st.write("")

        # ====================================================
        # ANALYZE BUTTON
        # ====================================================

        if st.button(
            "⚔️ BEGIN THE ANALYSIS",
            type="primary",
            use_container_width=True
        ):

            progress = st.progress(0)

            status = st.empty()

            temp_audio_path = None

            try:

                # ==================================================
                # STEP 1 — SAVE AUDIO
                # ==================================================

                status.info(
                    "🕯️ Preparing the recording..."
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
                # MIME TYPE
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
                # STEP 2 — UPLOAD
                # ==================================================

                status.info(
                    "📜 Sending the recording into the Archive..."
                )

                progress.progress(30)

                uploaded_file = client.files.upload(
                    file=temp_audio_path
                )

                # ==================================================
                # STEP 3 — ANALYZE
                # ==================================================

                status.info(
                    "👁️ The intelligence agent is listening..."
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
                # GEMINI INTERACTION
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
                    "⚔️ Forging the final intelligence..."
                )

                # ==================================================
                # GET RESPONSE
                # ==================================================

                result_text = (
                    interaction.output_text.strip()
                )

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
                # JSON
                # ==================================================

                meeting_data = json.loads(
                    result_text
                )

                # ==================================================
                # VALIDATION
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
                # SAVE
                # ==================================================

                st.session_state.meeting_data = (
                    meeting_data
                )

                progress.progress(100)

                status.success(
                    "⚔️ The Archive has revealed its findings."
                )

                st.session_state.page = 3

                st.rerun()

            # ======================================================
            # JSON ERROR
            # ======================================================

            except json.JSONDecodeError:

                st.error(
                    "⚠️ The returned intelligence could not "
                    "be interpreted."
                )

                st.write(
                    "Raw intelligence:"
                )

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
                    "⚠️ The Archive encountered an error."
                )

                st.info(
                    "Check your Gemini API key, audio file "
                    "and Gemini API access."
                )

                st.exception(e)

            # ======================================================
            # CLEAN TEMP FILE
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
            "🕯️ No recording has been offered yet."
        )

    st.write("")

    if st.button(
        "← RETURN TO THE ARCHIVE"
    ):

        st.session_state.page = 1
        st.rerun()


# ============================================================
# PAGE 3 — THE REVELATION
# ============================================================

elif st.session_state.page == 3:

    st.title("⚔️ THE REVELATION")

    st.subheader(
        "The conversation has been forged into intelligence"
    )

    st.write(
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

    st.progress(1.0)

    st.caption(
        "⚔️ JOURNEY COMPLETE — III / III"
    )

    meeting_data = st.session_state.meeting_data

    if meeting_data is None:

        st.warning(
            "🕯️ No intelligence has been discovered."
        )

        if st.button(
            "← RETURN TO THE CHAMBER"
        ):

            st.session_state.page = 2
            st.rerun()

        st.stop()

    # ========================================================
    # DATA
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
    # SEPARATE TASKS / PROMISES
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

            if (
                str(deadline).lower()
                != "not specified"
            ):

                deadlines.append(item)

    # ========================================================
    # OVERVIEW
    # ========================================================

    st.subheader(
        "🛡️ THE BATTLEFIELD OVERVIEW"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "⚔️ TASKS",
            len(tasks)
        )

    with col2:

        st.metric(
            "🤝 OATHS",
            len(promises)
        )

    with col3:

        st.metric(
            "⌛ DEADLINES",
            len(deadlines)
        )

    with col4:

        st.metric(
            "💡 DECISIONS",
            len(decisions)
        )

    st.write("")

    # ========================================================
    # SUMMARY
    # ========================================================

    with st.container():

        st.subheader(
            "📜 CHRONICLE OF THE MEETING"
        )

        st.info(summary)

    st.write("")

    # ========================================================
    # TASKS
    # ========================================================

    st.subheader(
        "⚔️ QUESTS — TASKS"
    )

    if tasks:

        for index, task in enumerate(
            tasks,
            start=1
        ):

            with st.container():

                st.write(
                    f"### ⚔️ Quest {index}"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.caption(
                        "👤 CHAMPION"
                    )

                    st.write(
                        task.get(
                            "speaker",
                            "Unknown"
                        )
                    )

                with col2:

                    st.caption(
                        "⌛ TIMEBOUND"
                    )

                    st.write(
                        task.get(
                            "deadline",
                            "Not specified"
                        )
                    )

                st.write(
                    "📜 **Objective**"
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
            "🕯️ No quests were discovered."
        )

    # ========================================================
    # PROMISES
    # ========================================================

    st.subheader(
        "🤝 OATHS — PROMISES & COMMITMENTS"
    )

    if promises:

        for index, promise in enumerate(
            promises,
            start=1
        ):

            with st.container():

                st.write(
                    f"### 🤝 Oath {index}"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.caption(
                        "👤 SWORN BY"
                    )

                    st.write(
                        promise.get(
                            "speaker",
                            "Unknown"
                        )
                    )

                with col2:

                    st.caption(
                        "⌛ DEADLINE"
                    )

                    st.write(
                        promise.get(
                            "deadline",
                            "Not specified"
                        )
                    )

                st.write(
                    "📜 **Oath**"
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
            "🕯️ No oaths were discovered."
        )

    # ========================================================
    # DEADLINES
    # ========================================================

    st.subheader(
        "⌛ THE HOUR OF FATE — DEADLINES"
    )

    if deadlines:

        for index, item in enumerate(
            deadlines,
            start=1
        ):

            with st.container():

                st.write(
                    f"### ⌛ Deadline {index}"
                )

                st.write(
                    f"**{item.get('deadline', 'Not specified')}**"
                )

                st.caption(
                    "Related action"
                )

                st.write(
                    item.get(
                        "task",
                        "Not specified"
                    )
                )

                st.divider()

    else:

        st.info(
            "🕯️ No deadlines were discovered."
        )

    # ========================================================
    # DECISIONS
    # ========================================================

    st.subheader(
        "💡 THE COUNCIL'S DECISIONS"
    )

    if decisions:

        for index, decision in enumerate(
            decisions,
            start=1
        ):

            with st.container():

                st.write(
                    f"### 💡 Decision {index}"
                )

                st.write(decision)

                st.divider()

    else:

        st.info(
            "🕯️ No major decisions were discovered."
        )

    # ========================================================
    # DOWNLOAD
    # ========================================================

    st.subheader(
        "📥 CLAIM THE CHRONICLE"
    )

    download_text = ""

    download_text += (
        "THE TARNISHED ARCHIVE\n"
    )

    download_text += (
        "AI MEETING TO ACTION INTELLIGENCE\n"
    )

    download_text += "=" * 55
    download_text += "\n\n"

    download_text += (
        "CHRONICLE OF THE MEETING\n"
    )

    download_text += "-" * 35
    download_text += "\n"

    download_text += summary
    download_text += "\n\n"

    # --------------------------------------------------------
    # TASKS
    # --------------------------------------------------------

    download_text += (
        "QUESTS — TASKS\n"
    )

    download_text += "-" * 35
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
                f"   Champion: "
                f"{task.get('speaker', 'Unknown')}\n"
            )

            download_text += (
                f"   Deadline: "
                f"{task.get('deadline', 'Not specified')}\n\n"
            )

    else:

        download_text += (
            "No quests discovered.\n\n"
        )

    # --------------------------------------------------------
    # PROMISES
    # --------------------------------------------------------

    download_text += (
        "OATHS — PROMISES & COMMITMENTS\n"
    )

    download_text += "-" * 35
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
                f"   Sworn by: "
                f"{promise.get('speaker', 'Unknown')}\n"
            )

            download_text += (
                f"   Deadline: "
                f"{promise.get('deadline', 'Not specified')}\n\n"
            )

    else:

        download_text += (
            "No oaths discovered.\n\n"
        )

    # --------------------------------------------------------
    # DECISIONS
    # --------------------------------------------------------

    download_text += (
        "THE COUNCIL'S DECISIONS\n"
    )

    download_text += "-" * 35
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
            "No decisions discovered.\n"
        )

    st.download_button(
        label="📜 DOWNLOAD THE CHRONICLE",
        data=download_text,
        file_name="tarnished_meeting_chronicle.txt",
        mime="text/plain",
        use_container_width=True
    )

    st.write("")

    # ========================================================
    # NEW MEETING
    # ========================================================

    if st.button(
        "⚔️ BEGIN ANOTHER CHRONICLE",
        type="primary",
        use_container_width=True
    ):

        st.session_state.page = 2
        st.session_state.meeting_data = None
        st.session_state.audio_name = None

        st.rerun()