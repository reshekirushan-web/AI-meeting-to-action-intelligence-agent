
import streamlit as st
from google import genai
import os
import json
import tempfile


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="AI Meeting to Action",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# SESSION STATE
# =========================================================

if "page" not in st.session_state:
    st.session_state.page = 1

if "meeting_data" not in st.session_state:
    st.session_state.meeting_data = None

if "audio_uploaded" not in st.session_state:
    st.session_state.audio_uploaded = False


# =========================================================
# GEMINI API
# =========================================================

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

if not api_key:
    st.error(
        "GEMINI_API_KEY is not configured. "
        "Add it to Streamlit Secrets."
    )
    st.stop()

client = genai.Client(api_key=api_key)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

@import url(
    'https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700;800;900&display=swap'
);


/* =====================================================
   GLOBAL
===================================================== */

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 100% 0%,
            rgba(255, 75, 150, 0.35),
            transparent 25%
        ),
        radial-gradient(
            circle at 0% 100%,
            rgba(255, 70, 110, 0.30),
            transparent 25%
        ),
        #170024;

    min-height: 100vh;
}


/* Remove Streamlit default elements */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}


/* Main container */

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 3rem !important;
    max-width: 100% !important;
}


/* =====================================================
   BACKGROUND BLOBS
===================================================== */

.blob {
    position: fixed;

    width: 280px;
    height: 280px;

    border-radius: 50%;

    filter: blur(35px);

    opacity: 0.8;

    pointer-events: none;

    z-index: 0;
}

.blob-one {
    top: -100px;
    right: -80px;

    background:
        linear-gradient(
            135deg,
            #ff5d62,
            #c832ff
        );
}

.blob-two {
    bottom: -120px;
    left: -100px;

    background:
        linear-gradient(
            135deg,
            #ff7048,
            #9d28ff
        );
}


/* =====================================================
   MAIN CONTENT
===================================================== */

.main-content {
    position: relative;

    z-index: 2;

    min-height: 78vh;

    padding: 40px 7%;
}


/* =====================================================
   PAGE INDICATOR
===================================================== */

.page-indicator {
    display: flex;

    align-items: center;

    gap: 12px;

    color: #bda8df;

    font-size: 14px;

    letter-spacing: 2px;

    margin-bottom: 55px;
}

.dot {
    width: 10px;
    height: 10px;

    border: 1px solid #a95cff;

    border-radius: 50%;

    display: inline-block;
}

.dot.active {
    background:
        linear-gradient(
            135deg,
            #ff5c70,
            #9d45ff
        );

    box-shadow:
        0 0 12px #ff4f9a;
}


/* =====================================================
   TITLES
===================================================== */

.title {
    font-size: clamp(42px, 5vw, 76px);

    font-weight: 900;

    line-height: 1.02;

    text-transform: uppercase;

    background:
        linear-gradient(
            90deg,
            #ff586d,
            #ff6a92,
            #9c4dff
        );

    -webkit-background-clip: text;

    -webkit-text-fill-color: transparent;

    max-width: 950px;
}

.subtitle {
    margin-top: 30px;

    color: #d2b9f5;

    font-size: 16px;

    line-height: 1.8;

    letter-spacing: 4px;

    text-transform: uppercase;

    max-width: 700px;
}

.gradient-line {
    width: 80px;

    height: 5px;

    border-radius: 10px;

    background:
        linear-gradient(
            90deg,
            #ff586d,
            #9e39ff
        );

    margin-top: 30px;

    box-shadow:
        0 0 15px #e13aff;
}


/* =====================================================
   BUTTONS
===================================================== */

.stButton {
    position: relative;

    z-index: 20;
}

.stButton > button {
    border: 1px solid #ff71bd !important;

    background:
        linear-gradient(
            100deg,
            #ff526c,
            #c735ff,
            #4932ff
        ) !important;

    color: white !important;

    border-radius: 50px !important;

    padding: 15px 38px !important;

    font-family: 'Montserrat', sans-serif !important;

    font-size: 14px !important;

    font-weight: 700 !important;

    letter-spacing: 1px !important;

    box-shadow:
        0 0 12px rgba(255, 73, 168, 0.7),
        0 0 35px rgba(130, 50, 255, 0.35);

    transition:
        transform 0.3s ease,
        box-shadow 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-4px) scale(1.03);

    box-shadow:
        0 0 20px rgba(255, 73, 168, 0.9),
        0 0 45px rgba(130, 50, 255, 0.65);
}


