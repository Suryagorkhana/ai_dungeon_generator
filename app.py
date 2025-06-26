import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer
import pathlib, base64, datetime, time

# --- Paths ---
IMAGE_PATH = pathlib.Path("images/back.png")
LOADING_IMAGE_PATH = pathlib.Path("images/type.gif")
WELCOME_GIF = pathlib.Path("images/welcome.gif")
WELCOME_STATIC = pathlib.Path("images/back.png")
THANKYOU_GIF = pathlib.Path("images/thankyou.gif")

# --- Encode image to base64 ---
def encode_image_to_base64(img_path):
    with open(img_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = img_path.suffix[1:]
    return f"data:image/{ext};base64,{data}"

# --- Page Config ---
st.set_page_config("AI Dungeon Story Generator", "🧙", layout="centered")

# --- Show Welcome GIF once ---
if "welcome_played" not in st.session_state:
    st.session_state.welcome_played = True
    welcome_gif = encode_image_to_base64(WELCOME_GIF)
    st.markdown(f"""
        <div style="text-align:center; margin-top: 100px;">
            <img src="{welcome_gif}" width="400"><br>
            <h2 style="color:blue; font-family:Quicksand; margin-top:20px;">
                ✨ Welcome To The AI Dungeon Story Generator...
            </h2>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(3)
    st.rerun()

# --- Theme Selection ---
theme_display = st.sidebar.selectbox("🎨 Select Theme", [
    "🌞 Light", "🌚 Dark", "🌇 Solarized", "🌌 Midnight", "🍬 Pastel"
])
theme = theme_display.split(" ")[1]

# --- Theme Styles ---
themes = {
    "Light": {
        "bg_overlay": "rgba(255, 255, 255, 0.5)",
        "main_bg": "rgba(255, 255, 255, 0.95)",
        "font_color": "#000000",
        "button_gradient": "linear-gradient(to right, #7c3aed, #4f46e5)",
        "card_bg": "#ffffff",
        "hover_shadow": "#a855f7"
    },
    "Dark": {
        "bg_overlay": "rgba(0, 0, 0, 0.7)",
        "main_bg": "rgba(30, 30, 30, 0.85)",
        "font_color": "#ffffff",
        "button_gradient": "linear-gradient(to right, #06b6d4, #3b82f6)",
        "card_bg": "#1e1e1e",
        "hover_shadow": "#06b6d4"
    },
    "Solarized": {
        "bg_overlay": "rgba(253, 246, 227, 0.6)",
        "main_bg": "#fdf6e3",
        "font_color": "#586e75",
        "button_gradient": "linear-gradient(to right, #b58900, #cb4b16)",
        "card_bg": "#eee8d5",
        "hover_shadow": "#b58900"
    },
    "Midnight": {
        "bg_overlay": "rgba(25, 25, 112, 0.6)",
        "main_bg": "#0f172a",
        "font_color": "#f8fafc",
        "button_gradient": "linear-gradient(to right, #1e3a8a, #4f46e5)",
        "card_bg": "#1e293b",
        "hover_shadow": "#1e3a8a"
    },
    "Pastel": {
        "bg_overlay": "rgba(255, 240, 245, 0.6)",
        "main_bg": "#fef3f3",
        "font_color": "#5a5a5a",
        "button_gradient": "linear-gradient(to right, #fca5a5, #f9a8d4)",
        "card_bg": "#fff1f2",
        "hover_shadow": "#f472b6"
    }
}
cfg = themes[theme]
bg_url = encode_image_to_base64(IMAGE_PATH)

# --- CSS Styling ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap');
html, body, .stApp {{
    font-family: 'Quicksand', sans-serif;
    color: {cfg["font_color"]};
    background-image: url("{bg_url}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
.overlay {{
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    backdrop-filter: blur(6px);
    background-color: {cfg["bg_overlay"]};
    z-index: -1;
}}
.block-container {{
    background: {cfg["main_bg"]};
    padding: 2rem;
    border-radius: 20px;
}}
.stButton > button {{
    background: {cfg["button_gradient"]};
    color: white;
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
    font-weight: bold;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}}
.stButton > button:hover {{
    box-shadow: 0 0 12px {cfg["hover_shadow"]}, 0 0 20px {cfg["hover_shadow"]};
    transform: scale(1.03);
}}
textarea, select, input, .stSlider, .stRadio {{
    border-radius: 8px;
    border: 2px solid {cfg["hover_shadow"]};
    box-shadow: 0 0 10px {cfg["hover_shadow"]};
    transition: all 0.3s ease;
}}
</style>
<div class="overlay"></div>
""", unsafe_allow_html=True)

# --- Welcome Static Screen ---
if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    st.markdown("## 🧙 Welcome to AI Dungeon Story Generator")
    st.image(str(WELCOME_STATIC), use_container_width=True)
    if st.button("🚀 Start Creating"):
        st.session_state.started = True
    else:
        st.stop()

# --- Sidebar Settings ---
st.sidebar.header("📚 Settings")
genre = st.sidebar.selectbox("Genre", ["Fantasy", "Mystery", "Sci-Fi", "Horror", "Romance"])
num_versions = st.sidebar.slider("Versions", 1, 5, 2)

# --- Prompt Input ---
st.markdown("### ✍️ ENTER YOUR STORY")
prompt = st.text_area("Start your story below:", "Once upon a time in a faraway kingdom...")

# --- Load Model ---
MODEL = "gpt2"

@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    tokenizer.pad_token = tokenizer.eos_token  # Fix: set pad_token
    model = AutoModelForCausalLM.from_pretrained(MODEL)
    return model, tokenizer

model, tokenizer = load_model()

# --- Generate Button ---
if st.button("✨ Generate Story"):
    try:
        st.image(str(LOADING_IMAGE_PATH), caption="✨ Generating your story...", use_container_width=True)
    except Exception:
        st.warning("🖼️ Loading animation not found. Skipping...")

    with st.spinner("Please wait while your adventure unfolds..."):
        full_prompt = f"[Genre: {genre}] {prompt.strip()}"
        inputs = tokenizer(full_prompt, return_tensors="pt", padding=True)
        input_ids = inputs["input_ids"]
        attention_mask = inputs["attention_mask"]

        outputs = model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_length=300,
            do_sample=True,
            temperature=0.9,
            top_p=0.95,
            num_return_sequences=num_versions,
            pad_token_id=tokenizer.eos_token_id
        )

        st.subheader("📖 Generated Stories")
        all_text = []
        for i, output in enumerate(outputs, 1):
            story = tokenizer.decode(output, skip_special_tokens=True).replace(prompt, "").strip()
            st.markdown(f"### ✨ Version {i}")
            st.markdown(
                f"<div style='background:{cfg['card_bg']}; padding:1rem; border-radius:10px; box-shadow: 0 0 10px {cfg['hover_shadow']}'><p>{story}</p></div>",
                unsafe_allow_html=True
            )
            all_text.append(f"--- Version {i} ---\n{story}")

        if st.button("💾 Save All Versions"):
            fname = f"story_{datetime.datetime.now():%Y%m%d-%H%M%S}.txt"
            with open(fname, "w", encoding="utf-8") as f:
                f.write(f"Prompt: {prompt}\nGenre: {genre}\n\n")
                f.write("\n\n".join(all_text))
            st.success(f"Saved as `{fname}` ✅")

# --- Exit ---
if st.button("👋 Exit"):
    thankyou_gif = encode_image_to_base64(THANKYOU_GIF)
    st.markdown(f"""
        <div style="text-align:center; margin-top: 50px;">
            <img src="{thankyou_gif}" width="400">
            <h2>Thanks for using AI Dungeon!</h2>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(3)
    st.stop()
