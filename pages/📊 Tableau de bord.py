import os
import streamlit as st

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
    st.logo("assets/ooredoo_logo.png", size="large", link="http://localhost:8501/")

# --------------------------------------------------------------------------------------------------
# Tous les fonctions
# --------------------------------------------------------------------------------------------------

# Fonction de déconnexion
def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

# Fonction pour afficher le tableau de bord principal
def afficher_tableau():
    st.markdown("<h1 style='text-align: center;'>TABLEAU DE BORD PRINCIPAL</h1>", unsafe_allow_html=True)
    # Ajout de 3 Cards pour les opérateurs
    col1, col2, col3 = st.columns(3, vertical_alignment='center', border=True)

    with col1:
        col11, col12 = st.columns(2, vertical_alignment='center')
        with col11:
            st.image("assets/ooredoo_logo2.png", width=70)
        with col12:
            st.metric(label="Abonnés Facebook", value="6.3M")

    with col2:
        col21, col22 = st.columns(2, vertical_alignment='center')
        with col21:
            st.image("assets/djezzy_logo.png", width=60)
        with col22:
            st.metric(label="Abonnés Facebook", value="6.3M")

    with col3:
        col31, col32 = st.columns(2, vertical_alignment='center')
        with col31:
            st.image("assets/mobilis_logo.png", width=70)
        with col32:
            st.metric(label="Abonnés Facebook", value="3.2M")

# Définition des fonctions pour chaque opérateur
def afficher_tableau_ooredoo():
    st.title("Tableau de bord - Ooredoo")
    # Ajoutez ici le contenu spécifique à Ooredoo

def afficher_tableau_djezzy():
    st.title("Tableau de bord - Djezzy")
    # Ajoutez ici le contenu spécifique à Djezzy

def afficher_tableau_mobilis():
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
            # On utilise st.rerun() pour recharger la page et masquer le formulaire
            st.rerun()
        else:
            st.sidebar.error("Nom d'utilisateur ou mot de passe incorrect.")
else:
    with st.sidebar:
        operateur = st.selectbox(
            "Choisissez l'opérateur pour afficher le tableau de bord correspondant :",
            ["Aucun", "Ooredoo", "Djezzy", "Mobilis"]
        )
        st.write(f"Bienvenue, {st.session_state.username} !")
        st.button("Déconnexion", on_click=logout, use_container_width=True)

    # Appel des fonctions en fonction de l'opérateur sélectionné
    if operateur == "Ooredoo":
        afficher_tableau_ooredoo()
    elif operateur == "Djezzy":
        afficher_tableau_djezzy()
    elif operateur == "Mobilis":
        afficher_tableau_mobilis()
    else:
        afficher_tableau()
        