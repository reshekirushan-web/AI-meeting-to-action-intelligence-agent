
import streamlit as st
import os
import json
import tempfile
from google import genai


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Neon Meeting AI",
    page_icon="💠",
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
# PAGE 1 — HOME
# ============================================================

if st.session_state.page == 1:

    st.title("💠 NEON MEETING AI")

    st.subheader(
        "AI MEETING TO ACTION INTELLIGENCE"
    )

    st.caption(
        "Turn conversations into structured actions."
    )

    st.write("")

    # ========================================================
    # HERO PANEL
    # ========================================================

    with st.container(border=True):

        st.subheader(
            "⚡ CONVERSATION → INTELLIGENCE"
        )

        st.write(
            """
            Transform meeting recordings into actionable
            intelligence using Gemini AI.
            """
        )

        st.info(
            "Upload a meeting recording and let AI discover "
            "tasks, promises, deadlines and decisions."
        )

    st.write("")

    # ========================================================
    # FEATURES
    # ========================================================

    st.subheader("🔷 CORE INTELLIGENCE")

    col1, col2, col3 = st.columns(3)

    with col1:

        with st.container(border=True):

            st.metric(
                "⚡ TASKS",
                "01"
            )

            st.write(
                "Identifies tasks assigned during the meeting."
            )

    with col2:

        with st.container(border=True):

            st.metric(
                "🔗 PROMISES",
                "02"
            )

            st.write(
                "Detects promises and commitments."
            )

    with col3:

        with st.container(border=True):

            st.metric(
                "◈ DEADLINES",
                "03"
            )

            st.write(
                "Extracts deadlines and important dates."
            )

    st.write("")

    # ========================================================
    # HOW IT WORKS
    # ========================================================

    st.subheader("🚀 INTELLIGENCE PIPELINE")

    step1, step2, step3 = st.columns(3)

    with step1:

        with st.container(border=True):

            st.write("### 01")
            st.write("🎙️ **UPLOAD**")

            st.caption(
                "Provide your meeting recording."
            )

    with step2:

        with st.container(border=True):

            st.write("### 02")
            st.write("🧠 **ANALYZE**")

            st.caption(
                "Gemini processes the conversation."
            )

    with step3:

        with st.container(border=True):

            st.write("### 03")
            st.write("⚡ **ACT**")

            st.caption(
                "Receive structured actionable intelligence."
            )

    st.write("")

    # ========================================================
    # START
    # ========================================================

    with st.container(border=True):

        st.subheader(
            "🔮 READY TO ANALYZE?"
        )

        st.write(
            "Begin your meeting intelligence session."
        )

        if st.button(
            "⚡ START ANALYSIS →",
            type="primary",
            use_container_width=True
        ):

            st.session_state.page = 2
            st.rerun()


# ============================================================
# PAGE 2 — UPLOAD
# ============================================================

