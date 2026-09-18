
import os
import json
import base64
import tempfile
from pathlib import Path
from datetime import datetime

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

# Persistent local storage:
# speaker_profiles/
#   profiles.json
#   audio/
#       <speaker files>
PROFILE_DIR = APP_DIR / "speaker_profiles"
AUDIO_DIR = PROFILE_DIR / "audio"
PROFILE_DB = PROFILE_DIR / "profiles.json"

PROFILE_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# PREMIUM GLASS UI — DESIGN PRESERVED
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
# SECRETS
# ============================================================

def get_secret(name: str):
    value = os.environ.get(name)
    if value:
        return value

    try:
        value = st.secrets[name]
        return value
    except Exception:
        return None


GEMINI_API_KEY = get_secret("GEMINI_API_KEY")
AUTH_USERNAME = get_secret("AUTH_USERNAME") or "admin"
AUTH_PASSWORD = get_secret("AUTH_PASSWORD") or "admin123"


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "authenticated": False,
    "page": 1,
    "meeting_data": None,
    "audio_name": None,
    "speaker_results": [],
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


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
        st.caption(
            "Enter your credentials to access the meeting intelligence system."
        )

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

        if st.button(
            "🔓 LOGIN",
            type="primary",
            use_container_width=True,
        ):
            if (
                username == AUTH_USERNAME
                and password == AUTH_PASSWORD
            ):
                st.session_state.authenticated = True
                st.session_state.page = 1
                st.rerun()
            else:
                st.error("❌ Invalid username or password.")

    st.caption(
        "🔒 Secure access • Speaker Recognition • Meeting Intelligence"
    )
    st.stop()


# ============================================================
# PERSISTENT SPEAKER DATABASE
# ============================================================

def load_profiles():
    """
    Returns:
        {
            "Venkatesh": {
                "audio_file": "venkatesh_abc123.wav",
                "original_name": "venkatesh.wav",
                "mime_type": "audio/wav",
                "created_at": "2026-09-19T03:00:00"
            }
        }
    """
    if not PROFILE_DB.exists():
        return {}

    try:
        data = json.loads(
            PROFILE_DB.read_text(encoding="utf-8")
        )

        if not isinstance(data, dict):
            return {}

        # Clean invalid entries safely.
        cleaned = {}
        for name, profile in data.items():
            if isinstance(profile, dict):
                audio_file = profile.get("audio_file")
                if audio_file:
                    cleaned[str(name)] = profile

        return cleaned

    except Exception:
        return {}


