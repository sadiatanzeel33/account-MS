import streamlit as st
from auth import hash_password, verify_password
from db import (
    init_db, register_user, get_user_by_username,
    get_account_balance, update_balance,
    get_transaction_history
)

st.set_page_config(page_title="🏦 Bank Account System", layout="centered")

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

menu = ["Login", "Register", "Dashboard"]
choice = st.sidebar.selectbox("Navigation", menu)

# ✅ Registration Page
if choice == "Register":
    st.subheader("🔐 Register New Account")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Register"):
        if password != confirm_password:
            st.error("Passwords do not match!")
        elif register_user(username, password, email):
            st.success("Account created successfully. You can now login.")
        else:
            st.error("Username already exists.")

# ✅ Login Page
elif choice == "Login":
    st.subheader("👤 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = get_user_by_username(username)
        if user and verify_password(password, user[2]):
            st.success(f"Welcome, {username}!")
            st.session_state.logged_in = True
            st.session_state.user = user
        else:
            st.error("Invalid credentials")

# ✅ Dashboard Page
elif choice == "Dashboard":
    if not st.session_state.logged_in:
        st.warning("Please log in first.")
        st.stop()

    user = st.session_state.user
    st.subheader(f"🏠 Dashboard: {user[1]}")
    balance = get_account_balance(user[0])
    st.metric("💰 Account Balance", f"PKR{balance:.2f}")

    st.divider()

    col1, col2, col3 = st.columns(3)

    # 📥 Deposit
    with col1:
        st.subheader("📥 Deposit")
        deposit_amount = st.number_input("Amount", min_value=1.0, step=1.0, key="deposit")
        if st.button("Deposit"):
            if update_balance(user[0], deposit_amount, "deposit"):
                st.success("Deposit successful.")
                st.rerun()

    # 📤 Withdraw
    with col2:
        st.subheader("📤 Withdraw")
        withdraw_amount = st.number_input("Withdraw Amount", min_value=1.0, step=1.0, key="withdraw")
        if st.button("Withdraw"):
            if update_balance(user[0], withdraw_amount, "withdraw"):
                st.success("Withdrawal successful.")
                st.rerun()
            else:
                st.error("Insufficient balance.")

    # 🛒 Purchase
    with col3:
        st.subheader("🛒 Purchase")
        item_name = st.text_input("Item Name")
        purchase_amount = st.number_input("Purchase Amount", min_value=1.0, step=1.0, key="purchase")
        if st.button("Make Purchase"):
            if update_balance(user[0], purchase_amount, "purchase", item_name):
                st.success(f"Purchased: {item_name}")
                st.rerun()
            else:
                st.error("Insufficient balance.")

    st.divider()
    st.subheader("📜 Transaction History")
    transactions = get_transaction_history(user[0])
    if transactions:
        st.table(transactions)
    else:
        st.info("No transactions yet.")


      