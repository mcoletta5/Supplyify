import streamlit as st
import sqlite3
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
AFFILIATE_TAG = "michaelcolett-20"
AMAZON_SEARCH_URL = "https://www.amazon.com/s"

# ---------------- DATABASE ----------------
conn = sqlite3.connect("supplyify.db", check_same_thread=False)
c = conn.cursor()

# Users table
c.execute("""CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password TEXT
            )""")
# Supplies table
c.execute("""CREATE TABLE IF NOT EXISTS supplies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                name TEXT,
                amazon_link TEXT,
                amount_left REAL,
                usage_per_day REAL,
                added_on TEXT
            )""")
conn.commit()

# ---------------- SESSION INIT ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "email" not in st.session_state:
    st.session_state.email = ""

# ---------------- PASSWORD VALIDATION ----------------
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
            c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
            if c.fetchone():
                st.session_state.logged_in = True
                st.session_state.email = email
                st.experimental_rerun()
            else:
                st.error("Invalid email or password")

    with tab2:
        st.subheader("Create Account")
        st.info("Password must be at least 8 characters and include 1 uppercase letter")
        new_email = st.text_input("Email", key="create_email")
        new_password = st.text_input("Password", type="password", key="create_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="create_confirm")
        if st.button("Create Account"):
            c.execute("SELECT * FROM users WHERE email=?", (new_email,))
            if c.fetchone():
                st.error("Email already in use")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            elif not validate_password(new_password):
                st.error("Password must be at least 8 characters and include 1 uppercase letter")
            else:
                c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (new_email, new_password))
                conn.commit()
                st.success("Account created! Switch to Login tab to sign in.")
    st.stop()

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

# ---------------- FREE-TEXT SEARCH ----------------
query = st.text_input(
    "Search for a product (type anything, e.g., 'laundry detergent')",
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
            # Add to database with default 1 unit and usage
            c.execute("""INSERT INTO supplies 
                         (email, name, amazon_link, amount_left, usage_per_day, added_on) 
                         VALUES (?, ?, ?, ?, ?, ?)""",
                      (email, query, amazon_link, 1, 1, datetime.now().isoformat()))
            conn.commit()
            st.success(f"Added '{query}' to your list!")

    st.markdown(f"[View on Amazon]({amazon_link}){{:target='_blank'}}", unsafe_allow_html=True)

# ---------------- SUPPLY LIST ----------------
st.subheader("📋 My Supply List")
c.execute("SELECT id, name, amazon_link, amount_left, usage_per_day FROM supplies WHERE email=?", (email,))
rows = c.fetchall()

for row in rows:
    id_, name, amazon_link, amount_left, usage_per_day = row
    st.markdown(f"**{name}**")
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        new_amount = st.number_input("Units left", min_value=0, value=amount_left, key=f"amount_{id_}")
    with col2:
        new_usage = st.number_input("Units used per day", min_value=1, value=usage_per_day, key=f"usage_{id_}")
    with col3:
        if st.button("Remove", key=f"remove_{id_}"):
            c.execute("DELETE FROM supplies WHERE id=?", (id_,))
            conn.commit()
            st.experimental_rerun()

    # Update changes automatically
    if new_amount != amount_left or new_usage != usage_per_day:
        c.execute("UPDATE supplies SET amount_left=?, usage_per_day=? WHERE id=?", (new_amount, new_usage, id_))
        conn.commit()

    # Depletion prediction
    if new_usage > 0:
        days_left = new_amount / new_usage
        reorder_date = datetime.now() + timedelta(days=days_left)
        st.info(f"Estimated days remaining: {days_left:.1f} days (Reorder by {reorder_date.date()})")
        if days_left < 3:
            st.warning(f"⚠️ Low stock alert for {name}! Consider reordering soon.")

    st.markdown(f"[Reorder on Amazon]({amazon_link}){{:target='_blank'}}", unsafe_allow_html=True)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("<small>As an Amazon Associate, Supplyify earns from qualifying purchases.</small>", unsafe_allow_html=True)
