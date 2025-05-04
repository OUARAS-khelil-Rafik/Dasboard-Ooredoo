import streamlit as st
import pandas as pd
import altair as alt
import locale
locale.setlocale(locale.LC_TIME, 'French_France.1252')

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

#--------------------------------------------------------------------------------------------------
# Data Publications
#--------------------------------------------------------------------------------------------------

# Chargement du dataset
try:
    df = pd.read_csv("data/posts_df_classified.csv", encoding='utf-8', index_col=0)
except FileNotFoundError:
    st.error("Le fichier 'data/posts_df_classified.csv' est introuvable. Veuillez vérifier le chemin.")
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

def afficher_tableau_pub(df):
    st.markdown("<h1 style='text-align: center;'>TABLEAU DE BORD PUBLICATIONS</h1>", unsafe_allow_html=True)
    st.markdown("")

    if 'Date' in df.columns and 'Company' in df.columns:
        try:
            # Ordre des mois
            month_names = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                           'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

            # Préparer les colonnes de date
            df['Date'] = pd.to_datetime(df['Date'])
            df['Mois'] = df['Date'].dt.month
            df['Année'] = df['Date'].dt.year

            # Filtres AVANT affichage des cards

            selected_month_range = st.select_slider(
                "Filtrer par mois",
                options=list(range(1, 13)),
                value=(1, 12),
                format_func=lambda x: month_names[x - 1]
            )
            start_month, end_month = selected_month_range

            with st.sidebar:
                selected_year = st.selectbox("Filtrer par année", sorted(df['Année'].unique().tolist()))

            # Application des filtres
            df_filtered = df[
                (df['Mois'] >= start_month) &
                (df['Mois'] <= end_month) &
                (df['Année'] == selected_year)
            ]

            # Calcul des publications filtrées
            nb_pub_ooredoo = df_filtered[df_filtered['Company'] == 'Ooredoo'].shape[0]
            nb_pub_djezzy = df_filtered[df_filtered['Company'] == 'Djezzy'].shape[0]
            nb_pub_mobilis = df_filtered[df_filtered['Company'] == 'Mobilis'].shape[0]

            # Affichage des Cards
            col1, col2, col3 = st.columns(3, border=True, vertical_alignment="center")

            with col1:
                col11, col12 = st.columns([1, 3])
                with col11:
                    st.image("assets/ooredoo_logo2.png", width=70)
                with col12:
                    st.markdown(f"""
                        <div style="text-align: center;">
                            <span style="font-size: 0.9rem; font-weight: bold;">Nombre total des publications</span><br>
                            <span style="font-size: 2rem; font-weight: bold; color: #FF0000;">{nb_pub_ooredoo}</span>
                        </div>
                    """, unsafe_allow_html=True)

            with col2:
                col21, col22 = st.columns([1, 3])
                with col21:
                    st.image("assets/djezzy_logo.png", width=55)
                with col22:
                    st.markdown(f"""
                        <div style="text-align: center;">
                            <span style="font-size: 0.9rem; font-weight: bold;">Nombre total des publications</span><br>
                            <span style="font-size: 2rem; font-weight: bold; color: #FF0000;">{nb_pub_djezzy}</span>
                        </div>
                    """, unsafe_allow_html=True)

            with col3:
                col31, col32 = st.columns([1, 3])
                with col31:
                    st.image("assets/mobilis_logo.png", width=70)
                with col32:
                    st.markdown(f"""
                        <div style="text-align: center;">
                            <span style="font-size: 0.9rem; font-weight: bold;">Nombre total des publications</span><br>
                            <span style="font-size: 2rem; font-weight: bold; color: #FF0000;">{nb_pub_mobilis}</span>
                        </div>
                    """, unsafe_allow_html=True)

            st.markdown("")
            st.markdown("")

            # === Graphique Score des Réactions ===
            required_columns = ['Nb Love', 'Nb Care', 'Nb Like', 'Nb Wow', 'Nb Haha', 'Nb Sad', 'Nb Angry']
            if all(col in df.columns for col in required_columns):
                df_filtered['Reaction_Score'] = (
                    2.0 * df_filtered['Nb Love'] +
                    1.5 * df_filtered['Nb Wow'] +
                    1.2 * df_filtered['Nb Care'] +
                    1.0 * df_filtered['Nb Like'] +
                    0.5 * df_filtered['Nb Haha'] -
                    0.3 * df_filtered['Nb Sad'] -
                    0.5 * df_filtered['Nb Angry']
                )

                grouped = df_filtered.groupby(['Mois', 'Company'], as_index=False)['Reaction_Score'].sum()
                grouped['Mois'] = grouped['Mois'].apply(lambda x: month_names[x - 1])
                grouped['Mois'] = pd.Categorical(grouped['Mois'], categories=month_names, ordered=True)
                grouped = grouped.sort_values(['Mois', 'Company'])
                
                chart = alt.Chart(grouped).mark_bar().encode(
                    x=alt.X('Mois:O', title='Mois', axis=alt.Axis(labelAngle=-45), sort=month_names),
                    y=alt.Y('Reaction_Score:Q', title='Score des Réactions'),
                    color=alt.Color('Company:N',
                                    scale=alt.Scale(domain=['Ooredoo', 'Djezzy', 'Mobilis'],
                                                    range=['#E30613', '#F58220', '#007A33']),
                                    legend=alt.Legend(title="Opérateur")),
                    tooltip=['Company', 'Mois', 'Reaction_Score'],
                    xOffset='Company'
                ).properties(
                    width=700,
                    height=400,
                    title=f"Score des Réactions par Mois et par Opérateur en {selected_year}"
                )

                st.altair_chart(chart, use_container_width=True)
            else:
                st.error("Les colonnes nécessaires pour calculer le score des réactions sont manquantes.")

        except Exception as e:
            st.error(f"Erreur : {e}")
    else:
        st.error("Les colonnes 'Date' et 'Company' sont nécessaires.")

    
def afficher_data_pub(df):
    st.markdown("<h1 style='text-align: center;'>DONNÉES PUBLICATIONS</h1>", unsafe_allow_html=True)

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
        afficher_data_pub(df)
    else:
        afficher_tableau_pub(df)
    
    with st.sidebar:
        st.button("Déconnexion", on_click=logout, use_container_width=True)