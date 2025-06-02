import streamlit as st
import ollama
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import re
import pandas as pd
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
import sys
import sqlite3
import json
import io

# Supprimer torch.classes du système de surveillance de Streamlit
sys.modules['torch.classes'].__path__ = []

# ----------- Base SQLite pour historique --------------
def init_db():
    conn = sqlite3.connect('data/chat_history.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    return conn


def save_message(conn, username, role, content):
    c = conn.cursor()
    c.execute('INSERT INTO conversations (username, role, content) VALUES (?, ?, ?)', (username, role, content))
    conn.commit()

def load_messages(conn, username):
    c = conn.cursor()
    c.execute('SELECT role, content FROM conversations WHERE username = ? ORDER BY timestamp', (username,))
    rows = c.fetchall()
    return [{"role": r, "content": c} for r, c in rows]

def clear_messages(conn, username=None):
    c = conn.cursor()
    if username is None:
        c.execute('DELETE FROM conversations')
    else:
        c.execute('DELETE FROM conversations WHERE username = ?', (username,))
    conn.commit()

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

# ---------------------------- Déconnexion -------------------------
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

# ---------------------------- Fusion Post + Comments -------------------------
def merge_posts_with_comments(posts_df_path="data/posts_df_classified.csv", comments_df_path="data/comments_df_classified.csv"):
    posts_df = pd.read_csv(posts_df_path)
    comments_df = pd.read_csv(comments_df_path)

    # Merge avec ID Post
    merged_df = pd.merge(comments_df, posts_df, how="left", left_on="ID Post", right_on="ID")

    # Ajout d'une colonne indiquant s’il s’agit d’un Post ou d’un Commentaire
    merged_df['Type'] = "Commentaire"
    posts_df['Type'] = "Post"

    # Reconstituer les textes détaillés
    def full_comment_text(row):
        comment_categories = [col for col in comments_df.columns if col not in ['ID Comment', 'ID Post', 'User Name', 'Comments', 'Sentiments'] and row.get(col, 0) == 1]
        return (
            f"[COMMENTAIRE]\n"
            f"Utilisateur: {row['User Name']}\n"
            f"Commentaire: {row['Comments']}\n"
            f"Sentiment: {row['Sentiments']}\n"
            f"Catégories: {', '.join(comment_categories)}\n"
        )

    def full_post_text(row):
        post_categories = [col for col in ['Culture & Celebration', 'Sport', 'Product', 'Promotion', 'Network', 'Survey', 'Event', 'Contest & Games', 'Other'] if row.get(col, 0) == 1]
        return (
            f"[POST]\n"
            f"Date: {row['Date']}\n"
            f"Contenu: {row['Contents']}\n"
            f"Lien: {row['Lien Post']}\n"
            f"Réactions: Likes({row['Nb Like']}), Love({row['Nb Love']}), Care({row['Nb Care']}), Wow({row['Nb Wow']}), Sad({row['Nb Sad']}), Angry({row['Nb Angry']}), Haha({row['Nb Haha']})\n"
            f"Société: {row['Company']}\n"
            f"Catégories: {', '.join(post_categories)}\n"
        )

    # Génère les textes combinés pour le modèle
    merged_df['document_text'] = merged_df.apply(full_comment_text, axis=1)
    posts_df['document_text'] = posts_df.apply(full_post_text, axis=1)

    # Fusion finale : inclut TOUS les posts, avec ou sans commentaires
    final_df = pd.concat([
        posts_df[['ID', 'document_text', 'Type']],
        merged_df[['ID Post', 'document_text', 'Type']].rename(columns={'ID Post': 'ID'})
    ], ignore_index=True).drop_duplicates(subset=['ID', 'document_text'])

    final_df.sort_values(by="ID", inplace=True)

    return final_df

# ---------------------------- Chargement et préparation des données -------------------------
def load_and_prepare_data():
    combined_df = merge_posts_with_comments()
    return combined_df

# ---------------------------- Création du Vectorstore avec dédoublonnage -------------------------
def create_vectorstore(combined_df):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    texts = combined_df['document_text'].tolist()
    embeddings = model.encode(texts, show_progress_bar=True)

    client = PersistentClient(path=".chromadb")
    collection = client.get_or_create_collection(name="ooredoo_documents")

    existing_ids = set(collection.get()['ids'])
    new_texts, new_embeddings, new_ids = [], [], []
    base_id = max(map(int, existing_ids)) + 1 if existing_ids else 0

    for i, text in enumerate(texts):
        if text not in collection.get()['documents']:
            new_texts.append(text)
            new_embeddings.append(embeddings[i].tolist())
            new_ids.append(str(base_id + i))

    if new_texts:
        collection.add(documents=new_texts, embeddings=new_embeddings, ids=new_ids)

    return collection

# ------------------------------ Préparation du RAG -------------------------
@st.cache_resource(show_spinner="Chargement des données contextuelles...")
def setup_rag():
    combined_df = load_and_prepare_data()
    collection = create_vectorstore(combined_df)
    return collection

# ---------------------------- Recherche contextuelle -------------------------
def get_context_from_rag(query, collection, k=3):
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
    conn = init_db()
    username = st.session_state.get('username', 'anonyme')

    if "messages" not in st.session_state or st.session_state.get("last_page") != "🤖Chatbot":
        history = load_messages(conn, username)
        if not history:
            welcome_msg = f"Bonjour {username} 👋, comment puis-je vous aider sur les opérateurs télécom en Algérie ?"
            st.session_state.messages = [{"role": "assistant", "content": welcome_msg}]
            save_message(conn, username, "assistant", welcome_msg)
        else:
            st.session_state.messages = history
    st.session_state["last_page"] = "🤖Chatbot"

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
        save_message(conn, username, "human", prompt)

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
                save_message(conn, username, "assistant", response)

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
        conn = init_db()
        st.write(f'Bienvenue, {st.session_state.username} !')
        if st.sidebar.button("🗑️ Supprimer tous les historiques", use_container_width=True):
            clear_messages(conn)
            st.sidebar.success("Tous les historiques ont été supprimés.")
            st.session_state.messages = [{
                "role": "assistant",
                "content": f"Bonjour {st.session_state.get('username', '')} 👋, comment puis-je vous aider sur les opérateurs télécom en Algérie ?"
            }]
            st.rerun()
        
        # Bouton unique de téléchargement de l'historique
        data_to_export = st.session_state.messages
        json_str = json.dumps(data_to_export, ensure_ascii=False, indent=2)
        buffer = io.BytesIO()
        buffer.write(json_str.encode('utf-8'))
        buffer.seek(0)
        st.sidebar.download_button(
            label="📥 Télécharger l’historique",
            data=buffer,
            file_name=f"historique_{st.session_state.username}.json",
            mime="application/json",
            use_container_width=True
        )
        
        st.button('Déconnexion', on_click=logout, use_container_width=True)
        st.markdown("""
            <footer style='text-align: center; margin-top: 50px; font-size: 0.9rem; color: #888;'>
                <hr style='border: none; border-top: 1px solid #ccc; margin: 10px 0;'>
                <p>&copy; OOREDOO ALGERIA | Développé par <strong>OUARAS Khelil Rafik</strong></p>
            </footer>
        """, unsafe_allow_html=True)

    chatbot()
