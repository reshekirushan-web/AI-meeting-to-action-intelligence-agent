import streamlit as st
from google import genai
import os
import json
import tempfile
import html


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
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = 1

if "meeting_data" not in st.session_state:
    st.session_state.meeting_data = None

if "audio_name" not in st.session_state:
    st.session_state.audio_name = None


# ============================================================
# GEMINI API
# ============================================================

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = None

if not api_key:
    st.error("GEMINI_API_KEY is not configured.")
    st.info("Add GEMINI_API_KEY to your Streamlit Secrets.")
    st.stop()

client = genai.Client(api_key=api_key)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
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
                rgba(255, 72, 150, 0.32),
                transparent 25%
            ),
            radial-gradient(
                circle at 0% 100%,
                rgba(255, 90, 65, 0.28),
                transparent 24%
            ),
            #170024;

        min-height: 100vh;
    }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
        max-width: 100% !important;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }


    /* =====================================================
       BACKGROUND GLOW
    ===================================================== */

    .glow-top {
        position: fixed;

        width: 300px;
        height: 300px;

        top: -130px;
        right: -100px;

        border-radius: 50%;

        background:
            linear-gradient(
                135deg,
                #ff5d62,
                #c832ff
            );

        filter: blur(45px);

        opacity: 0.75;

        pointer-events: none;

        z-index: 0;
    }


    .glow-bottom {
        position: fixed;

        width: 300px;
        height: 300px;

        bottom: -140px;
        left: -120px;

        border-radius: 50%;

        background:
            linear-gradient(
                135deg,
                #ff7048,
                #9d28ff
            );

        filter: blur(45px);

        opacity: 0.7;

        pointer-events: none;

        z-index: 0;
    }


    /* =====================================================
       MAIN CONTENT
    ===================================================== */

    .main-content {
        position: relative;

        z-index: 2;

        min-height: 82vh;

        padding: 45px 7%;
    }


    /* =====================================================
       PAGE INDICATOR
    ===================================================== */

    .page-indicator {
        display: flex;

        align-items: center;

        gap: 11px;

        color: #bda8df;

        font-size: 13px;

        font-weight: 600;

        letter-spacing: 2px;

        margin-bottom: 60px;
    }


    .dot {
        width: 9px;
        height: 9px;

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
       TITLE
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

        max-width: 1000px;

        animation:
            titleAppear 0.8s ease forwards;
    }


    .subtitle {
        margin-top: 30px;

        color: #d2b9f5;

        font-size: 16px;

        font-weight: 500;

        line-height: 1.8;

        letter-spacing: 3px;

        text-transform: uppercase;

        max-width: 700px;

        animation:
            subtitleAppear 1s ease forwards;
    }


    .gradient-line {
        width: 85px;

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
        z-index: 50;
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

        padding: 14px 34px !important;

        font-family: 'Montserrat', sans-serif !important;

        font-size: 13px !important;

        font-weight: 800 !important;

        letter-spacing: 1.5px !important;

        box-shadow:
            0 0 12px rgba(255, 73, 168, 0.7),
            0 0 35px rgba(130, 50, 255, 0.35);

        transition:
            transform 0.3s ease,
            box-shadow 0.3s ease;
    }


    .stButton > button:hover {
        transform:
            translateY(-4px)
            scale(1.03);

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

        margin-bottom: 35px;
    }


    .audio-oval {
        width: 510px;

        height: 140px;

        border-radius: 100px;

        background:
            linear-gradient(
                120deg,
                rgba(93, 25, 150, 0.9),
                rgba(29, 8, 65, 0.96)
            );

        border: 2px solid #c65cff;

        display: flex;

        justify-content: center;

        align-items: center;

        position: relative;

        box-shadow:
            0 0 15px #ff49c6,
            0 0 40px rgba(180, 50, 255, 0.65),
            inset 0 0 30px rgba(160, 65, 255, 0.25);

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

        gap: 6px;

        height: 80px;
    }


    .wave span {
        width: 5px;

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
            waveAnimation 1.1s ease-in-out infinite;
    }


    .wave span:nth-child(1) {
        height: 22px;
        animation-delay: 0.05s;
    }

    .wave span:nth-child(2) {
        height: 38px;
        animation-delay: 0.10s;
    }

    .wave span:nth-child(3) {
        height: 55px;
        animation-delay: 0.15s;
    }

    .wave span:nth-child(4) {
        height: 30px;
        animation-delay: 0.20s;
    }

    .wave span:nth-child(5) {
        height: 65px;
        animation-delay: 0.25s;
    }

    .wave span:nth-child(6) {
        height: 43px;
        animation-delay: 0.30s;
    }

    .wave span:nth-child(7) {
        height: 78px;
        animation-delay: 0.35s;
    }

    .wave span:nth-child(8) {
        height: 48px;
        animation-delay: 0.40s;
    }

    .wave span:nth-child(9) {
        height: 68px;
        animation-delay: 0.45s;
    }

    .wave span:nth-child(10) {
        height: 35px;
        animation-delay: 0.50s;
    }

    .wave span:nth-child(11) {
        height: 58px;
        animation-delay: 0.55s;
    }

    .wave span:nth-child(12) {
        height: 28px;
        animation-delay: 0.60s;
    }

    .wave span:nth-child(13) {
        height: 48px;
        animation-delay: 0.65s;
    }

    .wave span:nth-child(14) {
        height: 22px;
        animation-delay: 0.70s;
    }


    /* =====================================================
       UPLOADER
    ===================================================== */

    [data-testid="stFileUploader"] {
        position: relative;

        z-index: 30;

        max-width: 650px;

        margin: auto;
    }


    [data-testid="stFileUploader"] section {
        background:
            rgba(35, 8, 65, 0.78);

        border:
            1px solid #8d39d9;

        border-radius: 20px;

        box-shadow:
            0 0 20px rgba(145, 48, 255, 0.15);
    }


    /* =====================================================
       AUDIO PLAYER
    ===================================================== */

    [data-testid="stAudio"] {
        max-width: 650px;

        margin:
            20px auto;

        position: relative;

        z-index: 30;
    }


    /* =====================================================
       RESULT CARDS
    ===================================================== */

    .result-card {
        margin-top: 20px;

        padding: 23px 26px;

        border-radius: 20px;

        background:
            rgba(30, 8, 55, 0.72);

        border:
            1px solid rgba(193, 75, 255, 0.5);

        box-shadow:
            0 0 25px rgba(153, 50, 255, 0.14);

        animation:
            resultAppear 0.6s ease forwards;
    }


    .result-type {
        color: #ff75bb;

        font-size: 12px;

        font-weight: 800;

        letter-spacing: 2px;

        text-transform: uppercase;

        margin-bottom: 12px;
    }


    .result-row {
        color: #e8d8f8;

        font-size: 15px;

        line-height: 1.7;

        margin: 5px 0;
    }


    .result-row b {
        color: #ffffff;
    }


    /* =====================================================
       SUMMARY
    ===================================================== */

    .summary-box {
        margin-top: 35px;

        padding: 25px;

        border-radius: 20px;

        background:
            rgba(35, 8, 65, 0.72);

        border:
            1px solid rgba(255, 82, 180, 0.4);

        color: #e5d5f4;

        font-size: 15px;

        line-height: 1.8;
    }


    /* =====================================================
       DOWNLOAD BOX
    ===================================================== */

    .download-box {
        margin-top: 40px;

        padding: 25px;

        text-align: center;

        border-radius: 22px;

        background:
            rgba(45, 10, 75, 0.7);

        border:
            1px solid rgba(255, 82, 180, 0.45);

        box-shadow:
            0 0 25px rgba(153, 50, 255, 0.15);
    }


    .download-title {
        color: #e0c8ff;

        font-size: 20px;

        font-weight: 800;

        letter-spacing: 1px;
    }


    .download-description {
        color: #bda8df;

        font-size: 13px;

        margin-top: 8px;
    }


    /* =====================================================
       RESULT CARDS
    ===================================================== */

    .visual-cards {
        display: flex;

        justify-content: center;

        align-items: center;

        gap: 55px;

        margin-top: 80px;

        margin-bottom: 60px;
    }


    .visual-card-wrapper {
        text-align: center;

        animation:
            floating 3s ease-in-out infinite;
    }


    .visual-card {
        width: 150px;

        height: 150px;

        border-radius: 50%;

        display: flex;

        justify-content: center;

        align-items: center;

        background:
            rgba(30, 10, 65, 0.65);

        border:
            2px solid #bd52ff;

        box-shadow:
            0 0 15px rgba(211, 63, 255, 0.6),
            inset 0 0 25px rgba(130, 40, 255, 0.2);
    }


    .visual-card-wrapper:nth-child(1)
    .visual-card {
        border-color: #ff5b77;
    }


    .visual-card-wrapper:nth-child(3)
    .visual-card {
        border-color: #626cff;
    }


    .visual-icon {
        font-size: 45px;
    }


    .visual-label {
        color: #d4b5ff;

        font-size: 13px;

        font-weight: 700;

        letter-spacing: 2px;

        margin-top: 16px;
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


    @keyframes titleAppear {

        from {
            opacity: 0;
            transform: translateY(20px);
        }

        to {
            opacity: 1;
            transform: translateY(0);
        }
    }


    @keyframes subtitleAppear {

        from {
            opacity: 0;
            transform: translateY(15px);
        }

        to {
            opacity: 1;
            transform: translateY(0);
        }
    }


    @keyframes resultAppear {

        from {
            opacity: 0;
            transform: translateY(15px);
        }

        to {
            opacity: 1;
            transform: translateY(0);
        }
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

        .visual-cards {
            gap: 15px;
        }

        .visual-card {
            width: 105px;
            height: 105px;
        }

        .visual-icon {
            font-size: 32px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# BACKGROUND ELEMENTS
# ============================================================

st.markdown(
    """
    <div class="glow-top"></div>
    <div class="glow-bottom"></div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PAGE 1 — INTRO
# ============================================================

if st.session_state.page == 1:

    st.markdown(
        """
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
        """,
        unsafe_allow_html=True
    )

    # Bottom-right button

    col1, col2, col3 = st.columns([7, 2, 1])

    with col2:

        if st.button(
            "GET STARTED  →",
            key="get_started"
        ):

            st.session_state.page = 2
            st.rerun()


# ============================================================
# PAGE 2 — AUDIO UPLOAD
# ============================================================

elif st.session_state.page == 2:

    st.markdown(
        """
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
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # AUDIO UPLOADER
    # ========================================================

    audio = st.file_uploader(
        "UPLOAD THE VOICE",
        type=[
            "mp3",
            "wav",
            "m4a"
        ],
        key="meeting_audio"
    )


    # ========================================================
    # AUDIO PREVIEW
    # ========================================================

    if audio:

        st.session_state.audio_name = audio.name

        st.audio(audio)


        st.markdown(
            f"""
            <div style="
                text-align:center;
                color:#cdb6e8;
                font-size:13px;
                margin-top:10px;
            ">
                🎙️ {html.escape(audio.name)}
            </div>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            "<br>",
            unsafe_allow_html=True
        )


        # ====================================================
        # ANALYZE BUTTON
        # ====================================================

        analyze_col1, analyze_col2, analyze_col3 = st.columns(
            [1, 2, 1]
        )

        with analyze_col2:

            analyze = st.button(
                "ANALYZE MEETING  ✦",
                key="analyze_meeting"
            )


        if analyze:

            with st.spinner(
                "🎧 AI is listening to your meeting..."
            ):

                temp_audio_path = None

                try:

                    # --------------------------------------------
                    # CREATE REAL TEMPORARY AUDIO FILE
                    # --------------------------------------------

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

                        temp_audio_path = (
                            temp_audio.name
                        )


                    # --------------------------------------------
                    # UPLOAD AUDIO TO GEMINI
                    # --------------------------------------------

                    audio_file = client.files.upload(
                        file=temp_audio_path
                    )


                    # --------------------------------------------
                    # GEMINI PROMPT
                    # --------------------------------------------

                    prompt = """
You are an AI Meeting-to-Action Intelligence Agent.

Analyze the uploaded meeting recording carefully.

Extract the following:

1. Tasks assigned to people
2. Promises or commitments made by people
3. Deadlines mentioned
4. Important decisions
5. A concise meeting summary

For every task or promise, identify the speaker if possible.

If the actual person's name is not available,
use Speaker 1, Speaker 2, Speaker 3, etc.

Do not invent names or information.

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

Important rules:

- Do not invent information.
- If there is no deadline, use null.
- Include both tasks and promises.
- Keep descriptions concise.
- If there are no commitments, return an empty list.
- If there are no decisions, return an empty list.
"""


                    # --------------------------------------------
                    # SEND AUDIO + PROMPT TO GEMINI
                    # --------------------------------------------

                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[
                            audio_file,
                            prompt
                        ]
                    )


                    # --------------------------------------------
                    # GET RESPONSE
                    # --------------------------------------------

                    result_text = response.text.strip()


                    # --------------------------------------------
                    # CLEAN JSON MARKDOWN
                    # --------------------------------------------

                    if result_text.startswith(
                        "```json"
                    ):

                        result_text = (
                            result_text[7:]
                        )

                    elif result_text.startswith(
                        "```"
                    ):

                        result_text = (
                            result_text[3:]
                        )


                    if result_text.endswith(
                        "```"
                    ):

                        result_text = (
                            result_text[:-3]
                        )


                    result_text = result_text.strip()


                    # --------------------------------------------
                    # PARSE JSON
                    # --------------------------------------------

                    meeting_data = json.loads(
                        result_text
                    )


                    # --------------------------------------------
                    # SAVE RESULT
                    # --------------------------------------------

                    st.session_state.meeting_data = (
                        meeting_data
                    )


                    st.success(
                        "✅ Meeting analyzed successfully!"
                    )


                    # --------------------------------------------
                    # MOVE TO PAGE 3
                    # --------------------------------------------

                    st.session_state.page = 3

                    st.rerun()


                except json.JSONDecodeError:

                    st.error(
                        "Gemini returned an invalid "
                        "JSON response. Please try again."
                    )


                except Exception as error:

                    st.error(
                        f"Something went wrong: {error}"
                    )


                finally:

                    # --------------------------------------------
                    # DELETE TEMP FILE
                    # --------------------------------------------

                    if (
                        temp_audio_path
                        and os.path.exists(
                            temp_audio_path
                        )
                    ):

                        os.remove(
                            temp_audio_path
                        )


    # ========================================================
    # BACK BUTTON
    # ========================================================

    st.markdown(
        "<br>",
        unsafe_allow_html=True
    )

    back_col1, back_col2, back_col3 = st.columns(
        [1, 1, 5]
    )

    with back_col1:

        if st.button(
            "← BACK",
            key="back_page_2"
        ):

            st.session_state.page = 1
            st.rerun()


# ============================================================
# PAGE 3 — RESULTS
# ============================================================

elif st.session_state.page == 3:

    st.markdown(
        """
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
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # GET MEETING DATA
    # ========================================================

    meeting_data = (
        st.session_state.meeting_data
    )


    if meeting_data:

        commitments = meeting_data.get(
            "commitments",
            []
        )

        summary = meeting_data.get(
            "summary",
            "No summary available."
        )

        decisions = meeting_data.get(
            "decisions",
            []
        )


        # ====================================================
        # VISUAL CARDS
        # ====================================================

        st.markdown(
            """
            <div class="visual-cards">

                <div class="visual-card-wrapper">

                    <div class="visual-card">
                        <div class="visual-icon"
                             style="color:#ff607c;">
                            ✓
                        </div>
                    </div>

                    <div class="visual-label">
                        TASKS
                    </div>

                </div>


                <div class="visual-card-wrapper">

                    <div class="visual-card">
                        <div class="visual-icon"
                             style="color:#c45cff;">
                            🤝
                        </div>
                    </div>

                    <div class="visual-label">
                        PROMISES
                    </div>

                </div>


                <div class="visual-card-wrapper">

                    <div class="visual-card">
                        <div class="visual-icon"
                             style="color:#6674ff;">
                            📅
                        </div>
                    </div>

                    <div class="visual-label">
                        DEADLINES
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        # ====================================================
        # MEETING SUMMARY
        # ====================================================

        st.markdown(
            """
            <h3 style="
                color:#dfc8f8;
                letter-spacing:1px;
                margin-top:20px;
            ">
                📝 MEETING SUMMARY
            </h3>
            """,
            unsafe_allow_html=True
        )


        st.markdown(
            f"""
            <div class="summary-box">
                {html.escape(str(summary))}
            </div>
            """,
            unsafe_allow_html=True
        )


        # ====================================================
        # TASKS & PROMISES
        # ====================================================

        st.markdown(
            """
            <h3 style="
                color:#dfc8f8;
                letter-spacing:1px;
                margin-top:45px;
            ">
                ✅ TASKS & PROMISES
            </h3>
            """,
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
                    "deadline",
                    None
                )

                commitment_type = item.get(
                    "type",
                    "Task"
                )


                if deadline is None:
                    deadline = "No deadline"


                st.markdown(
                    f"""
                    <div class="result-card">

                        <div class="result-type">
                            {index}. {html.escape(
                                str(commitment_type)
                            )}
                        </div>

                        <div class="result-row">
                            👤 <b>Person:</b>
                            {html.escape(str(speaker))}
                        </div>

                        <div class="result-row">
                            📌 <b>Task / Promise:</b>
                            {html.escape(str(task))}
                        </div>

                        <div class="result-row">
                            📅 <b>Deadline:</b>
                            {html.escape(str(deadline))}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


        else:

            st.info(
                "No tasks or promises were detected."
            )


        # ====================================================
        # DECISIONS
        # ====================================================

        if decisions:

            st.markdown(
                """
                <h3 style="
                    color:#dfc8f8;
                    letter-spacing:1px;
                    margin-top:45px;
                ">
                    💡 IMPORTANT DECISIONS
                </h3>
                """,
                unsafe_allow_html=True
            )


            for decision in decisions:

                st.markdown(
                    f"""
                    <div class="result-card">

                        <div class="result-row">
                            💡 {html.escape(
                                str(decision)
                            )}
                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


        # ====================================================
        # CREATE TXT REPORT
        # ====================================================

        download_text = ""

        download_text += (
            "AI MEETING TO ACTION\n"
        )

        download_text += (
            "MEETING TASKS & PROMISES REPORT\n"
        )

        download_text += (
            "=" * 55
            + "\n\n"
        )


        # Summary

        download_text += (
            "MEETING SUMMARY\n"
        )

        download_text += (
            "-" * 55
            + "\n"
        )

        download_text += (
            str(summary)
            + "\n\n"
        )


        # Tasks

        download_text += (
            "TASKS & PROMISES\n"
        )

        download_text += (
            "-" * 55
            + "\n\n"
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
                    "deadline",
                    None
                )

                commitment_type = item.get(
                    "type",
                    "Task"
                )


                if deadline is None:
                    deadline = "No deadline"


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

                download_text += "\n"


        else:

            download_text += (
                "No tasks or promises detected.\n\n"
            )


        # Decisions

        if decisions:

            download_text += (
                "IMPORTANT DECISIONS\n"
            )

            download_text += (
                "-" * 55
                + "\n\n"
            )

            for index, decision in enumerate(
                decisions,
                start=1
            ):

                download_text += (
                    f"{index}. "
                    f"{decision}\n"
                )


        # ====================================================
        # DOWNLOAD SECTION
        # ====================================================

        st.markdown(
            """
            <div class="download-box">

                <div class="download-title">
                    📥 DOWNLOAD YOUR RESULTS
                </div>

                <div class="download-description">
                    Save all detected tasks,
                    promises, deadlines and decisions.
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


        download_col1, download_col2, download_col3 = (
            st.columns([1, 2, 1])
        )


        with download_col2:

            st.download_button(
                label="⬇️ DOWNLOAD TASKS & PROMISES",
                data=download_text,
                file_name=(
                    "meeting_tasks_and_promises.txt"
                ),
                mime="text/plain",
                key="download_results"
            )


        # ====================================================
        # START ANOTHER MEETING
        # ====================================================

        st.markdown(
            "<br><br>",
            unsafe_allow_html=True
        )


        new_col1, new_col2, new_col3 = (
            st.columns([1, 2, 1])
        )


        with new_col2:

            if st.button(
                "🎙️ ANALYZE ANOTHER MEETING",
                key="another_meeting"
            ):

                st.session_state.page = 2

                st.session_state.meeting_data = None

                st.session_state.audio_name = None

                st.rerun()


    else:

        st.warning(
            "No meeting analysis is available."
        )


        if st.button(
            "← BACK TO AUDIO",
            key="back_to_audio"
        ):

            st.session_state.page = 2
            st.rerun()