/* =====================================================
   AUDIO OVAL
===================================================== */

.audio-container {
    display: flex;

    justify-content: center;

    align-items: center;

    margin-top: 110px;

    margin-bottom: 40px;
}

.audio-oval {
    width: 500px;

    height: 135px;

    border-radius: 100px;

    background:
        linear-gradient(
            120deg,
            rgba(93, 25, 150, 0.9),
            rgba(29, 8, 65, 0.95)
        );

    border: 3px solid #c65cff;

    box-shadow:
        0 0 15px #ff49c6,
        0 0 40px rgba(180, 50, 255, 0.65),
        inset 0 0 30px rgba(160, 65, 255, 0.25);

    position: relative;

    display: flex;

    justify-content: center;

    align-items: center;

    animation:
        pulseOval 3s ease-in-out infinite;
}


/* =====================================================
   AUDIO WAVE
===================================================== */

.wave {
    display: flex;

    align-items: center;

    justify-content: center;

    gap: 7px;

    height: 75px;
}

.wave span {
    width: 6px;

    border-radius: 10px;

    background:
        linear-gradient(
            180deg,
            #ff55b8,
            #9b4dff,
            #6370ff
        );

    box-shadow:
        0 0 10px #d348ff;

    animation:
        waveAnimation 1.2s ease-in-out infinite;
}

.wave span:nth-child(1) { height: 20px; }
.wave span:nth-child(2) { height: 35px; }
.wave span:nth-child(3) { height: 50px; }
.wave span:nth-child(4) { height: 28px; }
.wave span:nth-child(5) { height: 65px; }
.wave span:nth-child(6) { height: 40px; }
.wave span:nth-child(7) { height: 75px; }
.wave span:nth-child(8) { height: 45px; }
.wave span:nth-child(9) { height: 65px; }
.wave span:nth-child(10) { height: 32px; }
.wave span:nth-child(11) { height: 55px; }
.wave span:nth-child(12) { height: 25px; }
.wave span:nth-child(13) { height: 48px; }
.wave span:nth-child(14) { height: 20px; }


.wave span:nth-child(2) {
    animation-delay: 0.1s;
}

.wave span:nth-child(3) {
    animation-delay: 0.2s;
}

.wave span:nth-child(4) {
    animation-delay: 0.3s;
}

.wave span:nth-child(5) {
    animation-delay: 0.4s;
}

.wave span:nth-child(6) {
    animation-delay: 0.5s;
}

.wave span:nth-child(7) {
    animation-delay: 0.6s;
}

.wave span:nth-child(8) {
    animation-delay: 0.7s;
}

.wave span:nth-child(9) {
    animation-delay: 0.8s;
}

.wave span:nth-child(10) {
    animation-delay: 0.9s;
}

