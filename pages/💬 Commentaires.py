import streamlit as st
import pandas as pd
import altair as alt
import locale
locale.setlocale(locale.LC_TIME, 'French_France.1252')

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

#--------------------------------------------------------------------------------------------------
# Dataset
#--------------------------------------------------------------------------------------------------

# Chargement du dataset Publications
try:
    df_posts = pd.read_csv("data/posts_df_classified.csv", encoding='utf-8')
except FileNotFoundError:
    st.error("Le fichier 'data/posts_df_classified.csv' est introuvable. Veuillez vérifier le chemin.")
except pd.errors.EmptyDataError:
    st.error("Le fichier est vide. Veuillez vérifier son contenu.")
except Exception as e:
    st.error(f"Une erreur s'est produite : {e}")

# Chargement du dataset Commentaires
try:
    df_comments = pd.read_csv("data/comments_df_classified.csv", encoding='utf-8', index_col=0)
except FileNotFoundError:
    st.error("Le fichier 'data/comments_df_classified.csv' est introuvable. Veuillez vérifier le chemin.")
except pd.errors.EmptyDataError:
    st.error("Le fichier est vide. Veuillez vérifier son contenu.")
except Exception as e:
    st.error(f"Une erreur s'est produite : {e}")

# --------------------------------------------------------------------------------------------------
# Tous les fonctions
# --------------------------------------------------------------------------------------------------

# Fonction de déconnexion
def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

def afficher_tableau_comment(df_comments, df_posts):
    st.markdown("<h1 style='text-align: center;'>TABLEAU DE BORD COMMENTAIRES</h1>", unsafe_allow_html=True)

def afficher_data_comment(df_comments, df_posts):
    st.markdown("<h1 style='text-align: center;'>DONNÉES COMMENTAIRES</h1>", unsafe_allow_html=True)
    
    if not df_comments.empty:
        # Filtre pour sélectionner les colonnes à afficher jusqu'à l'index 4
        all_columns = df_comments.columns[:4].tolist()  # Sélectionner les colonnes jusqu'à l'index 4 inclus
        default_columns = ["ID Post", "User Name", "Comments", "Sentiments"]
        selected_columns = st.multiselect("Sélectionnez les colonnes à afficher", all_columns, default=[col for col in default_columns if col in all_columns])
        
        # Disposition des filtres sur une seule ligne
        col1, col2, col3, col4 = st.columns(4, vertical_alignment="center", gap="small")

        with col1:
            # Filtre par ID Post
            if 'ID Post' in df_comments.columns:
                post_ids = df_comments['ID Post'].dropna().unique()
                selected_post_id = st.selectbox("Filtrer par ID Post", ["Tous"] + list(post_ids))
                if selected_post_id != "Tous":
                    df_comments = df_comments[df_comments['ID Post'] == selected_post_id]
        
        
        with col2:
            # Filtre par Date
            if 'Date' in df_posts.columns and 'ID Post' in df_comments.columns:
                try:
                    df_posts['Date'] = pd.to_datetime(df_posts['Date']).dt.date  # Convertir en date uniquement
                    min_date = df_posts['Date'].min()
                    max_date = df_posts['Date'].max()
                    date_range = st.date_input("Filtrer par date", [min_date, max_date])
                    if len(date_range) == 2:
                        start_date, end_date = date_range
                        df_comments = df_comments.merge(df_posts[['ID', 'Date']], left_on='ID Post', right_on='ID', how='left')
                        df_comments = df_comments[(df_comments['Date'] >= start_date) & (df_comments['Date'] <= end_date)]
                except Exception as e:
                    st.error(f"Erreur lors de la conversion des dates : {e}")
        
        with col3:
            # Filtre par Sentiments
            if 'Sentiments' in df_comments.columns:
                sentiments = df_comments['Sentiments'].dropna().unique()
                selected_sentiments = st.selectbox("Filtrer par sentiment", ["Tous"] + list(sentiments))
                if selected_sentiments != "Tous":
                    df_comments = df_comments[df_comments['Sentiments'] == selected_sentiments]

        with col4:
            # Filtre par catégories (initialisé par les index 4 jusqu'à la fin des index du dataset)
            if len(df_comments.columns) > 4:  # Vérifier si le DataFrame a au moins 4 colonnes
                categories = df_comments.iloc[:, 4:].columns.tolist()  # Récupérer les colonnes à partir de l'index 11
                selected_category = st.selectbox("Filtrer par catégorie", ["Tous"] + categories)
                if selected_category != "Tous":
                    df_comments = df_comments[df_comments[selected_category] == 1]  # Supposons que les colonnes sont des indicateurs binaires
        
            
        
        # Afficher les données filtrées
        if selected_columns:
            filtered_data = df_comments[selected_columns]
            st.dataframe(filtered_data, height=450, row_height=70)
        else:
            st.error("Veuillez sélectionner au moins une colonne à afficher.")
        
        # Compter le nombre de publications affichées
        st.markdown(f"<p style='text-align: center;'><strong>Nombre total de commentaire trouvées : <span style='color: #E30613;'>{len(df_comments)}</span></strong></p>", unsafe_allow_html=True)
    else:
        st.warning("Le dataset est vide. Veuillez vérifier son contenu.")
    
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
        if (username.lower() == "ooredoodz" and password == "Ooredoo@2025") or \
           (username.lower() == "admin" and password == "Admin@admin"):
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
        pub = st.selectbox(
            "Choisissez pour afficher :",
            ["Statistiques", "Données"]
        )

    # Appel des fonctions
    if pub == "Données":
        afficher_data_comment(df_comments, df_posts)
    else:
        afficher_tableau_comment(df_comments, df_posts)
    
    with st.sidebar:
        st.button("Déconnexion", on_click=logout, use_container_width=True)