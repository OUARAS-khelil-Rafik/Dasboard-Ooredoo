import streamlit as st
import ollama
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import re
import pandas as pd
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
import sys

# Supprimer torch.classes du système de surveillance de Streamlit
sys.modules['torch.classes'].__path__ = []


# ---------------------------- Variables ---------------------------
usernames = st.secrets['usernames']
passwords = st.secrets['passwords']

# ---------------------------- Config page -------------------------
st.set_page_config(page_title="Chatbot Ooredoo",
                   page_icon="assets/ooredoo_logo2.png",
                   layout="wide")

st.markdown("""
<style>
    [data-testid="stSidebarNav"] > ul li:first-child {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------- Logo -------------------------
with st.sidebar:
    st.logo("assets/ooredoo_logo.png", size="large", link="https://www.ooredoo.dz/")

# ---------------------------- Auth -------------------------
def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

# ---------------------------- Chatbot Init -------------------------
@st.cache_resource(show_spinner=False)
def initialize_chatbot():
    client = ollama.Client()
    model = 'qwen3:8b'
    return client, model

# ---------------------------- Nettoyage -------------------------
def clean_response(text):
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'<search>.*?</search>', '', text, flags=re.DOTALL)
    return text.strip()

# ---------------------------- Chargement et préparation des données -------------------------
def load_and_prepare_data():
    # Charger les deux fichiers CSV complets
    comments_df = pd.read_csv("data/comments_df_classified.csv")
    posts_df = pd.read_csv("data/posts_df_classified.csv")

    # Pour chaque DataFrame, on crée une nouvelle colonne "document_text"
    # qui concatène de façon lisible toutes les infos importantes en texte.
    
    # Pour les commentaires : on concatène date (via ID Post si possible), user, comment, sentiment, catégories...
    post_dates = posts_df.set_index('ID')['Date'].to_dict()
    
    def build_comment_text(row):
        post_date = post_dates.get(row['ID Post'], 'Date inconnue')
        parts = [
            f"Date du post: {post_date}",
            f"Utilisateur: {row['User Name']}",
            f"Commentaire: {row['Comments']}",
            f"Sentiment: {row['Sentiments']}",
            "Catégories: " + ", ".join(
                [col for col in comments_df.columns if col not in ['ID Comment', 'ID Post', 'User Name', 'Comments', 'Sentiments'] and row[col] == 1]
            )
        ]
        # Supprimer les parties vides
        parts = [p for p in parts if p.strip() != ""]
        return " | ".join(parts)

    comments_df['document_text'] = comments_df.apply(build_comment_text, axis=1)

    # Pour les posts, on concatène toutes les infos importantes
    def build_post_text(row):
        parts = [
            f"Date: {row['Date']}",
            f"Contenu: {row['Contents']}",
            f"Lien: {row['Lien Post']}",
            f"Réactions: Likes({row['Nb Like']}), Love({row['Nb Love']}), Care({row['Nb Care']}), Wow({row['Nb Wow']}), Sad({row['Nb Sad']}), Angry({row['Nb Angry']}), Haha({row['Nb Haha']})",
            f"Société: {row['Company']}",
            "Catégories: " + ", ".join([col for col in ['Culture & Celebration', 'Sport', 'Product', 'Promotion', 'Network', 'Survey', 'Event', 'Contest & Games', 'Other'] if row[col] == 1])
        ]
        return " | ".join(parts)

    posts_df['document_text'] = posts_df.apply(build_post_text, axis=1)

    # Combine les deux DataFrames avec la colonne 'document_text'
    combined_df = pd.concat([comments_df[['document_text']], posts_df[['document_text']]], ignore_index=True)

    return combined_df

# ---------------------------- Création du Vectorstore -------------------------
def create_vectorstore(combined_df):
    # Init modèle embedding
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Embeddings des documents
    texts = combined_df['document_text'].tolist()
    embeddings = model.encode(texts, show_progress_bar=True)

    # Init ChromaDB (nouvelle API)
    client = PersistentClient(path=".chromadb")
    collection = client.get_or_create_collection(name="ooredoo_documents")

    # Ajout des documents (par lots si nécessaire)
    ids = [str(i) for i in range(len(texts))]
    collection.add(
        documents=texts,
        embeddings=embeddings.tolist(),
        ids=ids
    )

    return collection

# ------------------------------ Préparation du RAG -------------------------
@st.cache_resource(show_spinner="Chargement des données contextuelles...")
def setup_rag():
    combined_df = load_and_prepare_data()
    collection = create_vectorstore(combined_df)
    return collection

# ---------------------------- Recherche contextuelle -------------------------
def get_context_from_rag(query, collection, k=5):
    results = collection.query(query_texts=[query], n_results=k)
    return "\n\n".join(results['documents'][0]) if results['documents'] else ""

# ---------------------------- Génération réponse -------------------------
def generate_response(prompt, client, model, context=""):
    try:
        full_prompt = f"Contexte : {context}\n\nQuestion : {prompt}" if context else prompt
        full_prompt = full_prompt[:1000]
        response = client.generate(model=model, prompt=full_prompt)
        raw_text = response.get('response') if isinstance(response, dict) else getattr(response, 'response', str(response))
        return clean_response(raw_text)
    except Exception as e:
        return f"Erreur lors de la génération : {str(e)}"

executor = ThreadPoolExecutor(max_workers=4)

def generate_response_async(prompt, client, model, context=""):
    future = executor.submit(generate_response, prompt, client, model, context)
    return future

# ---------------------------- Chatbot principal -------------------------
def chatbot():
    st.markdown("<h1 style='text-align: center;'>ASSISTANT AI TÉLÉCOM</h1>", unsafe_allow_html=True)
    client, model = initialize_chatbot()
    collection = setup_rag()

    if "messages" not in st.session_state or st.session_state.get("last_page") != "🤖Chatbot":
        st.session_state.messages = [{
            "role": "assistant",
            "content": f"Bonjour {st.session_state.get('username', '')} 👋, comment puis-je vous aider sur les opérateurs télécom en Algérie ?"
        }]
    st.session_state["last_page"] = "🤖Chatbot"

    # Style
    st.markdown("""
    <style>
    .chat-bubble-assistant {
        background: #f6f6fa; box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border-radius: 12px; padding: 1rem 1.2rem;
        margin-bottom: 0.5rem; margin-right: 20%;
        border-left: 4px solid #E30613;
    }
    .chat-bubble-human {
        background: #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.10);
        border-radius: 12px; padding: 1rem 1.2rem;
        margin-bottom: 0.5rem; margin-left: 20%;
        border-right: 4px solid #28A745;
    }
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    [data-testid="stChatMessage"] {
        background: transparent !important; box-shadow: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    def is_arabic(text):
        return bool(re.search(r'[\u0600-\u06FF]', text))

    for msg in st.session_state.messages:
        direction = "rtl" if is_arabic(msg["content"]) else "ltr"
        with st.chat_message(msg["role"]):
            bubble_class = 'chat-bubble-assistant' if msg["role"] == "assistant" else 'chat-bubble-human'
            st.markdown(f"<div class='{bubble_class}' dir='{direction}'>{msg['content']}</div>", unsafe_allow_html=True)

    prompt = st.chat_input("Votre question...")
    if prompt:
        st.session_state.messages.append({"role": "human", "content": prompt})
        direction = "rtl" if is_arabic(prompt) else "ltr"
        with st.chat_message("human"):
            st.markdown(f"<div class='chat-bubble-human' dir='{direction}'>{prompt}</div>", unsafe_allow_html=True)

        with st.chat_message("assistant"):
            with st.spinner("L'Assistant réfléchit..."):
                context = get_context_from_rag(prompt, collection)
                future = generate_response_async(prompt, client, model, context)
                try:
                    response = future.result()
                except TimeoutError:
                    response = "Temps d'attente dépassé, veuillez réessayer."
                except Exception as e:
                    response = f"Erreur : {str(e)}"

                direction = "rtl" if is_arabic(response) else "ltr"
                st.markdown(f"<div class='chat-bubble-assistant' dir='{direction}'>{response}</div>", unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": response})

# ---------------------------- Authentification -------------------------
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
        if st.button("Effacer l'historique", use_container_width=True):
            st.session_state.messages = [{
                "role": "assistant",
                "content": f"Bonjour {st.session_state.get('username', '')} 👋, comment puis-je vous aider sur les opérateurs télécom en Algérie ?"
            }]
            st.rerun()
        st.button('Déconnexion', on_click=logout, use_container_width=True)
        st.markdown("""
            <footer style='text-align: center; margin-top: 50px; font-size: 0.9rem; color: #888;'>
                <hr style='border: none; border-top: 1px solid #ccc; margin: 10px 0;'>
                <p>&copy; OOREDOO ALGERIA | Développé par <strong>OUARAS Khelil Rafik</strong></p>
            </footer>
        """, unsafe_allow_html=True)

    chatbot()
