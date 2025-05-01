import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Authentification Ooredoo",
    page_icon=":red_circle:",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Suppression du header par défaut de Streamlit
st.markdown("""
<style>
    .stAppDeployButton {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Centrer tout le contenu de la page
center_content_style = """
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
"""
st.markdown(center_content_style, unsafe_allow_html=True)

# Fonction pour gérer les thèmes (dark mode et light mode)
def set_theme():
    st.markdown(
        """
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
        """,
        unsafe_allow_html=True,
    )

# Appel de la fonction pour appliquer les styles
set_theme()

# Affichage du logo et titre de l'application sur la même ligne
col1, col2 = st.columns([1, 3])
with col1:
    st.image("assets/ooredoo_logo.png", width=90)
with col2:
    st.markdown("<h1 style='text-align: center;'>Se connecter</h1>", unsafe_allow_html=True)

# Champs pour l'utilisateur et le mot de passe
username = st.text_input("Nom d'utilisateur", placeholder="Entrez votre nom d'utilisateur")
password = st.text_input("Mot de passe", type="password", placeholder="Entrez votre mot de passe")

# Bouton de connexion
if st.button("Se connecter"):
    # Vérification des identifiants
    if (username == "Ooredoodz2025" and password == "Ooredoo@2025") or \
       (username == "Admin" and password == "Admin@admin"):
        st.success("Connexion réussie ! Bienvenue sur le tableau de bord Ooredoo.")
    else:
        st.error("Nom d'utilisateur ou mot de passe incorrect.")