import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Authentification Ooredoo",
    page_icon=":red_circle:",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Fonction pour gérer les thèmes (dark mode et light mode)
def set_theme(dark_mode):
    if dark_mode:
        st.markdown(
            """
            <style>
            body {
                background-color: #121212;
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
    else:
        st.markdown(
            """
            <style>
            body {
                background-color: #ffffff;
                color: #000000;
            }
            .stButton>button {
                background-color: #e60000;
                color: #ffffff;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

# Gestion du mode sombre ou clair
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# Bouton pour basculer entre les modes
toggle_button = st.button("🌙 Mode Sombre" if not st.session_state.dark_mode else "☀️ Mode Clair")

if toggle_button:
    st.session_state.dark_mode = not st.session_state.dark_mode

# Appel de la fonction pour appliquer les styles
set_theme(st.session_state.dark_mode)

# Affichage du logo
st.image("assets/ooredoo_logo.png", width=200)

# Titre de l'application
st.title("Authentification Ooredoo")

# Formulaire d'authentification
st.subheader("Veuillez vous connecter")

# Champs pour l'utilisateur et le mot de passe
username = st.text_input("Nom d'utilisateur", placeholder="Entrez votre nom d'utilisateur")
password = st.text_input("Mot de passe", type="password", placeholder="Entrez votre mot de passe")

# Bouton de connexion
if st.button("Se connecter"):
    # Vérification des identifiants (insensible à la casse pour le nom d'utilisateur)
    if (username.lower() == "ooredoodz2025".lower() and password == "Ooredoo@2025") or \
       (username.lower() == "admin".lower() and password == "Admin@admin"):
        st.success("Connexion réussie ! Bienvenue sur le tableau de bord Ooredoo.")
    else:
        st.error("Nom d'utilisateur ou mot de passe incorrect.")