def save_profiles(profiles):
    PROFILE_DB.write_text(
        json.dumps(
            profiles,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def safe_filename(value: str) -> str:
    allowed = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789"
        "-_"
    )

    cleaned = "".join(
        c if c in allowed else "_"
        for c in value
    )

    return cleaned.strip("_") or "speaker"


def delete_profile(name: str):
    profiles = load_profiles()
    profile = profiles.pop(name, None)

    if profile:
        audio_file = profile.get("audio_file")

        if audio_file:
            audio_path = AUDIO_DIR / Path(audio_file).name

            try:
                if audio_path.exists():
                    audio_path.unlink()
            except OSError:
                pass

    save_profiles(profiles)


def store_reference_audio(
    speaker_name: str,
    uploaded_file,
):
    """
    Stores the RAW reference audio locally.

    This is intentionally different from the old version:
    we do NOT create an embedding and we do NOT need
    pyannote, SpeechBrain, Torch, or Hugging Face.
    """

    original_name = Path(uploaded_file.name).name
    extension = Path(original_name).suffix.lower()

    if not extension:
        extension = ".wav"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    clean = safe_filename(speaker_name)

    filename = (
        f"{clean}_{timestamp}{extension}"
    )

    destination = AUDIO_DIR / filename

    data = uploaded_file.getvalue()

    if not data:
        raise RuntimeError(
            "The uploaded reference audio is empty."
        )

    destination.write_bytes(data)

    return filename, original_name, data


def reference_path(profile):
    filename = profile.get("audio_file", "")
    if not filename:
        return None

    path = AUDIO_DIR / Path(filename).name

    # Prevent accidental path traversal.
    try:
        path.resolve().relative_to(
            AUDIO_DIR.resolve()
        )
    except ValueError:
        return None

    return path


# ============================================================
# AUDIO HELPERS
# ============================================================

def mime_for_extension(extension: str) -> str:
    mapping = {
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".mp4": "audio/mp4",
        ".webm": "audio/webm",
        ".ogg": "audio/ogg",
        ".oga": "audio/ogg",
        ".flac": "audio/flac",
    }

    return mapping.get(
        extension.lower(),
        "application/octet-stream",
    )


def save_uploaded_audio(uploaded, suffix=".wav"):
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as f:
        f.write(uploaded.getbuffer())
        return f.name


def clean_json_text(text: str) -> str:
    text = text.strip()

    if text.startswith("```json"):
        text = text[7:].strip()

    elif text.startswith("```"):
        text = text[3:].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    return text


# ============================================================
# SIDEBAR
# ============================================================

profiles = load_profiles()

with st.sidebar:
    st.markdown("## 💠 NEON MEETING AI")
    st.caption("AI Meeting to Action Intelligence")

    st.divider()

    if st.button(
        "🏠 HOME",
        use_container_width=True,
    ):
        st.session_state.page = 1
        st.rerun()

    if st.button(
        "🎙️ VOICE PROFILES",
        use_container_width=True,
    ):
        st.session_state.page = 2
        st.rerun()

    if st.button(
        "🎧 ANALYZE MEETING",
        use_container_width=True,
    ):
        st.session_state.page = 3
        st.rerun()

    st.divider()

    st.write("### 👤 SESSION")
    st.success("Logged in")

    st.metric(
        "Registered Speakers",
        len(profiles),
    )

    if st.button(
        "🚪 LOGOUT",
        use_container_width=True,
    ):
        st.session_state.authenticated = False
        st.session_state.meeting_data = None
        st.session_state.speaker_results = []
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
# PAGE 2 — VOICE PROFILES
# ============================================================

elif st.session_state.page == 2:

    st.title("🎙️ VOICE PROFILE")

    st.caption(
        "Add one reference audio for each speaker. "
        "The raw reference audio is stored locally and reused "
        "for future meeting analysis."
    )

    if not GEMINI_API_KEY:
        st.warning(
            "GEMINI_API_KEY is not configured. "
            "Add it to Streamlit Secrets."
        )

    st.markdown(
        '<div class="glass">',
        unsafe_allow_html=True,
    )

    name = st.text_input(
        "SPEAKER NAME",
        placeholder="Example: Venkatesh",
        key="reference_speaker_name",
    )

    reference_file = st.file_uploader(
        "UPLOAD REFERENCE VOICE",
        type=[
            "wav",
            "mp3",
            "m4a",
            "mp4",
            "webm",
            "ogg",
            "flac",
        ],
        accept_multiple_files=False,
        key="reference_voice_upload",
        help=(
            "Upload one clear reference recording for this speaker. "
            "About 10–30 seconds of natural speech is recommended."
        ),
    )

    if reference_file:
        st.audio(reference_file)

    if reference_file and st.button(
        "💾 ADD SPEAKER",
        type="primary",
        use_container_width=True,
    ):
        try:
            clean_name = name.strip()

            if len(clean_name) < 2:
                raise RuntimeError(
                    "Please enter a valid speaker name."
                )

            profiles = load_profiles()

            # Case-insensitive duplicate protection.
            existing = {
                key.casefold(): key
                for key in profiles.keys()
            }

            if clean_name.casefold() in existing:
                raise RuntimeError(
                    f"{existing[clean_name.casefold()]} already exists. "
                    "Delete the old profile before adding it again."
                )

            (
                stored_filename,
                original_name,
                audio_bytes,
            ) = store_reference_audio(
                clean_name,
                reference_file,
            )

            profiles[clean_name] = {
                "audio_file": stored_filename,
                "original_name": original_name,
                "mime_type": mime_for_extension(
                    Path(stored_filename).suffix
                ),
                "created_at": datetime.now().isoformat(
                    timespec="seconds"
                ),
                "storage": "local_file",
            }

            save_profiles(profiles)

            st.success(
                f"✅ {clean_name} reference voice stored successfully."
            )

            st.info(
                f"Stored file: {original_name} "
                f"({len(audio_bytes) / 1024:.1f} KB)"
            )

            st.rerun()

        except Exception as exc:
            st.error(
                f"❌ Could not store speaker: {exc}"
            )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    st.subheader("👥 REGISTERED SPEAKERS")

    profiles = load_profiles()

    if not profiles:
        st.info(
            "No speaker profiles registered yet."
        )

    else:
        for speaker_name, profile in profiles.items():

            path = reference_path(profile)

            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.write(
                        f"### 🎙️ {speaker_name}"
                    )

                    st.caption(
                        "Reference: "
                        + profile.get(
                            "original_name",
                            profile.get(
                                "audio_file",
                                "Unknown",
                            ),
                        )
                    )

                    st.caption(
                        "Registered: "
                        + profile.get(
                            "created_at",
                            "Unknown",
                        )
                    )

                    if path and path.exists():
                        try:
                            st.audio(
                                path.read_bytes(),
                                format=profile.get(
                                    "mime_type",
                                    "audio/wav",
                                ),
                            )
                        except Exception:
                            pass
                    else:
                        st.error(
                            "Reference audio file is missing."
                        )

                with col2:
                    if path and path.exists():
                        st.success("ACTIVE")
                    else:
                        st.error("MISSING")

                with col3:
                    if st.button(
                        "🗑️ DELETE",
                        key=f"delete_{safe_filename(speaker_name)}",
                    ):
                        delete_profile(speaker_name)
                        st.rerun()

    st.divider()

    st.warning(
        "Voice recordings are biometric information. "
        "Get the speaker's consent before storing and using "
        "a reference voice."
    )


# ============================================================
# PAGE 3 — MEETING ANALYSIS
# ============================================================

elif st.session_state.page == 3:

    st.title("🎧 MEETING ANALYSIS")

    profiles = load_profiles()

    if not profiles:
        st.warning(
            "No voice profiles exist yet. "
            "Register at least one speaker first."
        )

        if st.button(
            "🎙️ GO TO VOICE REGISTRATION",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.page = 2
            st.rerun()

        st.stop()

    valid_profiles = {}

    for speaker_name, profile in profiles.items():
        path = reference_path(profile)

        if path and path.exists():
            valid_profiles[speaker_name] = profile

    if not valid_profiles:
        st.error(
            "All stored speaker reference files are missing. "
            "Please register the speakers again."
        )
        st.stop()

    st.caption(
        f"{len(valid_profiles)} registered speaker profile(s) "
        "available for Gemini voice comparison."
    )

    st.markdown(
        '<div class="glass">',
        unsafe_allow_html=True,
    )

    st.write("### 👥 REFERENCE SPEAKERS")

    for speaker_name, profile in valid_profiles.items():
        st.write(
            f"🎙️ **{speaker_name}** → "
            f"{profile.get('original_name', profile.get('audio_file', 'audio'))}"
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    audio = st.file_uploader(
        "UPLOAD MEETING RECORDING",
        type=[
            "mp3",
            "wav",
            "m4a",
            "mp4",
            "webm",
            "ogg",
            "flac",
        ],
        accept_multiple_files=False,
        key="meeting_audio_upload",
    )

    if audio:
        st.audio(audio)

    if audio and st.button(
        "🧠 ANALYZE MEETING",
        type="primary",
        use_container_width=True,
    ):

        if not GEMINI_API_KEY:
            st.error(
                "❌ GEMINI_API_KEY is missing. "
                "Add it to Streamlit Secrets."
            )
            st.stop()

        temp_meeting = None
        uploaded_gemini_files = []

        try:
            extension = (
                Path(audio.name).suffix.lower()
                or ".mp3"
            )

            temp_meeting = save_uploaded_audio(
                audio,
                extension,
            )

            with st.status(
                "Running Gemini speaker comparison and meeting intelligence...",
                expanded=True,
            ) as status:

                st.write(
                    "1/4 Preparing registered speaker references..."
                )

                client = genai.Client(
                    api_key=GEMINI_API_KEY
                )

                # ------------------------------------------------
                # Upload ONE reference audio per registered speaker.
                # The text marker immediately before each audio
                # makes the speaker/audio relationship explicit.
                # ------------------------------------------------

                gemini_inputs = [
                    {
                        "type": "text",
                        "text": (
                            "You will receive reference voice recordings "
                            "followed by one meeting recording."
                        ),
                    }
                ]

                reference_names = []

                for index, (
                    speaker_name,
                    profile,
                ) in enumerate(
                    valid_profiles.items(),
                    start=1,
                ):

                    path = reference_path(profile)

                    if not path or not path.exists():
                        continue

                    st.write(
                        f"Uploading reference {index}: "
                        f"{speaker_name}"
                    )

                    ref_uploaded = client.files.upload(
                        file=str(path)
                    )

                    uploaded_gemini_files.append(
                        ref_uploaded
                    )

                    reference_names.append(
                        speaker_name
                    )

                    gemini_inputs.append(
                        {
                            "type": "text",
                            "text": (
                                f"REFERENCE AUDIO {index}: "
                                f"{speaker_name}"
                            ),
                        }
                    )

                    gemini_inputs.append(
                        {
                            "type": "audio",
                            "uri": ref_uploaded.uri,
                            "mime_type": (
                                ref_uploaded.mime_type
                                or profile.get(
                                    "mime_type",
                                    "audio/wav",
                                )
                            ),
                        }
                    )

                if not reference_names:
                    raise RuntimeError(
                        "No valid reference audio files were found."
                    )

                st.write(
                    "2/4 Uploading meeting audio..."
                )

                meeting_uploaded = client.files.upload(
                    file=temp_meeting
                )

                uploaded_gemini_files.append(
                    meeting_uploaded
                )

                gemini_inputs.extend(
                    [
                        {
                            "type": "text",
                            "text": "MEETING AUDIO:",
                        },
                        {
                            "type": "audio",
                            "uri": meeting_uploaded.uri,
                            "mime_type": (
                                meeting_uploaded.mime_type
                                or mime_for_extension(
                                    extension
                                )
                            ),
                        },
                    ]
                )

                reference_list = "\n".join(
                    f"{i}. {name}"
                    for i, name in enumerate(
                        reference_names,
                        start=1,
                    )
                )

                prompt = f"""
You are an AI Meeting to Action Intelligence Agent.

You are given:
1. One reference voice recording for each registered speaker.
2. One meeting recording containing potentially multiple speakers.

REGISTERED REFERENCE SPEAKERS:
{reference_list}

IMPORTANT VOICE-MATCHING RULES:
- Each reference audio belongs ONLY to the registered speaker named immediately before it.
- Compare voices acoustically. Do not identify a person from the words they say, topic, name mentioned in the meeting, or contextual clues alone.
- A meeting speaker can be matched to a registered speaker only when the voice evidence is reasonably strong.
- If the evidence is insufficient, use "Unknown".
- Do not invent identities.
- One registered person should normally map to at most one distinct meeting speaker.
- The meeting may contain speakers who are not registered.
- If multiple registered references are similar, explain the uncertainty rather than inventing a match.
- Give a confidence value from 0 to 1.

Your tasks:

A) Identify distinct speakers in the meeting.
B) Match each meeting speaker to one of the registered names or Unknown.
C) Provide a concise reason for each match.
D) Analyze the meeting for:
   - concise summary
   - tasks
   - promises / commitments
   - deadlines
   - important decisions

Return ONLY valid JSON.

Use exactly this structure:

{{
  "speaker_results": [
    {{
      "speaker_label": "Speaker 1",
      "name": "Venkatesh",
      "confidence": 0.91,
      "reason": "Voice characteristics are consistent with the Venkatesh reference recording."
    }}
  ],
  "summary": "Short meeting summary",
  "commitments": [
    {{
      "speaker": "Venkatesh",
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
- Use "Unknown" when a meeting speaker cannot be reliably matched.
- Use "Not specified" when no deadline is mentioned.
- Keep the summary concise.
- Do not invent tasks, deadlines, decisions, or identities.
- Return valid JSON only.
"""

                gemini_inputs.insert(
                    1,
                    {
                        "type": "text",
                        "text": prompt,
                    },
                )

                st.write(
                    "3/4 Comparing meeting speakers "
                    "with registered reference voices..."
                )

                interaction = client.interactions.create(
                    model="gemini-3.6-flash",
                    input=gemini_inputs,
                )

                result_text = clean_json_text(
                    interaction.output_text
                )

                meeting_data = json.loads(
                    result_text
                )

                speaker_results = meeting_data.get(
                    "speaker_results",
                    [],
                )

                if not isinstance(
                    speaker_results,
                    list,
                ):
                    speaker_results = []

                meeting_data.setdefault(
                    "summary",
                    "No summary available.",
                )

                meeting_data.setdefault(
                    "commitments",
                    [],
                )

                meeting_data.setdefault(
                    "decisions",
                    [],
                )

                meeting_data["speaker_results"] = (
                    speaker_results
                )

                st.session_state.speaker_results = (
                    speaker_results
                )

                st.session_state.meeting_data = (
                    meeting_data
                )

                st.session_state.audio_name = (
                    audio.name
                )

                st.write(
                    "4/4 Finalizing intelligence report..."
                )

                status.update(
                    label="✅ Meeting analysis complete",
                    state="complete",
                )

            st.rerun()

        except json.JSONDecodeError:
            st.error(
                "❌ Gemini returned invalid JSON. "
                "Please try the meeting again."
            )

        except Exception as exc:
            st.error(
                f"❌ Analysis failed: {exc}"
            )

        finally:
            if temp_meeting:
                try:
                    os.remove(temp_meeting)
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

    for index, item in enumerate(
        speaker_results,
        start=1,
    ):

        label = item.get(
            "speaker_label",
            f"Speaker {index}",
        )

        name = item.get(
            "name",
            "Unknown",
        )

        confidence = item.get(
            "confidence",
            0,
        )

        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.0

        confidence_text = (
            f"{confidence:.2f}"
        )

        if name == "Unknown":
            st.warning(
                f"🎤 {label} → **Unknown** "
                f"(confidence: {confidence_text})"
            )
        else:
            st.success(
                f"🎤 {label} → **{name}** "
                f"(confidence: {confidence_text})"
            )

        reason = item.get("reason")

        if reason:
            st.caption(
                f"Reason: {reason}"
            )

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
        st.info(
            "No tasks or promises detected."
        )

    st.subheader("💡 DECISIONS")

    decisions = data.get(
        "decisions",
        [],
    )

    if decisions:
        for decision in decisions:
            st.write(
                f"• {decision}"
            )
    else:
        st.info(
            "No important decisions detected."
        )

    st.subheader("📥 EXPORT")

    report = [
        "NEON MEETING AI",
        "AI MEETING TO ACTION INTELLIGENCE",
        "=" * 55,
        "",
        "SPEAKERS",
        "-" * 30,
    ]

    for item in speaker_results:

        label = item.get(
            "speaker_label",
            "Unknown",
        )

        name = item.get(
            "name",
            "Unknown",
        )

        confidence = item.get(
            "confidence",
            0,
        )

        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.0

        report.append(
            f"{label} -> {name} "
            f"(confidence: {confidence:.2f})"
        )

        if item.get("reason"):
            report.append(
                f"Reason: {item['reason']}"
            )

    report.extend(
        [
            "",
            "SUMMARY",
            "-" * 30,
            str(data.get("summary", "")),
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

    report.extend(
        [str(x) for x in decisions]
    )

    st.download_button(
        "⬇️ DOWNLOAD INTELLIGENCE REPORT",
        data="\n".join(report),
        file_name="neon_meeting_intelligence.txt",
        mime="text/plain",
        use_container_width=True,
    )
