import streamlit as st
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt

# import your poster code here
from poster import generate_poster, STYLE_PRESETS

st.set_page_config(layout="centered", page_title="Generative Poster")

st.title("🎨 Generative Poster UI")
st.write("Select style presets and generate posters instantly.")

# --- UI Controls ---
style = st.selectbox(
    "Poster Style",
    list(STYLE_PRESETS.keys()) + ["Custom"]
)

seed = st.number_input("Random Seed (optional)", min_value=0, step=1)
use_seed = st.checkbox("Use seed?", value=True)

n_layers = st.slider("Number of Layers", 3, 20, 8)
wobble_min, wobble_max = st.slider("Wobble Range", 0.01, 0.4, (0.05, 0.25))
alpha_min, alpha_max = st.slider("Alpha Range", 0.1, 1.0, (0.25, 0.6))

background = st.color_picker("Background Color", "#fafafe")
background_rgb = tuple(int(background.lstrip("#")[i:i+2], 16)/255 for i in (0,2,4))

# --- Generate Button ---
if st.button("Generate Poster"):
    
    fig, ax = generate_poster(
        style=None if style=="Custom" else style,
        seed=seed if use_seed else None,
        n_layers=n_layers,
        wobble_range=(wobble_min, wobble_max),
        alpha_range=(alpha_min, alpha_max),
        background=background_rgb,
    )

    st.pyplot(fig)

    # --- File Export ---
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)

    st.download_button(
        label="Download Poster PNG",
        data=buf,
        file_name=f"poster_{style}.png",
        mime="image/png",
    )
