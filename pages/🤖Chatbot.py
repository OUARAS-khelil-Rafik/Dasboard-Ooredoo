import streamlit as st
import locale
import ollama

locale.setlocale(locale.LC_TIME, 'French_France.1252')

# ---------------------------- Variables ---------------------------
usernames = st.secrets["usernames"]
passwords = st.secrets["passwords"]

# Configuration de la page
st.set_page_config(
    page_title="Assistant AI Télécom",
    page_icon="assets/ooredoo_logo2.png",
    layout="wide"
)

st.markdown("""
<style>
    [data-testid="stSidebarNav"] > ul li:first-child {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Logo dans la barre latérale
with st.sidebar:
    st.image("assets/ooredoo_logo.png", width=200)

# Fonction de déconnexion
def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

# Initialiser le chatbot Ollama
def initialize_chatbot():
    client = ollama.Client()  # instanciation correcte
    model = "qwen3:8b"        # modèle Ollama à utiliser
    return client, model

# Générer une réponse via Ollama
def generate_response(prompt, client, model):
    try:
        response = client.generate(model=model, prompt=prompt)
        raw_text = getattr(response, "response", None)
        if raw_text is None:
            # fallback au string complet
            raw_text = str(response)

        # Extraction : on enlève la partie <think> ... </think>
        if "</think>" in raw_text:
            # On récupère tout ce qui est après </think>
            clean_response = raw_text.split("</think>")[-1].strip()
        else:
            clean_response = raw_text.strip()

        return clean_response
    except Exception as e:
        return f"Erreur lors de la génération : {str(e)}"

# Fonction principale chatbot
def chatbot():
    st.title("Assistant AI Télécom")

    client, model = initialize_chatbot()

    st.markdown("### Posez vos questions sur Djezzy, Ooredoo, Mobilis")

    # Initialisation historique dans session_state
    if "history" not in st.session_state:
        st.session_state.history = []

    # Champ de texte utilisateur
    user_input = st.text_area("Votre question :", height=100)

    if st.button("Envoyer"):
        if user_input.strip():
            with st.spinner("L'Assistant réfléchit..."):
                response = generate_response(user_input, client, model)
            st.markdown("**Réponse :**")
            st.write(response)

            # Ajouter à l'historique uniquement ici
            st.session_state.history.append({"question": user_input, "response": response})

        else:
            st.warning("Veuillez entrer une question.")

    # Affichage de l'historique
    if st.session_state.history:
        st.markdown("### Historique des conversations")
        for chat in st.session_state.history:
            st.markdown(f"**Vous :** {chat['question']}")
            st.markdown(f"**Assistant :** {chat['response']}")

# Vérification de l'authentification
if "authenticated" not in st.session_state or not st.session_state.get("authenticated", False):
    st.warning("Vous devez vous connecter pour accéder à cette page.")
    with st.sidebar.form(key="login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submit_button = st.form_submit_button("Se connecter", use_container_width=True)

    if submit_button:
        if (username.lower() == usernames[0] and password == passwords[0]) or \
           (username.lower() == usernames[1] and password == passwords[1]):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.sidebar.success("Connexion réussie !")
            st.experimental_rerun()
        else:
            st.sidebar.error("Nom d'utilisateur ou mot de passe incorrect.")
else:
    with st.sidebar:
        st.write(f"Bienvenue, {st.session_state.username} !")
        st.button("Déconnexion", on_click=logout, use_container_width=True)
        st.markdown("""
            <footer style="text-align: center; margin-top: 50px; font-size: 0.9rem; color: #888;">
                <hr style="border: none; border-top: 1px solid #ccc; margin: 10px 0;">
                <p>&copy; OOREDOO ALGERIA | Développé par <strong>OUARAS Khelil Rafik</strong></p>
            </footer>
        """, unsafe_allow_html=True)
    chatbot()
