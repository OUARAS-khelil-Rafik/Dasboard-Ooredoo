import streamlit as st
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="Publications",
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

def afficher_tableau_pub():
    st.markdown("<h1 style='text-align: center;'>TABLEAU DE BORD PUBLICATIONS</h1>", unsafe_allow_html=True)
    

def afficher_data_pub():
    st.markdown("<h1 style='text-align: center;'>DONNÉES PUBLICATIONS</h1>", unsafe_allow_html=True)

    # Chargement du dataset
    try:
        df = pd.read_csv("data/posts_df_classified.csv", encoding='utf-8', index_col=0)
        # Vérifier si le DataFrame n'est pas vide
        if not df.empty:
            # Filtre pour sélectionner les colonnes à afficher jusqu'à l'index 11
            all_columns = df.columns[:11].tolist()  # Sélectionner les colonnes jusqu'à l'index 11 inclus
            default_columns = ["Contents", "Date", "Company"]
            selected_columns = st.multiselect("Sélectionnez les colonnes à afficher", all_columns, default=[col for col in default_columns if col in all_columns])
            
            # Disposition des filtres sur une seule ligne
            col1, col2, col3 = st.columns(3, vertical_alignment="center", gap="large")

            with col1:
                # Filtre par opérateur (Company)
                if 'Company' in df.columns:
                    companies = df['Company'].dropna().unique()
                    selected_company = st.selectbox("Filtrer par opérateur", ["Tous"] + list(companies))
                    if selected_company != "Tous":
                        df = df[df['Company'] == selected_company]

            with col2:
                # Filtre par date
                if 'Date' in df.columns:
                    try:
                        df['Date'] = pd.to_datetime(df['Date']).dt.date  # Convertir en date uniquement
                        min_date = df['Date'].min()
                        max_date = df['Date'].max()
                        date_range = st.date_input("Filtrer par date", [min_date, max_date])
                        if len(date_range) == 2:
                            start_date, end_date = date_range
                            df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
                    except Exception as e:
                        st.error(f"Erreur lors de la conversion des dates : {e}")

            with col3:
                # Filtre par catégories (initialisé par les index 11 jusqu'à la fin des index du dataset)
                if len(df.columns) > 11:  # Vérifier si le DataFrame a au moins 12 colonnes
                    categories = df.iloc[:, 11:].columns.tolist()  # Récupérer les colonnes à partir de l'index 11
                    selected_category = st.selectbox("Filtrer par catégorie", ["Tous"] + categories)
                    if selected_category != "Tous":
                        df = df[df[selected_category] == 1]  # Supposons que les colonnes sont des indicateurs binaires

            # Afficher les données filtrées
            if selected_columns:
                filtered_data = df[selected_columns]
                st.dataframe(filtered_data, height=450, row_height=70)
            else:
                st.error("Veuillez sélectionner au moins une colonne à afficher.")
            
            # Compter le nombre de publications affichées
            st.markdown(f"<p style='text-align: center;'><strong>Nombre total de publications trouvées : {len(df)}</strong></p>", unsafe_allow_html=True)
        else:
            st.warning("Le dataset est vide. Veuillez vérifier son contenu.")
    except FileNotFoundError:
        st.error("Le fichier 'data/posts_df_classified.csv' est introuvable. Veuillez vérifier le chemin.")
    except pd.errors.EmptyDataError:
        st.error("Le fichier est vide. Veuillez vérifier son contenu.")
    except Exception as e:
        st.error(f"Une erreur s'est produite : {e}")
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
        pub = st.selectbox(
            "Choisissez pour afficher :",
            ["Statistiques", "Données"]
        )
        st.write(f"Bienvenue, {st.session_state.username} !")
        st.button("Déconnexion", on_click=logout, use_container_width=True)

    # Appel des fonctions
    if pub == "Données":
        afficher_data_pub()
    else:
        afficher_tableau_pub()