.wave span:nth-child(11) {
    animation-delay: 1s;


/* =====================================================
   THIRD PAGE CARDS
===================================================== */

.cards {
    display: flex;

    justify-content: center;

    align-items: center;

    gap: 55px;

    margin-top: 100px;
}

.card-wrapper {
    text-align: center;

    animation:
        floating 3s ease-in-out infinite;
}

.card {
    width: 165px;

    height: 165px;

    border-radius: 50%;

    border: 2px solid #bd52ff;

    display: flex;

    justify-content: center;

    align-items: center;

    background:
        rgba(30, 10, 65, 0.6);

    box-shadow:
        0 0 15px rgba(211, 63, 255, 0.6),
        inset 0 0 25px rgba(130, 40, 255, 0.2);
}

.card-wrapper:nth-child(1) .card {
    border-color: #ff5b77;
}

.card-wrapper:nth-child(3) .card {
    border-color: #626cff;
}

.card-icon {
    font-size: 48px;
}

.card-text {
    text-align: center;

    color: #d4b5ff;

    font-size: 14px;

    letter-spacing: 2px;

    margin-top: 18px;
}


/* =====================================================
   RESULT SECTION
===================================================== */

.result-box {
    margin-top: 45px;

    padding: 25px;

    border-radius: 20px;

    background:
        rgba(30, 8, 55, 0.65);

    border: 1px solid rgba(193, 75, 255, 0.5);

    box-shadow:
        0 0 25px rgba(153, 50, 255, 0.15);
}

.result-label {
    color: #a88ac9;

    font-size: 12px;

    letter-spacing: 2px;

    text-transform: uppercase;
}

.result-value {
    color: #f0ddff;

    font-size: 16px;

    margin-top: 8px;
}


/* =====================================================
   DOWNLOAD AREA
===================================================== */

.download-area {
    margin-top: 45px;

    padding: 25px;

    text-align: center;

    border-radius: 20px;

    background:
        rgba(45, 10, 75, 0.65);

    border:
        1px solid rgba(255, 82, 180, 0.45);
}


/* =====================================================
   ANIMATIONS
===================================================== */

@keyframes waveAnimation {

    0%, 100% {
        transform: scaleY(0.55);
    }

    50% {
        transform: scaleY(1.25);
    }
}

@keyframes pulseOval {

    0%, 100% {
        box-shadow:
            0 0 15px #ff49c6,
            0 0 40px rgba(180, 50, 255, 0.55),
            inset 0 0 30px rgba(160, 65, 255, 0.25);
    }

    50% {
        box-shadow:
            0 0 25px #ff49c6,
            0 0 65px rgba(180, 50, 255, 0.85),
            inset 0 0 40px rgba(160, 65, 255, 0.35);
    }
}

@keyframes floating {

    0%, 100% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-12px);
    }
}


/* =====================================================
   FILE UPLOADER
===================================================== */

[data-testid="stFileUploader"] {
    margin-top: 20px;

    position: relative;

    z-index: 30;
}

[data-testid="stFileUploader"] section {
    background:
        rgba(35, 8, 65, 0.75);

    border:
        1px solid #8d39d9;

    border-radius: 20px;
}


/* =====================================================
   MOBILE
===================================================== */

