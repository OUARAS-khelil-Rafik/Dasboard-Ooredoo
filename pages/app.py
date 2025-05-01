import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Ooredoo",
    page_icon=":red_circle:",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Suppression du header, footer et sidebar de Streamlit
st.markdown("""
<style>
    /* Supprimer le bouton Deploy */
    .stAppDeployButton {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)


st.title("Bienvenue dans le Dashboard Ooredoo")
st.write("Contenu principal ici...")
