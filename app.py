import os
import streamlit as st
import base64
from openai import OpenAI
import openai
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
from streamlit_drawable_canvas import st_canvas

Expert = " "
profile_imgenh = " "

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró en la ruta especificada."

st.set_page_config(page_title="🎨 Tablero Inteligente", layout="centered", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600&display=swap');

html, body, .stApp {
    background: linear-gradient(to right, #fceabb, #f8b500);
    color: #333;
    font-family: 'Quicksand', sans-serif;
    text-align: center;
}

h1, h2, h3, .stTitle, .stHeader {
    color: #d9480f;
    text-align: center;
}

.stButton>button {
    background-color: #ff914d;
    color: white;
    border-radius: 10px;
    font-weight: bold;
    font-size: 16px;
    padding: 0.5em 1.2em;
}

.stSidebar {
    background-color: #fff3e0;
    font-family: 'Quicksand', sans-serif;
    color: #5d4037;
}

.stTextInput>div>input {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 Tablero Inteligente")
with st.sidebar:
    st.subheader("📝 Acerca de:")
    st.write("Esta aplicación demuestra cómo una IA puede interpretar bocetos simples en segundos.")
    st.write("Solo dibuja en el lienzo y deja que la magia ocurra ✨")

st.subheader("✏️ Dibuja tu boceto en el panel y presiona 'Analiza la imagen' para descubrir qué representa")

drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('🖌️ Ancho de línea', 1, 30, 5)
stroke_color = "#000000"
bg_color = '#FFFFFF'

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

ke = st.text_input('🔐 Ingresa tu clave de API')
os.environ['OPENAI_API_KEY'] = ke
api_key = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=api_key)

analyze_button = st.button("🔍 Analiza la imagen", type="primary")

if canvas_result.image_data is not None and api_key and analyze_button:
    with st.spinner("🔎 Analizando tu dibujo..."):
        input_numpy_array = np.array(canvas_result.image_data)
        input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
        input_image.save('img.png')
        base64_image = encode_image_to_base64("img.png")

        prompt_text = "Describe brevemente en español lo que ves en esta imagen."

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                        },
                    },
                ],
            }
        ]

        try:
            full_response = ""
            message_placeholder = st.empty()
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=500,
            )
            if response.choices[0].message.content is not None:
                full_response += response.choices[0].message.content
                message_placeholder.markdown("🎨 **Interpretación de la IA:**\n\n" + full_response)
            if Expert == profile_imgenh:
                st.session_state.mi_respuesta = response.choices[0].message.content
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
else:
    if not api_key:
        st.warning("🔐 Por favor ingresa tu clave de API.")
