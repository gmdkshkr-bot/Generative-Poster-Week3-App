# app.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io
from datetime import datetime
import matplotlib.colors as mcolors

# --- (A) Color Palettes --- #
def random_palette(n=6, style="vivid", seed=None):
    if seed is not None:
        np.random.seed(seed)
    hues = np.linspace(0, 1, n, endpoint=False)
    np.random.shuffle(hues)
    colors = []
    for h in hues:
        s_range, l_range = {
            "pastel": ((0.3, 0.5), (0.7, 0.9)),
            "vivid": ((0.7, 1.0), (0.4, 0.6)),
            "neon": ((0.8, 1.0), (0.5, 0.7)),
            "earthy": ((0.4, 0.7), (0.3, 0.6)),
            "monochrome": ((0.0, 0.0), (0.3, 0.9)),
        }.get(style, ((0.3, 0.9), (0.3, 0.7)))
        s = np.random.uniform(*s_range)
        l = np.random.uniform(*l_range)
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h * 6) % 2 - 1))
        m = l - c / 2
        if h < 1/6: rgb = (c, x, 0)
        elif h < 2/6: rgb = (x, c, 0)
        elif h < 3/6: rgb = (0, c, x)
        elif h < 4/6: rgb = (0, x, c)
        elif h < 5/6: rgb = (x, 0, c)
        else: rgb = (c, 0, x)
        colors.append(tuple(np.clip(np.array(rgb) + m, 0, 1)))
    return colors

# --- (B) Blob Generator --- #
def generate_blob(center=(0, 0), radius=1, wobble=0.05, smoothness=8,
                  shape_mode="smooth", resolution=300, seed=None):
    if seed is not None:
        np.random.seed(seed)
    angles = np.linspace(0, 2*np.pi, resolution)
    if shape_mode == "spiky":
        noise = np.random.normal(0, wobble * 2, resolution)
    elif shape_mode == "square-ish":
        noise = wobble * np.sign(np.sin(4 * angles)) * np.random.uniform(0.5, 1.0)
    elif shape_mode == "star":
        noise = wobble * np.sin(5 * angles) * 2
    else:
        base_noise = np.random.normal(0, wobble, smoothness)
        noise = np.interp(np.linspace(0, smoothness, resolution), np.arange(smoothness), base_noise)
    r = radius * (1 + noise)
    x = center[0] + r * np.cos(angles)
    y = center[1] + r * np.sin(angles)
    if shape_mode == "ring":
        inner_r = radius * 0.6
        x_inner = center[0] + inner_r * np.cos(angles)
        y_inner = center[1] + inner_r * np.sin(angles)
        return np.concatenate([x, x_inner[::-1]]), np.concatenate([y, y_inner[::-1]])
    return x, y

# --- (C) Poster Drawing --- #
def draw_poster(n_blobs=8, wobble=0.05, seed=1, color_theme="vivid", shape_mode="smooth"):
    np.random.seed(seed)
    colors = random_palette(n_blobs, style=color_theme, seed=seed)
    fig, ax = plt.subplots(figsize=(6,6))
    ax.set_facecolor("black")
    ax.axis("off")
    for i, color in enumerate(colors):
        r = 0.25 * (1 + i * 0.12)
        angle = np.random.uniform(0, 2*np.pi)
        dist = np.random.uniform(0.1, 1.2)
        cx, cy = np.cos(angle) * dist, np.sin(angle) * dist
        x, y = generate_blob(center=(cx, cy), radius=r, wobble=wobble, shape_mode=shape_mode, seed=seed+i)
        ax.fill(x, y, color=color, alpha=0.7, lw=0.4)
    ax.text(-2, 2, "Generative Poster", fontsize=16, color="white", weight="bold", ha="left")
    ax.text(-2, 1.8, f"{color_theme.title()} / {shape_mode.title()}", fontsize=10, color="white")
    return fig

# --- Streamlit UI --- #
st.title("🎨 Generative Poster")

n_blobs = st.sidebar.slider("Number of Blobs", 3, 30, 8)
wobble = st.sidebar.slider("Wobble", 0.0, 0.2, 0.05, 0.01)
seed = st.sidebar.number_input("Seed", value=1, step=1)
color_theme = st.sidebar.selectbox("Color Theme", ["pastel", "vivid", "neon", "earthy", "monochrome"])
shape_mode = st.sidebar.selectbox("Shape Mode", ["smooth", "spiky", "square-ish", "ring", "star"])

fig = draw_poster(n_blobs=n_blobs, wobble=wobble, seed=seed, color_theme=color_theme, shape_mode=shape_mode)
st.pyplot(fig)

# Save as PNG
if st.button("💾 Save Poster"):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight", facecolor='black')
    buf.seek(0)
    filename = f"poster_seed{seed}_{color_theme}_{shape_mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    st.download_button("Download Poster", data=buf, file_name=filename, mime="image/png")