@media (max-width: 800px) {

    .main-content {
        padding: 35px 7%;
    }

    .title {
        font-size: 42px;
    }

    .audio-oval {
        width: 90%;
        height: 110px;
    }

    .cards {
        gap: 15px;
    }

    .card {
        width: 105px;
        height: 105px;
    }

    .card-icon {
        font-size: 35px;
    }
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# BACKGROUND
# =========================================================

st.markdown("""
<div class="blob blob-one"></div>
<div class="blob blob-two"></div>
""", unsafe_allow_html=True)


# =========================================================
# PAGE 1
# =========================================================

if st.session_state.page == 1:

    st.markdown("""
    <div class="main-content">

        <div class="page-indicator">
            <span class="dot active"></span>
            <span class="dot"></span>
            <span class="dot"></span>
            <span>01 / 03</span>
        </div>

        <div class="title">
            AI MEETING TO ACTION<br>
            INTELLIGENCE AGENT
        </div>

        <div class="subtitle">
            TURN CONVERSATIONS INTO<br>
            REAL ACTIONS
        </div>

        <div class="gradient-line"></div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div style="position:fixed;right:7%;bottom:6%;z-index:50;">',
        unsafe_allow_html=True
    )

    if st.button("GET STARTED  →", key="start_button"):
        st.session_state.page = 2
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# PAGE 2
# =========================================================

elif st.session_state.page == 2:

    st.markdown("""
    <div class="main-content">

        <div class="page-indicator">
            <span class="dot"></span>
            <span class="dot active"></span>
            <span class="dot"></span>
            <span>02 / 03</span>
        </div>

        <div class="title">
            LISTEN<br>
            TO YOUR MEETINGS
        </div>

        <div class="subtitle">
            UPLOAD YOUR AUDIO AND LET<br>
            AI DO THE HEAVY LIFTING
        </div>

        <div class="gradient-line"></div>

        <div class="audio-container">

            <div class="audio-oval">

                <div class="wave">
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                    <span></span>
                </div>

            </div>

        </div>

    </div>
    """, unsafe_allow_html=True)


    # -----------------------------------------------------
    # AUDIO UPLOAD
    # -----------------------------------------------------

    audio = st.file_uploader(
        "UPLOAD THE VOICE",
        type=["mp3", "wav", "m4a"],
        key="meeting_audio"
    )


    # -----------------------------------------------------
    # SHOW AUDIO PLAYER
    # -----------------------------------------------------

    if audio:

        st.session_state.audio_uploaded = True

        st.audio(audio)

        st.markdown(
            "<p style='color:#cbb0e8;text-align:center;'>"
            "Audio uploaded successfully"
            "</p>",
            unsafe_allow_html=True
        )


    # -----------------------------------------------------
    # ANALYZE BUTTON
    # -----------------------------------------------------

    if audio:

        if st.button(
            "ANALYZE MEETING  ✦",
            key="analyze_button"
        ):

            with st.spinner(
                "AI is listening to your meeting..."
            ):

                suffix = os.path.splitext(
                    audio.name
                )[1]

                temp_audio_path = None

                try:

                    # Save Streamlit audio
                    # as a real temporary file
                    with tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix=suffix
                    ) as temp_audio:

                        temp_audio.write(
                            audio.getbuffer()
                        )

                        temp_audio_path = (
                            temp_audio.name
                        )


                    # Upload audio to Gemini
                    audio_file = client.files.upload(
                        file=temp_audio_path
                    )


                    # -------------------------------------------------
                    # GEMINI PROMPT
                    # -------------------------------------------------

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
- If the speaker cannot be identified,
  use Speaker 1, Speaker 2, etc.
- Include both tasks and promises.
- Keep task descriptions clear and concise.
"""


                    # -------------------------------------------------
                    # GEMINI ANALYSIS
                    # -------------------------------------------------

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[
                            audio_file,
                            prompt
                        ]
                    )


                    result_text = response.text


                    # Remove markdown JSON fences
                    result_text = result_text.replace(
                        "```json",
                        ""
                    ).replace(
                        "```",
                        ""
                    ).strip()


                    # Convert to JSON
                    meeting_data = json.loads(
                        result_text
                    )


                    # Save result
                    st.session_state.meeting_data = (
                        meeting_data
                    )


                    st.success(
                        "✅ Meeting analyzed successfully!"
                    )


                    # Move to results
                    st.session_state.page = 3

                    st.rerun()


                except json.JSONDecodeError:

                    st.error(
                        "Gemini returned an invalid "
                        "response. Please try again."
                    )


                except Exception as e:

                    st.error(
                        f"An error occurred: {str(e)}"
                    )


                finally:

                    # Delete temporary file
                    if (
                        temp_audio_path
                        and os.path.exists(
                            temp_audio_path
                        )
                    ):

                        os.remove(
                            temp_audio_path
                        )


    # -----------------------------------------------------
    # NEXT BUTTON
    # -----------------------------------------------------

    # Only allow Next if analysis exists
    if st.session_state.meeting_data:

        st.markdown(
            '<div style="position:fixed;right:7%;bottom:6%;z-index:50;">',
            unsafe_allow_html=True
        )

        if st.button(
            "NEXT  →",
            key="page2_next"
        ):

            st.session_state.page = 3
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# PAGE 3
# =========================================================

elif st.session_state.page == 3:

    meeting_data = (
        st.session_state.meeting_data
    )


    # -----------------------------------------------------
    # PAGE HEADER
    # -----------------------------------------------------

    st.markdown("""
    <div class="main-content">

        <div class="page-indicator">
            <span class="dot"></span>
            <span class="dot"></span>
            <span class="dot active"></span>
            <span>03 / 03</span>
        </div>

        <div class="title">
            GET TASKS, PROMISES<br>
            & DEADLINES
        </div>

        <div class="subtitle">
            STAY ORGANIZED. STAY AHEAD.
        </div>

        <div class="gradient-line"></div>

    </div>
    """, unsafe_allow_html=True)


    # =====================================================
    # RESULT DATA
    # =====================================================

    if meeting_data:

        commitments = meeting_data.get(
            "commitments",
            []
        )

        summary = meeting_data.get(
            "summary",
            "No summary available."
        )


        # -------------------------------------------------
        # VISUAL CARDS
        # -------------------------------------------------

        st.markdown("""
        <div class="cards">

            <div class="card-wrapper">

                <div class="card">
                    <div class="card-icon"
                         style="color:#ff607c;">
                        ✓
                    </div>
                </div>

                <div class="card-text">
                    TASKS
                </div>

            </div>


            <div class="card-wrapper">

                <div class="card">
                    <div class="card-icon"
                         style="color:#c45cff;">
                        🤝
                    </div>
                </div>

                <div class="card-text">
                    PROMISES
                </div>

            </div>


            <div class="card-wrapper">

                <div class="card">
                    <div class="card-icon"
                         style="color:#6674ff;">
                        📅
                    </div>
                </div>

                <div class="card-text">
                    DEADLINES
                </div>

            </div>

        </div>
        """, unsafe_allow_html=True)


        # -------------------------------------------------
        # SUMMARY
        # -------------------------------------------------

        st.markdown(
            "<h3 style='color:#d9c3f5;margin-top:70px;'>"
            "📝 MEETING SUMMARY"
            "</h3>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="result-box">

                <div class="result-value">
                    {summary}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        # -------------------------------------------------
        # TASKS & PROMISES
        # -------------------------------------------------

        st.markdown(
            "<h3 style='color:#d9c3f5;margin-top:45px;'>"
            "✅ TASKS & PROMISES"
            "</h3>",
            unsafe_allow_html=True
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


                st.markdown(
                    f"""
                    <div class="result-box">

                        <div class="result-label">
                            {index}. {commitment_type}
                        </div>

                        <div class="result-value">
                            👤 <b>Person:</b>
                            {speaker}
                        </div>

                        <div class="result-value">
                            📌 <b>Task / Promise:</b>
                            {task}
                        </div>

                        <div class="result-value">
                            📅 <b>Deadline:</b>
                            {deadline}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

        else:

            st.info(
                "No tasks or promises were detected."
            )


        # =================================================
        # CREATE DOWNLOAD FILE
        # =================================================

        download_text = ""

        download_text += (
            "AI MEETING TO ACTION\n"
        )

        download_text += (
            "TASKS & PROMISES REPORT\n"
        )

        download_text += (
            "=" * 50 + "\n\n"
        )


        download_text += (
            "MEETING SUMMARY\n"
        )

        download_text += (
            "-" * 50 + "\n"
        )

        download_text += (
            summary + "\n\n"
        )


        download_text += (
            "TASKS & PROMISES\n"
        )

        download_text += (
            "-" * 50 + "\n\n"
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
                    f"{index}. "
                    f"{commitment_type}\n"
                )

                download_text += (
                    f"Person: {speaker}\n"
                )

                download_text += (
                    f"Task / Promise: {task}\n"
                )

                download_text += (
                    f"Deadline: {deadline}\n"
                )

                download_text += (
                    "\n"
                )

        else:

            download_text += (
                "No tasks or promises "
                "were detected.\n"
            )


        # =================================================
        # DOWNLOAD BUTTON
        # =================================================

        st.markdown(
            "<div class='download-area'>"
            "<h3 style='color:#e0c8ff;'>"
            "📥 DOWNLOAD YOUR RESULTS"
            "</h3>"
            "<p style='color:#bda8df;'>"
            "Save all detected tasks, promises "
            "and deadlines."
            "</p>"
            "</div>",
            unsafe_allow_html=True
        )


        st.download_button(
            label="⬇️ DOWNLOAD TASKS & PROMISES",
            data=download_text,
            file_name=(
                "meeting_tasks_and_promises.txt"
            ),
            mime="text/plain",
            key="download_button"
        )


    else:

        st.warning(
            "No meeting analysis is available yet."
        )


        if st.button(
            "← BACK TO AUDIO"
        ):

            st.session_state.page = 2
            st.rerun()