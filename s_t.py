import os
import time
import glob
import streamlit as st

from PIL import Image
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

from gtts import gTTS
from googletrans import Translator


# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------

st.set_page_config(page_title="Traductor por voz", page_icon="🎤")

translator = Translator()

st.title("🎤 Traductor por Voz")
st.subheader("Habla y traduce automáticamente")


# -----------------------------
# IMAGEN
# -----------------------------

image = Image.open("OIG7.jpg")
st.image(image, width=300)


# -----------------------------
# SIDEBAR
# -----------------------------

with st.sidebar:
    st.header("Instrucciones")
    st.write(
        """
        1️⃣ Presiona el botón **Escuchar**  
        2️⃣ Cuando veas el indicador rojo 🔴 habla  
        3️⃣ Selecciona los idiomas  
        4️⃣ Convierte a audio
        """
    )


# -----------------------------
# BOTÓN DE ESCUCHA
# -----------------------------

st.write("Presiona el botón y habla")

stt_button = Button(label="🎤 Escuchar", width=300, height=60)

stt_button.js_on_event(
    "button_click",
    CustomJS(
        code="""
        var recognition = new webkitSpeechRecognition();

        recognition.continuous = false;
        recognition.interimResults = true;
        recognition.lang = "es-ES";

        document.dispatchEvent(
            new CustomEvent("LISTENING", {detail: "start"})
        );

        recognition.onresult = function(e){

            var value = "";

            for (var i = e.resultIndex; i < e.results.length; ++i){

                if (e.results[i].isFinal){
                    value += e.results[i][0].transcript;
                }

            }

            if(value != ""){
                document.dispatchEvent(
                    new CustomEvent("GET_TEXT", {detail:value})
                );
            }

        };

        recognition.onend = function(){

            document.dispatchEvent(
                new CustomEvent("LISTENING", {detail:"stop"})
            );

        };

        recognition.start();
"""
    ),
)


result = streamlit_bokeh_events(
    stt_button,
    events=["GET_TEXT", "LISTENING"],
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0,
)


# -----------------------------
# INDICADOR DE ESCUCHA
# -----------------------------

if result:

    if "LISTENING" in result:

        if result["LISTENING"] == "start":
            st.warning("🔴 Escuchando...")

        if result["LISTENING"] == "stop":
            st.success("✅ Reconocimiento terminado")


# -----------------------------
# TEXTO CAPTURADO
# -----------------------------

if result and "GET_TEXT" in result:

    text = result["GET_TEXT"]

    st.markdown("### Texto detectado:")
    st.write(text)


    # -----------------------------
    # SELECCIÓN DE IDIOMAS
    # -----------------------------

    languages = {
        "Inglés": "en",
        "Español": "es",
        "Bengali": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja",
    }

    in_lang = st.selectbox("Idioma de entrada", list(languages.keys()))
    out_lang = st.selectbox("Idioma de salida", list(languages.keys()))

    input_language = languages[in_lang]
    output_language = languages[out_lang]


    # -----------------------------
    # ACENTO
    # -----------------------------

    accents = {
        "Defecto": "com",
        "Español": "com.mx",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canada": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za",
    }

    accent = st.selectbox("Selecciona el acento", list(accents.keys()))
    tld = accents[accent]


    # -----------------------------
    # FUNCIÓN DE TRADUCCIÓN
    # -----------------------------

    def text_to_speech(text, input_language, output_language, tld):

        translation = translator.translate(
            text,
            src=input_language,
            dest=output_language
        )

        translated_text = translation.text

        tts = gTTS(
            translated_text,
            lang=output_language,
            tld=tld,
            slow=False
        )

        filename = text[:20]

        os.makedirs("temp", exist_ok=True)

        path = f"temp/{filename}.mp3"

        tts.save(path)

        return path, translated_text


    # -----------------------------
    # BOTÓN DE CONVERSIÓN
    # -----------------------------

    show_text = st.checkbox("Mostrar texto traducido")

    if st.button("🔊 Convertir a audio"):

        path, translated = text_to_speech(
            text,
            input_language,
            output_language,
            tld
        )

        audio = open(path, "rb").read()

        st.audio(audio)

        if show_text:
            st.markdown("### Traducción:")
            st.write(translated)


# -----------------------------
# LIMPIAR ARCHIVOS
# -----------------------------

def remove_old_files(days):

    mp3_files = glob.glob("temp/*.mp3")

    now = time.time()

    for f in mp3_files:

        if os.stat(f).st_mtime < now - days * 86400:
            os.remove(f)


remove_old_files(7)



        
    


