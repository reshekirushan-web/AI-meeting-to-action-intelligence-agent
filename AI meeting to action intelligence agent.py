import os
import json
import tempfile
from pathlib import Path

import streamlit as st
from google import genai


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Neon Meeting AI",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).resolve().parent

# Gemini model requested for the new voice-comparison workflow.
GEMINI_MODEL = "gemini-3.6-flash"


# ============================================================
# PREMIUM GLASS UI — UNCHANGED
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 15% 15%, rgba(70, 80, 120, .32), transparent 30%),
            radial-gradient(circle at 85% 75%, rgba(20, 130, 150, .22), transparent 30%),
            #080b12;
        color: #f5f7fb;
    }

    [data-testid="stSidebar"] {
        background: rgba(255,255,255,.045);
        border-right: 1px solid rgba(255,255,255,.10);
    }

    .glass {
        padding: 24px;
        border-radius: 22px;
        background: rgba(255,255,255,.065);
        border: 1px solid rgba(255,255,255,.12);
        backdrop-filter: blur(18px);
        margin-bottom: 18px;
    }

    .hero {
        padding: 32px;
        border-radius: 28px;
        background: linear-gradient(
            135deg,
            rgba(255,255,255,.10),
            rgba(255,255,255,.035)
        );
        border: 1px solid rgba(255,255,255,.14);
        box-shadow: 0 18px 55px rgba(0,0,0,.28);
        margin-bottom: 24px;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 850;
        letter-spacing: -1.5px;
    }

    .hero-subtitle {
        color: #aeb8ca;
        font-size: 16px;
    }

    .profile-card {
        padding: 18px;
        border-radius: 18px;
        background: rgba(255,255,255,.055);
        border: 1px solid rgba(255,255,255,.10);
        margin-bottom: 12px;
    }

    div.stButton > button {
        border-radius: 14px;
        min-height: 44px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SECRETS / CLIENT
# ============================================================

def get_secret(name: str):
    value = os.environ.get(name)
    if value:
        return value
    try:
        return st.secrets[name]
    except Exception:
        return None


GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
AUTH_USERNAME = get_secret("AUTH_USERNAME") or "admin"
AUTH_PASSWORD = get_secret("AUTH_PASSWORD") or "admin123"


# ============================================================
# SESSION STATE
# ============================================================

def initialize_state():
    defaults = {
        "authenticated": False,
        "page": 1,
        "meeting_data": None,
        "audio_name": None,
        "speaker_results": [],
        "reference_audio_bytes": None,
        "reference_audio_name": None,
        "reference_speaker_name": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_state()


# ============================================================
# LOGIN
# ============================================================

if not st.session_state.authenticated:
    st.write("")
    st.write("")
    st.write("")

    st.markdown(
        '<div class="hero">'
        '<div class="hero-title">💠 NEON MEETING AI</div>'
        '<div class="hero-subtitle">AI MEETING TO ACTION INTELLIGENCE</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.subheader("🔐 SIGN IN")
        st.caption("Enter your credentials to access the meeting intelligence system.")

        username = st.text_input(
            "USERNAME",
            placeholder="Enter username",
            key="login_username",
        )

        password = st.text_input(
            "PASSWORD",
            type="password",
            placeholder="Enter password",
            key="login_password",
        )

        if st.button("🔓 LOGIN", type="primary", use_container_width=True):
            if username == AUTH_USERNAME and password == AUTH_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.page = 1
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

    st.caption("🔒 Secure access • Speaker Recognition • Meeting Intelligence")
    st.stop()


# ============================================================
# AUDIO HELPERS
# ============================================================

def save_uploaded_audio(uploaded, suffix=None):
    """Save a Streamlit UploadedFile to a temporary file."""
    if uploaded is None:
        raise ValueError("No audio file was supplied.")

    if suffix is None:
        suffix = Path(uploaded.name).suffix.lower() or ".wav"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(uploaded.getbuffer())
        return f.name


def save_bytes_to_temp(audio_bytes, suffix):
    """Save reference audio bytes to a temporary file."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
        f.write(audio_bytes)
        return f.name


def clean_json_text(text):
    """Remove Markdown JSON fences if Gemini returns them."""
    text = (text or "").strip()

    if text.startswith("```json"):
        text = text[7:].strip()
    elif text.startswith("```"):
        text = text[3:].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    return text


def upload_to_gemini(client, path):
    """Upload an audio file to Gemini and return its uploaded-file object."""
    return client.files.upload(file=path)


# ============================================================
# SIDEBAR
# ============================================================

reference_ready = bool(st.session_state.reference_audio_bytes)

with st.sidebar:
    st.markdown("## 💠 NEON MEETING AI")
    st.caption("AI Meeting to Action Intelligence")

    st.divider()

    if st.button("🏠 HOME", use_container_width=True):
        st.session_state.page = 1
        st.rerun()

    if st.button("🎙️ VOICE PROFILES", use_container_width=True):
        st.session_state.page = 2
        st.rerun()

    if st.button("🎧 ANALYZE MEETING", use_container_width=True):
        st.session_state.page = 3
        st.rerun()

    st.divider()

    st.write("### 👤 SESSION")
    st.success("Logged in")

    st.metric(
        "Reference Voice",
        "READY" if reference_ready else "NOT SET",
    )

    if st.button("🚪 LOGOUT", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.meeting_data = None
        st.session_state.speaker_results = []
        st.session_state.reference_audio_bytes = None
        st.session_state.reference_audio_name = None
        st.session_state.reference_speaker_name = None
        st.session_state.page = 1
        st.rerun()


# ============================================================
# PAGE 1 — HOME
# ============================================================

if st.session_state.page == 1:

    st.markdown(
        '<div class="hero">'
        '<div class="hero-title">💠 NEON MEETING AI</div>'
        '<div class="hero-subtitle">'
        'AI MEETING TO ACTION INTELLIGENCE'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="glass">'
        '<h3>⚡ CONVERSATION → INTELLIGENCE</h3>'
        '<p>Turn meetings into identified speakers, tasks, promises, deadlines and decisions.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("🎙️ SPEAKER ID", "ON")

    with c2:
        st.metric("🧠 AI ANALYSIS", "ON")

    with c3:
        st.metric("🔗 COMMITMENTS", "ON")

    with c4:
        st.metric("◈ DEADLINES", "ON")

    st.write("")

    if st.button(
        "🎙️ REGISTER VOICE",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.page = 2
        st.rerun()

    if st.button(
        "🎧 ANALYZE A MEETING",
        use_container_width=True,
    ):
        st.session_state.page = 3
        st.rerun()


# ============================================================
# PAGE 2 — REFERENCE VOICE UPLOAD
# ============================================================

elif st.session_state.page == 2:

    st.title("🎙️ VOICE PROFILE")

    st.caption(
        "Upload a reference voice instead of recording in the browser. "
        "The audio is kept only for this Streamlit session and used for comparison."
    )

    st.markdown(
        '<div class="glass">',
        unsafe_allow_html=True,
    )

    name = st.text_input(
        "SPEAKER NAME",
        placeholder="Example: Venkatesh",
        value=st.session_state.reference_speaker_name or "",
        key="reference_speaker_name_input",
    )

    st.write("### 🎤 Upload reference voice")

    reference_audio = st.file_uploader(
        "Upload 10–30 seconds of clear speech",
        type=["wav", "mp3", "m4a", "mp4", "webm", "ogg"],
        key="reference_audio_uploader",
    )

    if reference_audio:
        st.audio(reference_audio)
        st.caption(
            f"🎧 Reference audio: {reference_audio.name} • "
            f"{reference_audio.size / 1024:.1f} KB"
        )

        if st.button(
            "💾 USE REFERENCE VOICE",
            type="primary",
            use_container_width=True,
        ):
            clean_name = name.strip()

            if len(clean_name) < 2:
                st.error("❌ Please enter a valid speaker name.")
            else:
                st.session_state.reference_audio_bytes = reference_audio.getvalue()
                st.session_state.reference_audio_name = reference_audio.name
                st.session_state.reference_speaker_name = clean_name
                st.session_state.meeting_data = None
                st.session_state.speaker_results = []
                st.success(
                    f"✅ Reference voice loaded for {clean_name}."
                )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    st.subheader("👥 REFERENCE VOICE")

    if st.session_state.reference_audio_bytes:
        st.success(
            f"ACTIVE • {st.session_state.reference_speaker_name}"
        )
        st.caption(
            f"Source: {st.session_state.reference_audio_name}"
        )

        if st.button("🗑️ CLEAR REFERENCE VOICE", use_container_width=True):
            st.session_state.reference_audio_bytes = None
            st.session_state.reference_audio_name = None
            st.session_state.reference_speaker_name = None
            st.session_state.meeting_data = None
            st.session_state.speaker_results = []
            st.rerun()
    else:
        st.info("No reference voice uploaded yet.")

    st.divider()

    st.warning(
        "Voice recordings are biometric information. Get the speaker's "
        "consent before uploading and comparing a voice."
    )


# ============================================================
# PAGE 3 — MEETING ANALYSIS
# ============================================================

elif st.session_state.page == 3:

    st.title("🎧 MEETING ANALYSIS")

    if not st.session_state.reference_audio_bytes:
        st.warning(
            "No reference voice is available. Upload a reference audio first."
        )

        if st.button(
            "🎙️ GO TO VOICE PROFILE",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.page = 2
            st.rerun()

        st.stop()

    st.caption(
        f"Reference speaker: {st.session_state.reference_speaker_name} • "
        "Gemini will compare the reference voice with speakers in the meeting."
    )

    audio = st.file_uploader(
        "UPLOAD MEETING RECORDING",
        type=["mp3", "wav", "m4a", "mp4", "webm", "ogg"],
        key="meeting_audio_uploader",
    )

    if audio:
        st.audio(audio)

    if audio and st.button(
        "🧠 ANALYZE MEETING",
        type="primary",
        use_container_width=True,
    ):

        reference_temp = None
        meeting_temp = None

        try:
            if not GEMINI_API_KEY:
                raise RuntimeError(
                    "GEMINI_API_KEY is missing. Add it to Streamlit Secrets."
                )

            reference_suffix = (
                Path(st.session_state.reference_audio_name or ".wav")
                .suffix
                .lower()
                or ".wav"
            )
            meeting_suffix = Path(audio.name).suffix.lower() or ".wav"

            reference_temp = save_bytes_to_temp(
                st.session_state.reference_audio_bytes,
                reference_suffix,
            )
            meeting_temp = save_uploaded_audio(audio, meeting_suffix)

            with st.status(
                "Running Gemini speaker comparison and meeting intelligence...",
                expanded=True,
            ) as status:

                st.write("1/4 Preparing reference voice...")
                st.write("2/4 Uploading reference and meeting audio to Gemini...")

                client = genai.Client(api_key=GEMINI_API_KEY)

                reference_file = upload_to_gemini(
                    client,
                    reference_temp,
                )
                meeting_file = upload_to_gemini(
                    client,
                    meeting_temp,
                )

                reference_name = st.session_state.reference_speaker_name

                prompt = f"""
You are an AI Meeting to Action Intelligence Agent using audio understanding.

There are TWO audio files:

1. REFERENCE VOICE
   - This is the known speaker: {reference_name}
   - The reference audio contains that person's voice.

2. MEETING AUDIO
   - This contains one or more people speaking.

Your job is to compare the reference voice with the voices that occur in the
meeting audio and identify which meeting speaker, if any, appears to match
{reference_name}.

IMPORTANT VOICE-COMPARISON RULES:
- Compare actual acoustic voice characteristics, not the words or topic.
- Do not assume the reference speaker is present.
- If there is not enough audio evidence, return Unknown.
- Do not identify a speaker from the speaker's words alone.
- Treat the comparison as an audio similarity estimate, not definitive
  biometric authentication.
- Use a confidence from 0 to 100 only when there is enough evidence.
- Identify other meeting speakers as Speaker 1, Speaker 2, etc. when possible.
- If the meeting contains only one clearly identifiable speaker, still compare
  that speaker against the reference.

MEETING INTELLIGENCE:
Also analyze the meeting audio for:
1. Concise meeting summary
2. Tasks
3. Promises / commitments
4. Deadlines
5. Important decisions

For every task or promise, identify the speaker label when the audio provides
reasonable evidence. If the matching speaker is the reference person, use the
name {reference_name}.

Return ONLY valid JSON in exactly this structure:

{{
  "summary": "Short meeting summary",
  "speaker_results": [
    {{
      "speaker_label": "Speaker 1",
      "name": "{reference_name}",
      "score": 86,
      "confidence": 86,
      "reason": "Voice characteristics appear similar to the reference audio."
    }},
    {{
      "speaker_label": "Speaker 2",
      "name": "Unknown",
      "score": 34,
      "confidence": 34,
      "reason": "Insufficient similarity to the reference voice."
    }}
  ],
  "commitments": [
    {{
      "speaker": "{reference_name}",
      "task": "Complete the backend",
      "deadline": "Tomorrow",
      "type": "Task"
    }}
  ],
  "decisions": [
    "Decision made"
  ]
}}

Rules:
- Do not invent information.
- If the reference speaker is not confidently identifiable, use Unknown.
- Keep score/confidence between 0 and 100.
- Use "Not specified" when no deadline is mentioned.
- Keep the summary concise.
- Return valid JSON only.
"""

                st.write("3/4 Comparing voices and analyzing the meeting...")

                interaction = client.interactions.create(
                    model=GEMINI_MODEL,
                    input=[
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "audio",
                            "uri": reference_file.uri,
                            "mime_type": reference_file.mime_type,
                        },
                        {
                            "type": "audio",
                            "uri": meeting_file.uri,
                            "mime_type": meeting_file.mime_type,
                        },
                    ],
                )

                result_text = clean_json_text(interaction.output_text)
                meeting_data = json.loads(result_text)

                meeting_data.setdefault("summary", "No summary available.")
                meeting_data.setdefault("commitments", [])
                meeting_data.setdefault("decisions", [])
                meeting_data.setdefault("speaker_results", [])

                # Normalize Gemini output so the existing results UI remains stable.
                normalized_results = []
                for index, item in enumerate(meeting_data["speaker_results"], start=1):
                    if not isinstance(item, dict):
                        continue

                    speaker_label = str(
                        item.get("speaker_label") or f"Speaker {index}"
                    )
                    name_value = str(item.get("name") or "Unknown")

                    raw_score = item.get(
                        "score",
                        item.get("confidence", -1),
                    )
                    try:
                        score = float(raw_score)
                    except (TypeError, ValueError):
                        score = -1.0

                    if name_value.lower() != reference_name.lower():
                        name_value = "Unknown"

                    normalized_results.append(
                        {
                            "speaker_label": speaker_label,
                            "name": name_value,
                            "score": score,
                            "segments": item.get("segments", 0),
                            "reason": str(item.get("reason") or ""),
                        }
                    )

                meeting_data["speaker_results"] = normalized_results
                st.session_state.speaker_results = normalized_results
                st.session_state.meeting_data = meeting_data
                st.session_state.audio_name = audio.name

                st.write("4/4 Finalizing intelligence report...")
                status.update(
                    label="✅ Meeting analysis complete",
                    state="complete",
                )

            st.rerun()

        except json.JSONDecodeError:
            st.error(
                "❌ Gemini returned invalid JSON. Please try the meeting again."
            )

        except Exception as exc:
            st.error(f"❌ Analysis failed: {exc}")

        finally:
            for path in [reference_temp, meeting_temp]:
                if path:
                    try:
                        os.remove(path)
                    except OSError:
                        pass


# ============================================================
# RESULTS
# ============================================================

if st.session_state.meeting_data:

    data = st.session_state.meeting_data

    st.divider()
    st.title("📊 MEETING INTELLIGENCE")

    speaker_results = data.get(
        "speaker_results",
        st.session_state.speaker_results,
    )

    st.subheader("🎙️ SPEAKER RECOGNITION")

    st.metric(
        "TOTAL SPEAKERS",
        len(speaker_results),
    )

    for item in speaker_results:

        score = item.get("score", -1)

        if score >= 0:
            score_text = f"{score:.0f}%"
        else:
            score_text = "N/A"

        if item.get("name") == "Unknown":
            st.warning(
                f"🎤 {item.get('speaker_label', 'Speaker')} → **Unknown** "
                f"(similarity: {score_text})"
            )
        else:
            st.success(
                f"🎤 {item.get('speaker_label', 'Speaker')} → **{item.get('name')}** "
                f"(similarity: {score_text})"
            )

        reason = item.get("reason")
        if reason:
            st.caption(f"Analysis: {reason}")

    st.subheader("📝 SUMMARY")

    with st.container(border=True):
        st.write(
            data.get(
                "summary",
                "No summary available.",
            )
        )

    commitments = data.get(
        "commitments",
        [],
    )

    st.subheader("✅ TASKS & PROMISES")

    if commitments:

        for index, item in enumerate(
            commitments,
            start=1,
        ):

            with st.container(border=True):

                st.write(
                    f"### {index}. "
                    f"{item.get('type', 'Commitment')}"
                )

                st.write(
                    f"👤 **Speaker:** "
                    f"{item.get('speaker', 'Unknown')}"
                )

                st.write(
                    f"📌 **Action:** "
                    f"{item.get('task', 'Not specified')}"
                )

                st.write(
                    f"◈ **Deadline:** "
                    f"{item.get('deadline', 'Not specified')}"
                )

    else:
        st.info("No tasks or promises detected.")

    st.subheader("💡 DECISIONS")

    decisions = data.get(
        "decisions",
        [],
    )

    if decisions:
        for decision in decisions:
            st.write(f"• {decision}")
    else:
        st.info("No important decisions detected.")

    st.subheader("📥 EXPORT")

    report = [
        "NEON MEETING AI",
        "AI MEETING TO ACTION INTELLIGENCE",
        "=" * 55,
        "",
        "REFERENCE SPEAKER",
        "-" * 30,
        str(st.session_state.reference_speaker_name or "Unknown"),
        "",
        "SPEAKERS",
        "-" * 30,
    ]

    for item in speaker_results:
        score = item.get("score", -1)
        if score >= 0:
            report.append(
                f"{item.get('speaker_label', 'Speaker')} -> "
                f"{item.get('name', 'Unknown')} "
                f"(similarity: {score:.0f}%)"
            )
        else:
            report.append(
                f"{item.get('speaker_label', 'Speaker')} -> Unknown"
            )

    report.extend(
        [
            "",
            "SUMMARY",
            "-" * 30,
            data.get("summary", ""),
            "",
            "TASKS / PROMISES",
            "-" * 30,
        ]
    )

    for item in commitments:
        report.append(
            f"{item.get('speaker', 'Unknown')}: "
            f"{item.get('task', 'Not specified')} | "
            f"{item.get('deadline', 'Not specified')} | "
            f"{item.get('type', 'Commitment')}"
        )

    report.extend(
        [
            "",
            "DECISIONS",
            "-" * 30,
        ]
    )

    report.extend([str(x) for x in decisions])

    st.download_button(
        "⬇️ DOWNLOAD INTELLIGENCE REPORT",
        data="\n".join(report),
        file_name="neon_meeting_intelligence.txt",
        mime="text/plain",
        use_container_width=True,
    )
