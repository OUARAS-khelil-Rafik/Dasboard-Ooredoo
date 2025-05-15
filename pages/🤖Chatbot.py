import streamlit as st
import pandas as pd
import altair as alt
import locale
locale.setlocale(locale.LC_TIME, 'French_France.1252')

#---------------------------- Variables ---------------------------

usernames = st.secrets["usernames"]
passwords = st.secrets["passwords"]

#--------------------------------------------------------------------------------------------------

# Configuration de la page
st.set_page_config(page_title="Commentaires",
                   page_icon="assets/ooredoo_logo2.png",  # Ensure this path is correct
                   layout="wide"
)

st.markdown("""
<style>
    /* Masque uniquement le premier élément li */
    [data-testid="stSidebarNav"] > ul li:first-child {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Logo
with st.sidebar:
    st.logo("assets/ooredoo_logo.png", size="large", link="https://www.ooredoo.dz/")

# --------------------------------------------------------------------------------------------------
# Tous les fonctions
# --------------------------------------------------------------------------------------------------

# Fonction de déconnexion
def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

def chatbot():
    st.markdown("<h1 style='text-align: center;'>Bienvenue dans le Chatbot</h1>", unsafe_allow_html=True)
    
    # Initialize messages in session state if not already present
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from the session state
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input box for user to ask questions
    if user_input := st.chat_input("Posez votre question ici...", key="chat_input"):
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Generate a response (simple example logic)
        if "offre" in user_input.lower():
            bot_response = "Nos offres incluent des forfaits Internet, des appels et des SMS adaptés à vos besoins."
        elif "assistance" in user_input.lower():
            bot_response = "Pour toute assistance, veuillez contacter notre service client au 123."
        else:
            bot_response = "Je suis désolé, je ne comprends pas votre question. Pouvez-vous reformuler ?"

        # Add bot response to session state
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

    # Button to clear chat messages
    if st.button("Effacer les messages", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Display updated chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --------------------------------------------------------------------------------------------------


# Vérification de l'authentification
if "authenticated" not in st.session_state or not st.session_state.get("authenticated", False):
    st.warning("Vous devez vous connecter pour accéder à cette page.")
    with st.sidebar.form(key="login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submit_button = st.form_submit_button("Se connecter", use_container_width=True)

    if submit_button:
        # Remplacez ces valeurs par vos propres vérifications
        if (username.lower() == usernames[0] and password == passwords[0]) or \
           (username.lower() == usernames[1] and password == passwords[1]):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.sidebar.success("Connexion réussie !")
            # On utilise st.rerun() pour recharger la page et masquer le formulaire
            st.rerun()
        else:
            st.sidebar.error("Nom d'utilisateur ou mot de passe incorrect.")
else:
    with st.sidebar:
        st.write(f"Bienvenue, {st.session_state.username} !")
    
    chatbot()
    
    with st.sidebar:
        st.button("Déconnexion", on_click=logout, use_container_width=True)
        st.markdown("""
            <footer style="text-align: center; margin-top: 50px; font-size: 0.9rem; color: #888;">
                <hr style="border: none; border-top: 1px solid #ccc; margin: 10px 0;">
                <p>&copy; OOREDOO ALGERIA | Développé par <strong>OUARAS Khelil Rafik</strong></p>
            </footer>
        """, unsafe_allow_html=True)