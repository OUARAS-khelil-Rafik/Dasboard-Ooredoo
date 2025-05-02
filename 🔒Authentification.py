import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Authentification Ooredoo",
    page_icon="assets/ooredoo_logo2.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Suppression du sidebar de Streamlit
st.markdown("""
<style>
    [class="st-emotion-cache-1y9tyez edtmxes15"] {
        display: none !important;
    }
    [class="st-emotion-cache-169dgwr edtmxes15"] {
        display: none !important;
    }
    [data-testid="stSidebarNav"] > ul li:first-child {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Centrer le contenu
st.markdown("""
<style>
    .block-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100vh;
        padding-top: 0;
        padding-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)

# Thème personnalisé
st.markdown("""
<style>
body {
    background-color: #ffffff;
    color: #000000;
}
.dark-mode body {
    background-color: #121212;
    color: #ffffff;
}
.dark-mode .stButton>button {
    background-color: #e60000;
    color: #ffffff;
}
.stButton>button {
    background-color: #e60000;
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

# Logo + titre
col1, col2 = st.columns([1, 3])
with col1:
    st.image("assets/ooredoo_logo2.png", width=90)
with col2:
    st.markdown("<h1 style='text-align: center;'>Se connecter</h1>", unsafe_allow_html=True)

# Initialiser session
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None

# Redirection si déjà connecté
if st.session_state.authenticated:
    st.switch_page("pages/📊 Tableau de bord.py")

# Champs de connexion
username = st.text_input("Nom d'utilisateur", placeholder="Entrez votre nom d'utilisateur")
password = st.text_input("Mot de passe", type="password", placeholder="Entrez votre mot de passe")

# Bouton de connexion
if st.button("Se connecter"):
    if (username.lower() == "ooredoodz" and password == "Ooredoo@2025") or \
       (username.lower() == "admin" and password == "Admin@admin"):
        st.session_state.authenticated = True
        st.session_state.username = username
        st.success("Connexion réussie ! Redirection...")
        st.rerun()
    else:
        st.error("Nom d'utilisateur ou mot de passe incorrect.")