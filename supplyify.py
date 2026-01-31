import streamlit as st
import urllib.parse
from datetime import datetime, timedelta

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Supplyify", page_icon="🛒", layout="centered")

# ---------------- STYLE ----------------
st.markdown("""
<style>
.stApp { background-color: white; color: black; }
h1, h2, h3, h4, p, label { color: black !important; }
input { color: black !important; }
</style>
""", unsafe_allow_html=True)

# ---------------- AMAZON CONFIG ----------------
AFFILIATE_TAG = "michaelcolett-20"   # <-- your Amazon Associate ID
AMAZON_SEARCH_URL = "https://www.amazon.com/s"

# ---------------- USER LOGIN ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = ""
if "supply_list" not in st.session_state:
    st.session_state.supply_list = []

# Login form
if not st.session_state.logged_in:
    st.title("🔑 Login to Supplyify")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        # Simple password check (for demo purposes)
        if email and password == "password123":  # replace with real password logic
            st.session_state.logged_in = True
            st.session_state.email = email
            st.success(f"Logged in as {email}")
        else:
            st.error("Invalid email or password")
    st.stop()  # stop script until login
else:
    st.sidebar.write(f"Logged in as: {st.session_state.email}")
    if st.sidebar.button("Log out"):
        st.session_state.logged_in = False
        st.session_state.email = ""
        st.session_state.supply_list = []
        st.experimental_rerun()

# ---------------- HEADER ----------------
st.title("🛒 Supplyify")
st.subheader("Search and track your supplies, reorder on Amazon.")

# ---------------- AMAZON SEARCH ----------------
query = st.text_input(
    "Search for a product (e.g., cleaning wipes, shampoo, protein powder)",
    placeholder="Start typing..."
)

if query:
    encoded_query = urllib.parse.quote_plus(query)
    amazon_link = f"{AMAZON_SEARCH_URL}?k={encoded_query}&tag={AFFILIATE_TAG}"

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**{query}**")
    with col2:
        if st.button("Add to My List", key=query):
            # Default amount and usage for prediction
            st.session_state.supply_list.append({
                "name": query,
                "amazon_link": amazon_link,
                "amount_left": 1,
                "usage_per_day": 1,
                "added_on": datetime.now()
            })
            st.success(f"Added {query} to your supply list!")

    # Direct Amazon search
    st.markdown(f"[View on Amazon]({amazon_link}){{:target='_blank'}}", unsafe_allow_html=True)

# ---------------- SUPPLY LIST ----------------
if st.session_state.supply_list:
    st.subheader("📋 My Supply List")
    for idx, item in enumerate(st.session_state.supply_list):
        st.markdown(f"**{item['name']}**")
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            # Update amount left
            item["amount_left"] = st.number_input(
                "Units left",
                min_value=0,
                value=item.get("amount_left", 1),
                key=f"amount_{idx}"
            )
        with col2:
            # Update usage per day
            item["usage_per_day"] = st.number_input(
                "Usage per day",
                min_value=1,
                value=item.get("usage_per_day", 1),
                key=f"usage_{idx}"
            )
        with col3:
            # Remove item button
            if st.button("Remove", key=f"remove_{idx}"):
                st.session_state.supply_list.pop(idx)
                st.experimental_rerun()

        # Predict depletion
        if item["usage_per_day"] > 0:
            days_left = item["amount_left"] / item["usage_per_day"]
            reorder_date = datetime.now() + timedelta(days=days_left)
            st.info(f"Estimated days remaining: {days_left:.1f} days (Reorder by {reorder_date.date()})")
        # Show Amazon link
        st.markdown(f"[Reorder on Amazon]({item['amazon_link']}){{:target='_blank'}}", unsafe_allow_html=True)

# ---------------- FOOTER / DISCLOSURE ----------------
st.markdown("---")
st.markdown(
    "<small>As an Amazon Associate, Supplyify earns from qualifying purchases.</small>",
    unsafe_allow_html=True
)
