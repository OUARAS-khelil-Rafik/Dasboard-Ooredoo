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

    if 'Date' in df_posts.columns and 'Company' in df_posts.columns and 'ID Post' in df_comments.columns:
        try:
            # Ordre des mois
            month_names = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                           'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

            # Préparer les colonnes de date
            df_posts['Date'] = pd.to_datetime(df_posts['Date'])
            df_posts['Mois'] = df_posts['Date'].dt.month
            df_posts['Année'] = df_posts['Date'].dt.year

            # Filtres d'affichage
            with st.sidebar:
                # Filtre par opérateurs
                operators = ["Tous"] + df_posts['Company'].dropna().unique().tolist()
                selected_operator = st.selectbox("Filtrer par opérateur", operators)
                
                # Recherche par ID Post
                search_post_id = st.text_input("Rechercher un ID Post", placeholder="Ex: 123456789")
                
                # Filtre par année
                selected_year = st.selectbox("Filtrer par année", sorted(df_posts['Année'].unique().tolist()))
                
                # Filtre par mois
                selected_month_range = st.select_slider(
                    "Filtrer par mois",
                    options=list(range(1, 13)),
                    value=(1, 12),
                    format_func=lambda x: month_names[x - 1]
                )
                start_month, end_month = selected_month_range

            # Application des filtres sur les publications
            df_filtered_posts = df_posts[
                (df_posts['Mois'] >= start_month) &
                (df_posts['Mois'] <= end_month) &
                (df_posts['Année'] == selected_year)
            ]

            if selected_operator != "Tous":
                df_filtered_posts = df_filtered_posts[df_filtered_posts['Company'] == selected_operator]

            if search_post_id:
                df_filtered_posts = df_filtered_posts[df_filtered_posts['ID'].astype(str) == search_post_id]

            # Filtrer les commentaires en fonction des publications filtrées
            filtered_post_ids = df_filtered_posts['ID']
            df_filtered_comments = df_comments[df_comments['ID Post'].isin(filtered_post_ids)]

            # Calcul des commentaires filtrés par opérateur
            nb_com_ooredoo = df_filtered_comments[
                df_filtered_comments['ID Post'].isin(
                    df_filtered_posts[df_filtered_posts['Company'] == 'Ooredoo']['ID']
                )
            ].shape[0]

            nb_com_djezzy = df_filtered_comments[
                df_filtered_comments['ID Post'].isin(
                    df_filtered_posts[df_filtered_posts['Company'] == 'Djezzy']['ID']
                )
            ].shape[0]

            nb_com_mobilis = df_filtered_comments[
                df_filtered_comments['ID Post'].isin(
                    df_filtered_posts[df_filtered_posts['Company'] == 'Mobilis']['ID']
                )
            ].shape[0]

            # Affichage des Cards
            col1, col2, col3 = st.columns(3, border=True, vertical_alignment="center")

            with col1:
                col11, col12 = st.columns([1, 3])
                with col11:
                    st.image("assets/ooredoo_logo2.png", width=70)
                with col12:
                    st.markdown(f"""
                        <div style="text-align: center;">
                            <span style="font-size: 0.9rem; font-weight: bold;">Nombre total des commentaires</span><br>
                            <span style="font-size: 2rem; font-weight: bold; color: #E30613;">{nb_com_ooredoo}</span>
                        </div>
                    """, unsafe_allow_html=True)

            with col2:
                col21, col22 = st.columns([1, 3])
                with col21:
                    st.image("assets/djezzy_logo.png", width=55)
                with col22:
                    st.markdown(f"""
                        <div style="text-align: center;">
                            <span style="font-size: 0.9rem; font-weight: bold;">Nombre total des commentaires</span><br>
                            <span style="font-size: 2rem; font-weight: bold; color: #F58220;">{nb_com_djezzy}</span>
                        </div>
                    """, unsafe_allow_html=True)

            with col3:
                col31, col32 = st.columns([1, 3])
                with col31:
                    st.image("assets/mobilis_logo.png", width=70)
                with col32:
                    st.markdown(f"""
                        <div style="text-align: center;">
                            <span style="font-size: 0.9rem; font-weight: bold;">Nombre total des commentaires</span><br>
                            <span style="font-size: 2rem; font-weight: bold; color: #28A745;">{nb_com_mobilis}</span>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("")
            st.markdown("")
            
            # === Graphique Score des Sentiments ===
            if 'Sentiments' in df_comments.columns and 'ID Post' in df_comments.columns and 'ID' in df_posts.columns:
                # Merge des commentaires avec les publications pour obtenir les informations nécessaires
                df_merged = pd.merge(df_comments, df_posts, left_on='ID Post', right_on='ID', how='inner')

                # Application des filtres
                df_merged = df_merged[
                    (df_merged['Mois'] >= start_month) &
                    (df_merged['Mois'] <= end_month) &
                    (df_merged['Année'] == selected_year)
                ]

                if selected_operator != "Tous":
                    df_merged = df_merged[df_merged['Company'] == selected_operator]

                if search_post_id:
                    df_merged = df_merged[df_merged['ID'].astype(str) == search_post_id]

                # Calcul du score des sentiments
                df_merged['Sentiment_Score'] = (
                    1.0 * (df_merged['Sentiments'] == 'Positif') +
                    0.5 * (df_merged['Sentiments'] == 'Neutre') -
                    1.0 * (df_merged['Sentiments'] == 'Negatif')
                )

                # Grouper par mois et opérateur pour calculer le score total des sentiments
                grouped = df_merged.groupby(['Mois', 'Company'], as_index=False)['Sentiment_Score'].sum()
                grouped['Mois'] = grouped['Mois'].apply(lambda x: month_names[x - 1])
                grouped['Mois'] = pd.Categorical(grouped['Mois'], categories=month_names, ordered=True)
                grouped = grouped.sort_values(['Mois', 'Company'])

                # Création du graphique
                chart = alt.Chart(grouped).mark_bar().encode(
                    x=alt.X('Mois:O', title='Mois', axis=alt.Axis(labelAngle=-45), sort=month_names),
                    y=alt.Y('Sentiment_Score:Q', title='Score des Sentiments'),
                    color=alt.Color('Company:N',
                                    scale=alt.Scale(domain=['Ooredoo', 'Djezzy', 'Mobilis'],
                                                    range=['#E30613', '#F58220', '#28A745']),
                                    legend=alt.Legend(title="Opérateur")),
                    tooltip=['Company', 'Mois', 'Sentiment_Score'],
                    xOffset='Company',
                    opacity=alt.value(0.9),
                ).properties(
                    width=700,
                    height=400,
                )

                st.markdown(f"<h3 style='text-align: center;'>Score des Sentiments par Mois et par Opérateur en {selected_year}</h3>", unsafe_allow_html=True)
                st.markdown("")
                st.altair_chart(chart, use_container_width=True)
            else:
                st.error("Les colonnes nécessaires pour calculer le score des sentiments sont manquantes.")
            
        except Exception as e:
            st.error(f"Erreur : {e}")
    else:
        st.error("Les colonnes 'Date', 'Company' et 'ID Post' sont nécessaires.")

def afficher_data_comment(df_comments, df_posts):
    st.markdown("<h1 style='text-align: center;'>DONNÉES COMMENTAIRES</h1>", unsafe_allow_html=True)
    
    if not df_comments.empty:
        # Filtre pour sélectionner les colonnes à afficher jusqu'à l'index 4
        all_columns = df_comments.columns[:4].tolist()  # Sélectionner les colonnes jusqu'à l'index 4 inclus
        default_columns = ["User Name", "Comments"]
        selected_columns = st.multiselect("Sélectionnez les colonnes à afficher", all_columns, default=[col for col in default_columns if col in all_columns])
        
        # Disposition des filtres sur une seule ligne
        col1, col2, col3, col4 = st.columns(4, vertical_alignment="center", gap="small")

        with col1:
            # Filtre par ID Post avec recherche exacte
            if 'ID Post' in df_comments.columns:
                search_post_id = st.text_input("Rechercher un ID Post", placeholder="Ex: 123456789")
            if search_post_id:
                df_comments = df_comments[df_comments['ID Post'].astype(str) == search_post_id]
        
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
                        post_ids_in_date_range = df_posts[
                            (df_posts['Date'] >= start_date) & (df_posts['Date'] <= end_date)
                        ]['ID']
                        df_comments = df_comments[df_comments['ID Post'].isin(post_ids_in_date_range)]
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
                categories = df_comments.iloc[:, 4:].columns.tolist()  # Récupérer les colonnes à partir de l'index 4
                selected_category = st.selectbox("Filtrer par catégorie", ["Tous"] + categories)
                if selected_category != "Tous":
                    df_comments = df_comments[df_comments[selected_category] == 1]  # Supposons que les colonnes sont des indicateurs binaires  
        
        with st.sidebar:
            # Filtre par Companies opérateur
            if 'Company' in df_posts.columns and 'ID Post' in df_comments.columns:
                companies = df_posts['Company'].dropna().unique()
                selected_company = st.selectbox("Filtrer par opérateur", ["Tous"] + list(companies))
                if selected_company != "Tous":
                    post_ids_by_company = df_posts[df_posts['Company'] == selected_company]['ID']
                    df_comments = df_comments[df_comments['ID Post'].isin(post_ids_by_company)]
        
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