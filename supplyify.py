import streamlit as st
import urllib.parse

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Supplyify",
    page_icon="🛒",
    layout="centered"
)

# ---------------- STYLING ----------------
st.markdown("""
<style>
.stApp {
    background-color: white;
    color: black;
}
h1, h2, h3, h4, p, label {
    color: black !important;
}
input {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

# ---------------- AMAZON CONFIG ----------------
AFFILIATE_TAG = "YOURTAG-20"   # <-- replace later
AMAZON_SEARCH_URL = "https://www.amazon.com/s"

# ---------------- HEADER ----------------
st.title("🛒 Supplyify")
st.subheader("Smart reordering. Powered by Amazon.")

st.write(
    "Search everyday products, save time, and reorder easily when you run low."
)

# ---------------- SEARCH ----------------
query = st.text_input(
    "Search for a product (ex: cleaning wipes, shampoo, protein powder)",
    placeholder="Start typing..."
)

if query:
    encoded_query = urllib.parse.quote_plus(query)
    amazon_link = f"{AMAZON_SEARCH_URL}?k={encoded_query}&tag={AFFILIATE_TAG}"

    st.markdown("### 🔍 Amazon Results")
    st.link_button(
        "View results on Amazon",
        amazon_link,
        use_container_width=True
    )

    st.info("Purchases made through this link support Supplyify 💙")

# ---------------- FOOTER / DISCLOSURE ----------------
st.markdown("---")
st.markdown(
    "<small>As an Amazon Associate, Supplyify earns from qualifying purchases.</small>",
    unsafe_allow_html=True
)
