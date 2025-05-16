import streamlit as st
import locale
import ollama
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import re

# Configuration locale pour la date (optionnel selon usage)
locale.setlocale(locale.LC_TIME, 'French_France.1252')

# ---------------------------- Variables ---------------------------
usernames = st.secrets['usernames']
passwords = st.secrets['passwords']

# Configuration de la page
st.set_page_config(page_title="Dashboard Ooredoo",
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

# Fonction de logout
def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

# Initialisation et cache du client Ollama et modèle
@st.cache_resource(show_spinner=False)
def initialize_chatbot():
    client = ollama.Client()
    model = 'qwen3:8b'  # Ton modèle Ollama
    return client, model

# Nettoyage de la réponse (suppression balise <think> ...)
def clean_response(text):
    if "<think>" in text and "</think>" in text:
        before = text.split("<think>")[0]
        after = text.split("</think>")[-1]
        return (before + after).strip()
    else:
        return text.strip()

# Génération de la réponse via Ollama
def generate_response(prompt, client, model):
    try:
        prompt = prompt[:500]
        response = client.generate(model=model, prompt=prompt)
        if isinstance(response, dict) and 'response' in response:
            raw_text = response['response']
        elif hasattr(response, 'response'):
            raw_text = response.response
        else:
            raw_text = str(response)
        clean_text = clean_response(raw_text)
        return clean_text
    except Exception as e:
        return f"Erreur lors de la génération : {str(e)}"

executor = ThreadPoolExecutor(max_workers=4)

def generate_response_async(prompt, client, model):
    future = executor.submit(generate_response, prompt, client, model)
    return future

def chatbot():
    st.markdown("<h1 style='text-align: center;'>ASSISTANT AI TÉLÉCOM</h1>", unsafe_allow_html=True)
    client, model = initialize_chatbot()

    # Initialisation de l'historique des messages
    if "messages" not in st.session_state or st.session_state.get("last_page") != "🤖Chatbot":
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": f"Bonjour {st.session_state.get('username', '')} 👋, comment puis-je vous aider sur les opèrateurs télécom en Algérie ?"
            }
        ]
    st.session_state["last_page"] = "🤖Chatbot"

    # Style CSS pour masquer les avatars et le fond des messages
    st.markdown("""
    <style>
    .chat-bubble-assistant {
        background: #f6f6fa;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.5rem;
        margin-right: 20%;
        border-left: 4px solid #e6002a;
    }
    .chat-bubble-human {
        background: #fff;
        box-shadow: 0 2px 8px rgba(0,0,0,0.10);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.5rem;
        margin-left: 20%;
        border-right: 4px solid #0072c6;
    }
    [data-testid="stChatMessageAvatarUser"], 
    [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    [data-testid="stChatMessage"] {
        background: transparent !important;
        box-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)


    def is_arabic(text):
        # Check if the text contains any Arabic character
        return bool(re.search(r'[\u0600-\u06FF]', text))

    # Affichage de l'historique des messages
    for msg in st.session_state.messages:
        direction = "rtl" if is_arabic(msg["content"]) else "ltr"
        if msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(
                    f"<div class='chat-bubble-assistant' dir='{direction}'>{msg['content']}</div>",
                    unsafe_allow_html=True
                )
        else:
            with st.chat_message("human"):
                st.markdown(
                    f"<div class='chat-bubble-human' dir='{direction}'>{msg['content']}</div>",
                    unsafe_allow_html=True
                )

    prompt = st.chat_input("Votre question...")
    if prompt:
        # Ajout du message utilisateur
        st.session_state.messages.append({"role": "human", "content": prompt})

        direction = "rtl" if is_arabic(prompt) else "ltr"
        with st.chat_message("human"):
            st.markdown(
                f"<div class='chat-bubble-human' dir='{direction}'>{prompt}</div>",
                unsafe_allow_html=True
            )

        with st.chat_message("assistant"):
            with st.spinner("L'Assistant réfléchit..."):
                future = generate_response_async(prompt, client, model)
                try:
                    response = future.result()
                except TimeoutError:
                    response = "Temps d'attente dépassé, veuillez réessayer."
                except Exception as e:
                    response = f"Erreur : {str(e)}"
                direction = "rtl" if is_arabic(response) else "ltr"
                st.markdown(
                    f"<div class='chat-bubble-assistant' dir='{direction}'>{response}</div>",
                    unsafe_allow_html=True
                )
                # Ajout de la réponse de l'assistant dans l'historique
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response
                })

# Authentification
if 'authenticated' not in st.session_state or not st.session_state.get('authenticated', False):
    st.warning('Vous devez vous connecter pour accéder à cette page.')
    with st.sidebar.form(key='login_form'):
        username = st.text_input('Nom d\'utilisateur')
        password = st.text_input('Mot de passe', type='password')
        submit_button = st.form_submit_button('Se connecter', use_container_width=True)

    if submit_button:
        if (username.lower() == usernames[0] and password == passwords[0]) or \
           (username.lower() == usernames[1] and password == passwords[1]):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.sidebar.success('Connexion réussie !')
            st.rerun()
        else:
            st.sidebar.error('Nom d\'utilisateur ou mot de passe incorrect.')
else:
    with st.sidebar:
        st.write(f'Bienvenue, {st.session_state.username} !')
        
        # Ajout du bouton Effacer l'historique dans la sidebar
        if st.button("Effacer l'historique", use_container_width=True):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": f"Bonjour {st.session_state.get('username', '')} 👋, comment puis-je vous aider sur les opèrateurs télécom en Algérie ?",
                    "avatar": "assets/ooredoo_logo2.png"
                }
            ]
            st.rerun()
        
        
        st.button('Déconnexion', on_click=logout, use_container_width=True)
        st.markdown('''
            <footer style='text-align: center; margin-top: 50px; font-size: 0.9rem; color: #888;'>
                <hr style='border: none; border-top: 1px solid #ccc; margin: 10px 0;'>
                <p>&copy; OOREDOO ALGERIA | Développé par <strong>OUARAS Khelil Rafik</strong></p>
            </footer>
        ''', unsafe_allow_html=True)
    chatbot()
