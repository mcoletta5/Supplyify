import streamlit as st
import urllib.parse
from datetime import datetime, timedelta
import re

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

# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = ""
if "users" not in st.session_state:
    st.session_state.users = {}  # stores email:password
if "supply_list" not in st.session_state:
    st.session_state.supply_list = {}

# ---------------- FUNCTIONS ----------------
def validate_password(password):
    return len(password) >= 8 and re.search(r"[A-Z]", password)

# ---------------- LOGIN / CREATE ACCOUNT ----------------
if not st.session_state.logged_in:
    st.title("🔑 Welcome to Supplyify")
    tab1, tab2 = st.tabs(["Login", "Create Account"])

    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            if email in st.session_state.users and st.session_state.users[email] == password:
                st.session_state.logged_in = True
                st.session_state.email = email
                st.success(f"Logged in as {email}")
            else:
                st.error("Invalid email or password")

    with tab2:
        st.subheader("Create Account")
        new_email = st.text_input("Email", key="create_email")
        new_password = st.text_input("Password", type="password", key="create_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="create_confirm")
        if st.button("Create Account"):
            if new_email in st.session_state.users:
                st.error("Email already in use")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif not validate_password(new_password):
                st.error("Password must be at least 8 characters and contain 1 uppercase letter")
            else:
                st.session_state.users[new_email] = new_password
                st.session_state.supply_list[new_email] = []
                st.success("Account created! Please switch to the Login tab to log in.")
    st.stop()  # stop script until logged in

# ---------------- LOGGED-IN APP ----------------
email = st.session_state.email
st.sidebar.write(f"Logged in as: {email}")
if st.sidebar.button("Log out"):
    st.session_state.logged_in = False
    st.session_state.email = ""
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

    col1, col2 = st.columns([3,1])
    with col1:
        st.markdown(f"**{query}**")
    with col2:
        if st.button("Add to My List", key=query):
            st.session_state.supply_list[email].append({
                "name": query,
                "amazon_link": amazon_link,
                "amount_left": 1,
                "usage_per_day": 1,
                "added_on": datetime.now()
            })
            st.success(f"Added {query} to your list!")

    # Direct Amazon search
    st.markdown(f"[View on Amazon]({amazon_link}){{:target='_blank'}}", unsafe_allow_html=True)

# ---------------- SUPPLY LIST ----------------
user_list = st.session_state.supply_list[email]
if user_list:
    st.subheader("📋 My Supply List")
    for idx, item in enumerate(user_list):
        st.markdown(f"**{item['name']}**")
        col1, col2, col3 = st.columns([2,1,1])
        with col1:
            item["amount_left"] = st.number_input(
                "Units left",
                min_value=0,
                value=item.get("amount_left",1),
                key=f"amount_{idx}"
            )
        with col2:
            item["usage_per_day"] = st.number_input(
                "Usage per day",
                min_value=1,
                value=item.get("usage_per_day",1),
                key=f"usage_{idx}"
            )
        with col3:
            if st.button("Remove", key=f"remove_{idx}"):
                user_list.pop(idx)
                st.experimental_rerun()

        # Predict depletion
        if item["usage_per_day"] > 0:
            days_left = item["amount_left"] / item["usage_per_day"]
            reorder_date = datetime.now() + timedelta(days=days_left)
            st.info(f"Estimated days remaining: {days_left:.1f} days (Reorder by {reorder_date.date()})")
        st.markdown(f"[Reorder on Amazon]({item['amazon_link']}){{:target='_blank'}}", unsafe_allow_html=True)

# ---------------- FOOTER / DISCLOSURE ----------------
st.markdown("---")
st.markdown(
    "<small>As an Amazon Associate, Supplyify earns from qualifying purchases.</small>",
    unsafe_allow_html=True
)
