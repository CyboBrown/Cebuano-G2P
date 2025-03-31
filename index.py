import streamlit as st
import requests
api = "https://storiatatts.agreeableground-aec2017e.australiaeast.azurecontainerapps.io/generate-audio"
from conversions import convert, convert_cpa, convert_ipa, synthesize_text
from meta import create_audio

st.write(""" 
# Cebuano Grapheme-to-Phoneme (G2P) Converter
""")

text = st.text_input(
    "Write any Cebuano text to generate its phonemic text equivalent",
    placeholder="Input text here"
)

generate_clicked = st.button("Generate", type="primary")

col1, col2 = st.columns(2)

if generate_clicked and text.strip():  # Ensure input isn't empty
    st.write("## Phonemic Form")
    st.write(convert(text))
    phonetic_text = convert(text)
    ptext1 = convert(text)
    ptext2 = convert(text)

    create_audio(text)

    st.write("## CPA Form")
    cpa_text = convert_cpa(ptext1)
    st.write(cpa_text)

    st.write("## IPA Form")
    ipa_text = convert_ipa(ptext2)
    st.write(ipa_text)
    synthesize_text(text, ipa_text)

    st.write("## Meta Cebuano-TTS")
    st.audio("output2.mpeg", format="audio/mpeg")
    st.write("## Google Cloud TTS with Phonemic Input")
    st.audio("output.mp3", format="audio/mp3")