elif st.session_state.page == 2:

    st.title("🎙️ AUDIO INTELLIGENCE")

    st.subheader(
        "Upload your meeting recording"
    )

    st.caption(
        "STEP 02 / 03"
    )

    st.progress(0.66)

    st.write("")

    # ========================================================
    # UPLOAD PANEL
    # ========================================================

    with st.container(border=True):

        st.subheader(
            "💠 RECORDING INPUT"
        )

        st.write(
            "Choose an MP3, WAV or M4A meeting recording."
        )

        audio = st.file_uploader(
            "UPLOAD AUDIO",
            type=["mp3", "wav", "m4a"],
            help="Supported formats: MP3, WAV and M4A."
        )

    # ========================================================
    # AUDIO EXISTS
    # ========================================================

    if audio is not None:

        st.session_state.audio_name = audio.name

        st.write("")

        # ====================================================
        # FILE ACCEPTED
        # ====================================================

        with st.container(border=True):

            st.success(
                f"✓ AUDIO READY — {audio.name}"
            )

            st.audio(audio)

        st.write("")

        # ====================================================
        # FILE INFORMATION
        # ====================================================

        st.subheader(
            "📊 RECORDING DATA"
        )

        file_size_mb = (
            len(audio.getbuffer())
            / (1024 * 1024)
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            with st.container(border=True):

                st.metric(
                    "📁 FILE",
                    audio.name
                )

        with col2:

            with st.container(border=True):

                st.metric(
                    "💾 SIZE",
                    f"{file_size_mb:.2f} MB"
                )

        with col3:

            with st.container(border=True):

                st.metric(
                    "🎧 FORMAT",
                    audio.name.split(".")[-1].upper()
                )

        st.write("")

        # ====================================================
        # ANALYSIS TARGETS
        # ====================================================

        with st.container(border=True):

            st.subheader(
                "🧠 AI ANALYSIS TARGETS"
            )

            target1, target2 = st.columns(2)

            with target1:

                st.write(
                    "⚡ **TASKS**"
                )

                st.caption(
                    "Assigned actions and responsibilities."
                )

                st.write(
                    "🔗 **PROMISES**"
                )

                st.caption(
                    "Commitments made by participants."
                )

            with target2:

                st.write(
                    "◈ **DEADLINES**"
                )

                st.caption(
                    "Important dates and time limits."
                )

                st.write(
                    "💡 **DECISIONS**"
                )

                st.caption(
                    "Important decisions made during the meeting."
                )

        st.write("")

        # ====================================================
        # ANALYZE
        # ====================================================

        if st.button(
            "🧠 ANALYZE MEETING",
            type="primary",
            use_container_width=True
        ):

            progress = st.progress(0)

            status = st.empty()

            temp_audio_path = None

            try:

                # ==================================================
                # SAVE AUDIO
                # ==================================================

                status.info(
                    "⚡ Preparing audio..."
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
                # UPLOAD TO GEMINI
                # ==================================================

                status.info(
                    "📡 Sending audio to Gemini..."
                )

                progress.progress(30)

                uploaded_file = client.files.upload(
                    file=temp_audio_path
                )

                # ==================================================
                # AI ANALYSIS
                # ==================================================

                status.info(
                    "🧠 AI is analyzing the conversation..."
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
                    "⚡ Forging the intelligence report..."
                )

                # ==================================================
                # RESPONSE
                # ==================================================

                result_text = (
                    interaction.output_text.strip()
                )

                # ==================================================
                # CLEAN JSON
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
                # PARSE
                # ==================================================

                meeting_data = json.loads(
                    result_text
                )

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
                    "✓ ANALYSIS COMPLETE"
                )

                st.session_state.page = 3

                st.rerun()

            except json.JSONDecodeError:

                st.error(
                    "⚠️ AI returned invalid JSON."
                )

                st.code(
                    result_text
                    if "result_text" in locals()
                    else "No response received."
                )

            except Exception as e:

                st.error(
                    "⚠️ Analysis failed."
                )

                st.info(
                    "Check your Gemini API key, "
                    "audio file and API access."
                )

                st.exception(e)

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

        st.write("")

        with st.container(border=True):

            st.info(
                "🎙️ Upload a meeting recording to begin."
            )

    st.write("")

    if st.button(
        "← BACK TO HOME"
    ):

        st.session_state.page = 1
        st.rerun()


# ============================================================
# PAGE 3 — RESULTS
# ============================================================

elif st.session_state.page == 3:

    st.title("⚡ INTELLIGENCE REPORT")

    st.subheader(
        "Your meeting has been converted into actionable intelligence."
    )

    st.caption(
        "STEP 03 / 03"
    )

    st.progress(1.0)

    meeting_data = st.session_state.meeting_data

    if meeting_data is None:

        st.warning(
            "No analysis results are available."
        )

        if st.button(
            "← RETURN TO AUDIO"
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
    # SEPARATE DATA
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
        "🔷 INTELLIGENCE OVERVIEW"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        with st.container(border=True):

            st.metric(
                "⚡ TASKS",
                len(tasks)
            )

    with col2:

        with st.container(border=True):

            st.metric(
                "🔗 PROMISES",
                len(promises)
            )

    with col3:

        with st.container(border=True):

            st.metric(
                "◈ DEADLINES",
                len(deadlines)
            )

    with col4:

        with st.container(border=True):

            st.metric(
                "💡 DECISIONS",
                len(decisions)
            )

    st.write("")

    # ========================================================
    # SUMMARY
    # ========================================================

    with st.container(border=True):

        st.subheader(
            "📡 MEETING SIGNAL"
        )

        st.write(summary)

    st.write("")

    # ========================================================
    # TASKS
    # ========================================================

    st.subheader(
        "⚡ TASK INTELLIGENCE"
    )

    if tasks:

        for index, task in enumerate(
            tasks,
            start=1
        ):

            with st.container(border=True):

                st.write(
                    f"### ⚡ TASK {index}"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.caption(
                        "👤 ASSIGNED TO"
                    )

                    st.write(
                        task.get(
                            "speaker",
                            "Unknown"
                        )
                    )

                with col2:

                    st.caption(
                        "◈ DEADLINE"
                    )

                    st.write(
                        task.get(
                            "deadline",
                            "Not specified"
                        )
                    )

                st.write(
                    "📌 **ACTION**"
                )

                st.write(
                    task.get(
                        "task",
                        "No task description"
                    )
                )

    else:

        with st.container(border=True):

            st.info(
                "No tasks detected."
            )

    st.write("")

    # ========================================================
    # PROMISES
    # ========================================================

    st.subheader(
        "🔗 PROMISE & COMMITMENT INTELLIGENCE"
    )

    if promises:

        for index, promise in enumerate(
            promises,
            start=1
        ):

            with st.container(border=True):

                st.write(
                    f"### 🔗 COMMITMENT {index}"
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.caption(
                        "👤 PERSON"
                    )

                    st.write(
                        promise.get(
                            "speaker",
                            "Unknown"
                        )
                    )

                with col2:

                    st.caption(
                        "◈ DEADLINE"
                    )

                    st.write(
                        promise.get(
                            "deadline",
                            "Not specified"
                        )
                    )

                st.write(
                    "📌 **COMMITMENT**"
                )

                st.write(
                    promise.get(
                        "task",
                        "No commitment description"
                    )
                )

    else:

        with st.container(border=True):

            st.info(
                "No promises or commitments detected."
            )

    st.write("")

    # ========================================================
    # DEADLINES
    # ========================================================

    st.subheader(
        "◈ DEADLINE MATRIX"
    )

    if deadlines:

        for index, item in enumerate(
            deadlines,
            start=1
        ):

            with st.container(border=True):

                st.write(
                    f"### ◈ DEADLINE {index}"
                )

                st.write(
                    item.get(
                        "deadline",
                        "Not specified"
                    )
                )

                st.caption(
                    "RELATED ACTION"
                )

                st.write(
                    item.get(
                        "task",
                        "Not specified"
                    )
                )

    else:

        with st.container(border=True):

            st.info(
                "No deadlines detected."
            )

    st.write("")

    # ========================================================
    # DECISIONS
    # ========================================================

    st.subheader(
        "💡 DECISION SIGNALS"
    )

    if decisions:

        for index, decision in enumerate(
            decisions,
            start=1
        ):

            with st.container(border=True):

                st.write(
                    f"### 💡 DECISION {index}"
                )

                st.write(decision)

    else:

        with st.container(border=True):

            st.info(
                "No important decisions detected."
            )

    st.write("")

    # ========================================================
    # DOWNLOAD
    # ========================================================

    with st.container(border=True):

        st.subheader(
            "📥 EXPORT INTELLIGENCE"
        )

        download_text = ""

        download_text += (
            "NEON MEETING AI\n"
        )

        download_text += (
            "AI MEETING TO ACTION INTELLIGENCE\n"
        )

        download_text += "=" * 55
        download_text += "\n\n"

        download_text += (
            "MEETING SUMMARY\n"
        )

        download_text += "-" * 35
        download_text += "\n"

        download_text += summary
        download_text += "\n\n"

        # ====================================================
        # TASKS
        # ====================================================

        download_text += (
            "TASKS\n"
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

        # ====================================================
        # PROMISES
        # ====================================================

        download_text += (
            "PROMISES & COMMITMENTS\n"
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

        # ====================================================
        # DECISIONS
        # ====================================================

        download_text += (
            "IMPORTANT DECISIONS\n"
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
                "No important decisions identified.\n"
            )

        st.download_button(
            label="⬇️ DOWNLOAD INTELLIGENCE REPORT",
            data=download_text,
            file_name="neon_meeting_intelligence.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.write("")

    # ========================================================
    # NEW ANALYSIS
    # ========================================================

    if st.button(
        "⚡ ANALYZE ANOTHER MEETING",
        type="primary",
        use_container_width=True
    ):

        st.session_state.page = 2
        st.session_state.meeting_data = None
        st.session_state.audio_name = None

        st.rerun()

