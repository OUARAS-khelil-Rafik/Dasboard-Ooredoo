import streamlit as st
import pandas as pd
import altair as alt
import locale
locale.setlocale(locale.LC_TIME, 'French_France.1252')

#---------------------------- Variables ---------------------------
value_abonnee_ooredoo = "6.3M"
value_abonnee_djezzy = "6.3M"
value_abonnee_mobilis = "3.2M"

#-------------------------------------------------------------------

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

# Fonction pour afficher le tableau de bord principal
def afficher_tableau(value_abonnee_ooredoo, value_abonnee_djezzy, value_abonnee_mobilis, df_comments, df_posts):
    st.markdown("<h1 style='text-align: center;'>TABLEAU DE BORD PRINCIPAL</h1>", unsafe_allow_html=True)
    # Ajout de 3 Cards pour les opérateurs
    col1, col2, col3 = st.columns(3, border=True, vertical_alignment="center")

    with col1:
        col11, col12 = st.columns([1, 3])
        with col11:
            st.image("assets/ooredoo_logo2.png", width=70)
        with col12:
            st.markdown(f"""
                <div style="text-align: center;">
                    <span style="font-size: 1rem; font-weight: bold;">Abonnés Facebook</span><br>
                    <span style="font-size: 2rem; font-weight: bold; color: #E30613;">{value_abonnee_ooredoo}</span>
                </div>
            """, unsafe_allow_html=True)

    with col2:
        col21, col22 = st.columns([1, 3])
        with col21:
            st.image("assets/djezzy_logo.png", width=55)
        with col22:
            st.markdown(f"""
                <div style="text-align: center;">
                    <span style="font-size: 1rem; font-weight: bold;">Abonnés Facebook</span><br>
                    <span style="font-size: 2rem; font-weight: bold; color: #F58220;">{value_abonnee_djezzy}</span>
                </div>
            """, unsafe_allow_html=True)

    with col3:
        col31, col32 = st.columns([1, 3])
        with col31:
            st.image("assets/mobilis_logo.png", width=70)
        with col32:
            st.markdown(f"""
                <div style="text-align: center;">
                    <span style="font-size: 1rem; font-weight: bold;">Abonnés Facebook</span><br>
                    <span style="font-size: 2rem; font-weight: bold; color: #28A745;">{value_abonnee_mobilis}</span>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("")
            
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

            # Fusionner les datasets pour associer les commentaires aux publications
            df_merged = pd.merge(df_comments, df_filtered_posts, left_on="ID Post", right_on="ID", suffixes=('_comment', '_post'))

            # Ajouter une colonne pour le mois et l'année
            df_merged['Mois'] = pd.to_datetime(df_merged['Date']).dt.to_period('M')

            # Calculer le Score Sentiment par mois
            df_merged['Score Sentiment'] = (1.0 * (df_merged['Sentiments'] == 'Positif') +
                                            0.5 * (df_merged['Sentiments'] == 'Neutre') -
                                            1.0 * (df_merged['Sentiments'] == 'Negatif'))
            sentiment_par_mois = df_merged.groupby(['Company', 'Mois'])['Score Sentiment'].sum()

            # Calculer le Score Réactions par mois
            df_merged['Score Réactions'] = (2.0 * df_merged['Nb Love'] +
                                            1.2 * df_merged['Nb Care'] +
                                            1.0 * df_merged['Nb Like'] +
                                            1.5 * df_merged['Nb Wow'] +
                                            0.5 * df_merged['Nb Haha'] -
                                            0.3 * df_merged['Nb Sad'] -
                                            0.5 * df_merged['Nb Angry'])
            reactions_par_mois = df_merged.groupby(['Company', 'Mois'])['Score Réactions'].sum()

            # Calculer le Score total par mois
            posts_par_mois = df_merged.groupby(['Company', 'Mois'])['ID Post'].nunique()
            score_total_par_mois = (sentiment_par_mois + reactions_par_mois) / posts_par_mois

            # Calculer le Score total Annuel pour chaque opérateur
            score_annuel_par_operateur = score_total_par_mois.groupby('Company').sum()

            # Diagramme en bar pour les scores annuels
            chart_data = pd.DataFrame({
                'Opérateur': score_annuel_par_operateur.index,
                'Score Annuel': [f"{value:.2f}" for value in score_annuel_par_operateur.values]
            })
            # Définir les couleurs pour chaque opérateur
            color_scale = alt.Scale(
                domain=["Ooredoo", "Djezzy", "Mobilis"],
                range=["#E30613", "#F58220", "#28A745"]
            )

            bar_chart = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('Opérateur:N', axis=alt.Axis(labelAngle=-45), sort=None),
                y=alt.Y('Score Annuel:Q', title='Score Annuel'),
                color=alt.Color('Opérateur', scale=color_scale),
                opacity=alt.value(0.9)
            ).properties(
                title=alt.TitleParams(
                    text=f"Score total Annuel par Opérateur en {selected_year}",
                    anchor="middle",
                    fontSize=27
                )
            )

            st.altair_chart(bar_chart, use_container_width=True)
        except Exception as e:
            st.error(f"Une erreur s'est produite lors de l'application des filtres : {e}")

# Définition des fonctions pour chaque opérateur
def afficher_tableau_ooredoo(df_comments, df_posts):
    st.title("Tableau de bord - Ooredoo")
    # Ajoutez ici le contenu spécifique à Ooredoo

def afficher_tableau_djezzy(df_comments, df_posts):
    st.title("Tableau de bord - Djezzy")
    # Ajoutez ici le contenu spécifique à Djezzy

def afficher_tableau_mobilis(df_comments, df_posts):
    st.title("Tableau de bord - Mobilis")
    # Ajoutez ici le contenu spécifique à Mobilis

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
            # On utilise st.experimental_rerun() pour recharger la page et masquer le formulaire
            st.rerun()
        else:
            st.sidebar.error("Nom d'utilisateur ou mot de passe incorrect.")
else:
    with st.sidebar:
        st.write(f"Bienvenue, {st.session_state.username} !")
        operateur = st.selectbox(
            "Choisissez l'opérateur pour afficher le tableau de bord correspondant :",
            ["All", "Ooredoo", "Djezzy", "Mobilis"]
        )

    # Appel des fonctions en fonction de l'opérateur sélectionné
    if operateur == "Ooredoo":
        afficher_tableau_ooredoo(df_comments, df_posts)
    elif operateur == "Djezzy":
        afficher_tableau_djezzy(df_comments, df_posts)
    elif operateur == "Mobilis":
        afficher_tableau_mobilis(df_comments, df_posts)
    else:
        afficher_tableau(value_abonnee_ooredoo, value_abonnee_djezzy, value_abonnee_mobilis, df_comments, df_posts)

    with st.sidebar:
        st.button("Déconnexion", on_click=logout, use_container_width=True)
