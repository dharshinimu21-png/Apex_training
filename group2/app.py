import streamlit as st
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# ---------------- PAGE SETTING ----------------
st.set_page_config(page_title="Bank Management System", page_icon="🏦")

# ---------------- MYSQL CONNECTION ----------------
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)
cursor = conn.cursor()

# ---------------- SESSION ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"

if "role" not in st.session_state:
    st.session_state.role = ""

if "username" not in st.session_state:
    st.session_state.username = ""

# =====================================================
# HOME PAGE
# =====================================================
if st.session_state.page == "home":

    st.markdown(
        "<h1 style='text-align:center;color:green;'>🏦 BANK MANAGEMENT SYSTEM</h1>",
        unsafe_allow_html=True
    )

    st.subheader("Welcome to Our Bank")

    if st.button("🔐 Login", use_container_width=True):
        st.session_state.page = "login"
        st.rerun()

# =====================================================
# LOGIN PAGE
# =====================================================
elif st.session_state.page == "login":

    st.title("🔑 Login Page")

    role = st.selectbox("Login As", ["Admin", "User"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):

        # ADMIN LOGIN
        if role == "Admin":

            if username == "admin" and password == "admin123":
                st.success("Admin Login Successful!")
                st.session_state.role = "admin"
                st.session_state.page = "bank"
                #st.rerun()


            else:
                st.error("Invalid Admin Username or Password")

        # USER LOGIN
        else:

            cursor.execute(
                "SELECT * FROM account WHERE customer_name=%s AND password=%s",
                (username, password)
            )
            user = cursor.fetchone()

            if user:
                st.success("User Login Successful!")
                st.session_state.role = "user"
                st.session_state.username = username
                st.session_state.page = "bank"
                #st.rerun()

            else:
                st.error("Invalid Username or Password")

# =====================================================
# BANK PAGE
# =====================================================
elif st.session_state.page == "bank":

    st.title("🏦 BANK MANAGEMENT SYSTEM")
    st.sidebar.success(f"Welcome {st.session_state.role}")

    # ---------------- ADMIN MENU ----------------
    if st.session_state.role == "admin":

        menu = st.sidebar.radio(
            "Admin Menu",
            [
                "Create Account",
                "Change User Password",
                "View All Accounts"
            ]
        )

    # ---------------- USER MENU ----------------
    else:

        menu = st.sidebar.radio(
            "User Menu",
            [
                "Deposit Money",
                "Withdraw Money",
                "Check Balance"
            ]
        )

    # =====================================================
    # CREATE ACCOUNT
    # =====================================================
    if menu == "Create Account":

        st.header("Create New Account")

        name = st.text_input("Customer Name")
        pwd = st.text_input("Create Password", type="password")
        balance = st.number_input("Initial Balance", min_value=0.0)

        if st.button("Create Account"):

            cursor.execute(
                """
                INSERT INTO account(customer_name, password, balance)
                VALUES(%s, %s, %s)
                """,
                (name, pwd, balance)
            )

            conn.commit()

            st.success("Account Created Successfully!")
            st.write("Account Number :", cursor.lastrowid)

    # =====================================================
    # CHANGE PASSWORD (OLD PASSWORD + NEW PASSWORD)
    # =====================================================
    elif menu == "Change User Password":

        st.header("🔑 Change User Password")

        acc_no = st.number_input("Account Number", min_value=1, step=1)

        old_pwd = st.text_input("Old Password", type="password")
        new_pwd = st.text_input("New Password", type="password")
        confirm_pwd = st.text_input("Confirm New Password", type="password")

        if st.button("Update Password"):

            # Get old password from DB
            cursor.execute(
                "SELECT password FROM account WHERE account_no=%s",
                (acc_no,)
            )

            data = cursor.fetchone()

            if data:

                if data[0] == old_pwd:

                    if new_pwd == confirm_pwd:

                        cursor.execute(
                            "UPDATE account SET password=%s WHERE account_no=%s",
                            (new_pwd, acc_no)
                        )

                        conn.commit()
                        st.success("✅ Password Updated Successfully!")

                    else:
                        st.error("❌ New Password and Confirm Password do not match!")

                else:
                    st.error("❌ Old Password is Incorrect!")

            else:
                st.error("❌ Account Not Found!")

    # =====================================================
    # VIEW ALL ACCOUNTS (PASSWORD SHOWN TO ADMIN)
    # =====================================================
    elif menu == "View All Accounts":

        st.header("📋 All Customer Accounts")

        cursor.execute("""
            SELECT account_no, customer_name, password, balance
            FROM account
        """)

        records = cursor.fetchall()

        if records:
            st.table(records)
        else:
            st.warning("No Accounts Available!")

    # =====================================================
    # DEPOSIT MONEY
    # =====================================================
    elif menu == "Deposit Money":

        st.header("Deposit Money")

        acc_no = st.number_input("Account Number", min_value=1, step=1)
        amount = st.number_input("Deposit Amount", min_value=1.0)

        if st.button("Deposit"):

            cursor.execute(
                "UPDATE account SET balance = balance + %s WHERE account_no=%s",
                (amount, acc_no)
            )

            conn.commit()

            if cursor.rowcount > 0:

                cursor.execute(
                    "SELECT balance FROM account WHERE account_no=%s",
                    (acc_no,)
                )

                bal = cursor.fetchone()[0]

                st.success(f"₹{amount} Deposited Successfully!")
                st.write("Current Balance : ₹", bal)

            else:
                st.error("Account Not Found!")

    # =====================================================
    # WITHDRAW MONEY
    # =====================================================
    elif menu == "Withdraw Money":

        st.header("Withdraw Money")

        acc_no = st.number_input("Account Number", min_value=1, step=1)
        amount = st.number_input("Withdraw Amount", min_value=1.0)

        if st.button("Withdraw"):

            cursor.execute(
                "SELECT balance FROM account WHERE account_no=%s",
                (acc_no,)
            )

            data = cursor.fetchone()

            if data:

                if data[0] >= amount:

                    cursor.execute(
                        "UPDATE account SET balance = balance - %s WHERE account_no=%s",
                        (amount, acc_no)
                    )

                    conn.commit()

                    cursor.execute(
                        "SELECT balance FROM account WHERE account_no=%s",
                        (acc_no,)
                    )

                    bal = cursor.fetchone()[0]

                    st.success(f"₹{amount} Withdrawn Successfully!")
                    st.write("Current Balance : ₹", bal)

                else:
                    st.error("Insufficient Balance!")

            else:
                st.error("Account Not Found!")

    # =====================================================
    # CHECK BALANCE
    # =====================================================
    elif menu == "Check Balance":

        st.header("Check Balance")

        cursor.execute(
            "SELECT account_no, balance FROM account WHERE customer_name=%s",
            (st.session_state.username,)
        )

        record = cursor.fetchone()

        if record:
            st.write("Customer Name :", st.session_state.username)
            st.write("Account Number :", record[0])
            st.write("Current Balance : ₹", record[1])
        else:
            st.error("Account Not Found!")

    # =====================================================
    # LOGOUT
    # =====================================================
    st.sidebar.markdown("---")

    if st.sidebar.button("🚪 Logout", use_container_width=True):

        st.session_state.page = "home"
        st.session_state.role = ""
        st.session_state.username = ""

        st.success("Logged Out Successfully!")
        st.rerun()

# ---------------- CLOSE CONNECTION ----------------
cursor.close()
conn.close()