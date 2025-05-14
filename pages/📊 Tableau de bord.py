import streamlit as st
import pandas as pd
import altair as alt
import locale
locale.setlocale(locale.LC_TIME, 'French_France.1252')

#---------------------------- Variables ---------------------------
value_abonnee_ooredoo = "6.3M"
value_abonnee_djezzy = "6.3M"
value_abonnee_mobilis = "3.2M"

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

#--------------------------------------------------------------------------------------------------

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
            
    if all(col in df_posts.columns for col in ['Date', 'Company', 'ID']) and 'ID Post' in df_comments.columns:
        try:
            # Ordre des mois
            month_names = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 
                        'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

            # Préparer les colonnes de date
            df_posts['Date'] = pd.to_datetime(df_posts['Date'], errors='coerce')
            df_posts = df_posts.dropna(subset=['Date'])  # Supprimer les lignes avec des dates non valides
            df_posts['Mois'] = df_posts['Date'].dt.month
            df_posts['Année'] = df_posts['Date'].dt.year

            # Filtres d'affichage
            with st.sidebar:
                # Filtre par année
                selected_year = st.selectbox("Filtrer par année", sorted(df_posts['Année'].dropna().unique()))

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
            df_merged['Mois'] = pd.to_datetime(df_merged['Date'], errors='coerce').dt.to_period('M')

            # Calculer le Score Sentiment par mois
            sentiment_mapping = {'Positif': 1.2, 'Neutre': 0.3, 'Negatif': -1.0}
            df_merged['Score Sentiment'] = df_merged['Sentiments'].map(sentiment_mapping).fillna(0)

            sentiment_par_mois = df_merged.groupby(['Company', 'Mois'])['Score Sentiment'].sum()

            # Calculer le Score Réactions par mois
            df_merged['Score Réactions'] = (
                2.0 * df_merged.get('Nb Love', 0) +
                1.5 * df_merged.get('Nb Care', 0) +
                1.2 * df_merged.get('Nb Like', 0) +
                1.7 * df_merged.get('Nb Wow', 0) +
                0.7 * df_merged.get('Nb Haha', 0) -
                0.5 * df_merged.get('Nb Sad', 0) -
                0.8 * df_merged.get('Nb Angry', 0)
            )
            reactions_par_mois = df_merged.groupby(['Company', 'Mois'])['Score Réactions'].sum()

            # Calculer le Score d'Engagement par mois
            df_merged['Score Engagement'] = (
                (df_merged.get('Nb Love', 0) + df_merged.get('Nb Care', 0) + df_merged.get('Nb Like', 0) +
                 df_merged.get('Nb Wow', 0) + df_merged.get('Nb Haha', 0) + df_merged.get('Nb Sad', 0) +
                 df_merged.get('Nb Angry', 0) + df_merged.get('Nb Commentaires', 0)) /
                df_merged['ID Post'].nunique()
            )
            engagement_par_mois = df_merged.groupby(['Company', 'Mois'])['Score Engagement'].mean()

            # Calculer le Score total par mois
            score_total_par_mois = (
                sentiment_par_mois + reactions_par_mois + engagement_par_mois
            ) / 2

            # Calculer le Score total Annuel pour chaque opérateur
            score_annuel_par_operateur = score_total_par_mois.groupby('Company').sum()
            
            # =======================================
            # Digramme en bar pour les scores annuels
            # =======================================
            
            # Préparer les données pour le graphique
            chart_data = pd.DataFrame({
                'Opérateur': score_annuel_par_operateur.index,
                'Score Annuel': [round(value, 2) for value in score_annuel_par_operateur.values]
            })

            # Définir les couleurs pour chaque opérateur
            color_scale = alt.Scale(
                domain=["Ooredoo", "Djezzy", "Mobilis"],
                range=["#E30613", "#F58220", "#28A745"]
            )

            bar_chart = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X('Opérateur:N', axis=alt.Axis(labelAngle=-45), sort=None),
                y=alt.Y('Score Annuel', title='Score Annuel'),
                color=alt.Color('Opérateur', scale=color_scale),
                opacity=alt.value(0.9)
            ).properties(
                title=alt.TitleParams(
                    text=f"Score total Annuel par Opérateur en {selected_year}",
                    anchor="middle",
                    fontSize=15
                )
            )
            
            # =========================================================
            # Digramme en camembert pour la répartition du Score Global
            # =========================================================
            
            # Calculer le Score Global pour chaque opérateur
            score_total_annuel = score_annuel_par_operateur.sum()
            score_global_par_operateur = (score_annuel_par_operateur / score_total_annuel) * 100

            # Préparer les données pour le diagramme en camembert
            pie_data = pd.DataFrame({
                'Opérateur': score_global_par_operateur.index,
                'Score Global (%)': [round(value, 2) for value in score_global_par_operateur.values]
            })

            # Définir les couleurs pour chaque opérateur
            pie_color_scale = alt.Scale(
                domain=["Ooredoo", "Djezzy", "Mobilis"],
                range=["#E30613", "#F58220", "#28A745"]
            )

            pie_chart = alt.Chart(pie_data).mark_arc(innerRadius=50, outerRadius=120).encode(
                theta=alt.Theta('Score Global (%):Q', stack=True),
                color=alt.Color('Opérateur:N', scale=pie_color_scale),
                tooltip=['Opérateur:N', 'Score Global (%):Q']
            ).properties(
                title=alt.TitleParams(
                    text=f"Répartition du Score Global par Opérateur en {selected_year}",
                    anchor="middle",
                    fontSize=15
                )
            )
            
            col1, col2 = st.columns(2, gap="medium", vertical_alignment="center")
            
            with col1:
                st.altair_chart(bar_chart, use_container_width=True) # Affichage du diagramme en bar
            with col2:
                st.altair_chart(pie_chart, use_container_width=True) # Affichage du diagramme en camembert
            
            # =========================================================
            # Digramme en bar pour l'évolution du Score Total par Mois
            # =========================================================
            
            # Calculer le Score total par mois
            score_total_par_mois = pd.DataFrame({
                'Score Sentiment': sentiment_par_mois,
                'Score Réactions': reactions_par_mois,
                'Score Engagement': engagement_par_mois
            })
            score_total_par_mois['Score Total'] = (score_total_par_mois.sum(axis=1)) / 2
            
            # Préparer les données pour le graphique
            score_total_par_mois = score_total_par_mois.reset_index()
            score_total_par_mois['Mois'] = score_total_par_mois['Mois'].dt.strftime('%B').str.capitalize()
            score_total_par_mois['Score Total'] = score_total_par_mois['Score Total'].round(2)  # Arrondir à 2 décimales

            chart = alt.Chart(score_total_par_mois).mark_bar().encode(
                x=alt.X('Mois:O', title='Mois', axis=alt.Axis(labelAngle=-45), sort=month_names),
                y=alt.Y('Score Total:Q', title='Score Total'),
                color=alt.Color('Company:N',
                                scale=alt.Scale(domain=['Ooredoo', 'Djezzy', 'Mobilis'],
                                                range=['#E30613', '#F58220', '#28A745']),
                                legend=alt.Legend(title="Opérateur")),
                tooltip=['Company', 'Mois', 'Score Total'],
                xOffset='Company',
                opacity=alt.value(0.9),
            ).properties(
                width=700,
                height=400,
                title=alt.TitleParams(
                    text=f"Évolution du Score Total par Mois et par Opérateur en {selected_year}",
                    anchor="middle",
                    fontSize=20
                )
            )
            
            st.altair_chart(chart, use_container_width=True) # Affichage du diagramme en bar
            
            # ============================================================
            # Digramme en lignes pour l'évolution mensuelle du Score Total
            # ============================================================
            
            # Préparer les données pour l'évolution mensuelle du Score Total
            evolution_data = score_total_par_mois.copy()
            evolution_data['Mois'] = pd.Categorical(
                evolution_data['Mois'], categories=month_names, ordered=True
            )
            evolution_data = evolution_data.sort_values(['Mois', 'Company'])

            # Diagramme en lignes pour l'évolution mensuelle du Score Total
            line_chart = alt.Chart(evolution_data).mark_line(point=True).encode(
                x=alt.X('Mois:O', title='Mois', axis=alt.Axis(labelAngle=-45), sort=month_names),
                y=alt.Y('Score Total:Q', title='Score Total', scale=alt.Scale(zero=False)),
                color=alt.Color('Company:N',
                                scale=alt.Scale(domain=['Ooredoo', 'Djezzy', 'Mobilis'],
                                                range=['#E30613', '#F58220', '#28A745']),
                                legend=alt.Legend(title="Opérateur")),
                tooltip=['Company', 'Mois', 'Score Total']
            ).properties(
                width=800,
                height=400,
                title=alt.TitleParams(
                    text=f"Évolution mensuelle du Score Total par Opérateur en {selected_year}",
                    anchor="middle",
                    fontSize=20
                )
            )

            st.altair_chart(line_chart, use_container_width=True)  # Affichage du diagramme en lignes
        
        except Exception as e:
            st.error(f"Erreur lors de l'application des filtres : {str(e)}")

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
        st.markdown("""
            <footer style="text-align: center; margin-top: 50px; font-size: 0.9rem; color: #888;">
                <hr style="border: none; border-top: 1px solid #ccc; margin: 10px 0;">
                <p>&copy; OOREDOO ALGERIA | Développé par <strong>OUARAS Khelil Rafik</strong></p>
            </footer>
        """, unsafe_allow_html=True)