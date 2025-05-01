import streamlit as st

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Ooredoo",
    page_icon="assets/ooredoo_logo.png",
    layout="centered",
)

st.markdown("""
    <style>
        [class="st-emotion-cache-1tuwfdi edtmxes19"] {
            display: none !important;
        }
        [class="st-emotion-cache-1gb1rig edtmxes3"] {
            display: none !important;
        }
        [class="st-emotion-cache-1xgtwnd edtmxes10"] {
            display: none !important;
        }
        [class="st-emotion-cache-uzxc3z edtmxes19"] {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

# Logo + titre
col1, col2 = st.columns([1, 3])
with col1:
    st.sidebar.image("assets/ooredoo_logo.png", width=90)
with col2:
    st.sidebar.markdown("<h1 style='text-align: center;'>Ooredoo</h1>", unsafe_allow_html=True)

st.title("Bienvenue dans le Dashboard Ooredoo")
