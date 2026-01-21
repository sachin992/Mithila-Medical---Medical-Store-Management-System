
import streamlit as st
from b import execute_custom_query
from admin_setup import verify_login_with_role, signup_admin
import hashlib
import sqlite3

# ================ PAGE CONFIG ================
st.set_page_config(
    page_title="Mithila Medical - Login/Signup",
    page_icon="Ⓜ️",
    layout="wide"
)

# ================ CUSTOM CSS ================
st.markdown("""
<style>
    /* Main background */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #e2eaf4 0%, #cbd9e9 100%);
    }

    /* Target the specific column containers for background colors */
    [data-testid="column"]:nth-of-type(1) [data-testid="stVerticalBlock"] {
        background: linear-gradient(180deg, #7ec9c9 0%, #a4d49c 100%);
        padding: 40px 30px;
        border-radius: 20px;
        color: white;
    }

    [data-testid="column"]:nth-of-type(3) [data-testid="stVerticalBlock"] {
        background: linear-gradient(180deg, #7eb6f3 0%, #b19ef3 100%);
        padding: 40px 30px;
        border-radius: 20px;
        color: white;
    }

    /* Make text input labels white */
    .stTextInput label, .stForm p {
        color: white !important;
        font-weight: 600 !important;
    }

    /* Branding styles */
    .brand-section { text-align: center; margin-bottom: 20px; }
    .brand-name { color: #1a4d8c; font-size: 2.5em; font-weight: 800; margin: 0; }
    
    /* Bottom Banner styling */
    .footer-banner-box {
        background: white;
        padding: 15px 40px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-top: -25px;
        z-index: 100;
        font-weight: 700;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

# ================ DATABASE SETUP FOR AUTH ================
def init_auth_db():
    conn = sqlite3.connect("auth.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'customer',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def signup_user(email: str, password: str, full_name: str) -> tuple[bool, str]:
    """Register a customer"""
    try:
        conn = sqlite3.connect("auth.db")
        cursor = conn.cursor()
        
        hashed_pw = hash_password(password)
        cursor.execute(
            "INSERT INTO users (email, password, full_name, role) VALUES (?, ?, ?, ?)",
            (email, hashed_pw, full_name, 'customer')
        )
        conn.commit()
        conn.close()
        return True, "Signup successful! Please login."
    except sqlite3.IntegrityError:
        return False, "Email already registered."
    except Exception as e:
        return False, f"Error: {str(e)}"

# ================ INITIALIZATION ================
init_auth_db()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
    st.session_state["user_email"] = None
    st.session_state["user_id"] = None
    st.session_state["user_full_name"] = None
    st.session_state["user_role"] = "customer"

# ================ SHOW HOME PAGE OR LOGIN PAGE ================
if st.session_state["authenticated"]:
    # ================ HOME PAGE ================
    st.set_page_config(page_title="Mithila Medical - Home", layout="wide")
    
    st.markdown("""
        <style>
        /* Main Background */
        .stApp {
            background: linear-gradient(135deg, #e0eafc 0%, #cfdef3 100%);
        }

        /* Header Styling */
        .header-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px 5%;
            background-color: white;
            border-radius: 0 0 20px 20px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }

        /* Card Styling */
        .card {
            padding: 30px;
            border-radius: 25px;
            color: white;
            height: 450px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-10px);
        }

        .card-search { background: linear-gradient(180deg, #86d9d0 0%, #a2c38d 100%); }
        .card-order { background: linear-gradient(180deg, #7eb6f0 0%, #9198e5 100%); }
        .card-track { background: linear-gradient(180deg, #8eb0f3 0%, #b194f4 100%); }

        /* Input Fields */
        input {
            border-radius: 10px !important;
            border: none !important;
            padding: 10px !important;
            width: 100%;
            margin-bottom: 10px;
        }

        /* Buttons */
        .custom-button {
            background-color: rgba(255, 255, 255, 0.2);
            border: 1px solid white;
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            transition: 0.3s;
            text-decoration: none;
            margin: 5px;
        }
        .custom-button:hover {
            background-color: white;
            color: #7eb6f0;
        }

        .order-row {
            background: white;
            color: #333;
            border-radius: 10px;
            padding: 8px 15px;
            width: 100%;
            margin-top: 5px;
            display: flex;
            justify-content: space-between;
            font-size: 12px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header Section
    st.markdown(f"""
        <div class="header-container">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 40px; margin-right: 15px;">⚕️</div>
                <div style="text-align: left;">
                    <h2 style="margin: 0; color: #2c3e50;">Mithila Medical</h2>
                    <p style="margin: 0; color: #7f8c8d; font-size: 14px;">Your Health, Our Priority</p>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 20px;">
                <div style="color: #2c3e50;">Welcome, <b>{st.session_state['user_full_name']}</b> 👤</div>
                <button onclick="window.location.href='/';" style="background: #e74c3c; color: white; border: none; padding: 8px 16px; border-radius: 20px; cursor: pointer; font-weight: 600;">🚪 Logout</button>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Main Content (The Three Cards)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="card card-search">
                <h3>SEARCH MEDICINES</h3>
                <p style="font-size: 14px; margin: 20px 0;">🔍</p>
                <p style="font-size: 12px; opacity: 0.9;">Find medicines by name or condition...</p>
                <div style="margin-top: auto;">
                    <p style="font-size: 12px; margin-top: 10px;">Click to search medicines</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Open Search", key="btn_search_home", use_container_width=True):
            st.switch_page("pages/search_medicines.py")

    with col2:
        st.markdown("""
            <div class="card card-order">
                <h3>PLACE AN ORDER</h3>
                <div style="font-size: 80px; margin: 40px 0;">🛒</div>
                <div style="margin-top: auto;">
                    <p style="font-size: 12px; margin-top: 10px;">Start placing your order</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Place Order", key="btn_order_home", use_container_width=True):
            st.switch_page("pages/search_medicines.py")

    with col3:
        st.markdown("""
            <div class="card card-track">
                <h3>TRACK ORDER STATUS</h3>
                <div style="font-size: 80px; margin: 40px 0;">📍</div>
                <p style="font-size: 12px; margin-bottom: 5px;">Track your orders in real-time</p>
                <div style="margin-top: auto;">
                    <p style="font-size: 12px;">View order history and status</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Track Orders", key="btn_track_home", use_container_width=True):
            st.switch_page("pages/track_order.py")

    # Logout Button in Sidebar
    if st.sidebar.button("🚪 Logout"):
        st.session_state["authenticated"] = False
        st.session_state["user_email"] = None
        st.session_state["user_id"] = None
        st.session_state["user_full_name"] = None
        st.session_state["user_role"] = "customer"
        st.rerun()

    # Footer
    st.markdown("""
        <br><br>
        <div style="text-align: center; color: #7f8c8d;">
            <span style="margin: 0 15px;">Support</span>
            <span style="margin: 0 15px;">FAQ</span>
            <span style="margin: 0 15px;">Contact Us</span>
        </div>
    """, unsafe_allow_html=True)

else:
    # ================ LOGIN/SIGNUP PAGE ================
    
    # ================ BRANDING SECTION ================
    st.markdown("""
    <div class="brand-section">
        <div style="font-size: 3.5em; color: #1a4d8c;">Ⓜ️</div>
        <p class="brand-name">Mithila Medical</p>
        <p style="color: #666;">Your Health, Our Priority</p>
    </div>
    """, unsafe_allow_html=True)

    # ================ MAIN LAYOUT ================
    col1, spacer, col2 = st.columns([10, 1, 10])

    # ================ SIGN UP COLUMN ================
    with col1:
        st.markdown("### SIGN UP")
        with st.form("signup_form", border=False):
            new_name = st.text_input("Full Name", placeholder="Full Name")
            new_email = st.text_input("Email", placeholder="Email")
            new_pass = st.text_input("Password", type="password", placeholder="Password")
            conf_pass = st.text_input("Confirm Password", type="password", placeholder="Confirm Password")
            
            account_type = st.selectbox(
                "Account Type",
                ["👤 Customer", "👨‍💼 Store Staff"],
                label_visibility="collapsed"
            )
            
            store_name = ""
            if "Store Staff" in account_type:
                store_name = st.text_input("Store Name", placeholder="Store Name")
            
            signup_button = st.form_submit_button("CREATE ACCOUNT", use_container_width=True)
            
            if signup_button:
                if not all([new_name, new_email, new_pass, conf_pass]):
                    st.error("Please fill in all fields.")
                elif new_pass != conf_pass:
                    st.error("Passwords do not match.")
                elif len(new_pass) < 6:
                    st.error("Password must be at least 6 characters.")
                elif "Store Staff" in account_type and not store_name:
                    st.error("Please enter store name for staff account.")
                else:
                    if "Store Staff" in account_type:
                        success, message = signup_admin(new_email, new_pass, new_name, store_name)
                    else:
                        success, message = signup_user(new_email, new_pass, new_name)
                    
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        
        st.write("Already have an account? Sign In")

    # ================ SIGN IN COLUMN ================
    with col2:
        st.markdown("### SIGN IN")
        with st.form("signin_form", border=False):
            login_email = st.text_input("Email", placeholder="Email")
            login_pass = st.text_input("Password", type="password", placeholder="Password")
            
            st.markdown("<br>", unsafe_allow_html=True)
            signin_button = st.form_submit_button("LOG IN", use_container_width=True)
            
            if signin_button:
                if login_email and login_pass:
                    success, message, user_id, full_name, role = verify_login_with_role(login_email, login_pass)
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["user_email"] = login_email
                        st.session_state["user_id"] = user_id
                        st.session_state["user_full_name"] = full_name
                        st.session_state["user_role"] = role
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Please fill in all fields.")
        
        st.write("Forgot Password?")
        st.write("Don't have an account? Sign Up")

    # ================ FOOTER BANNER ================
    st.markdown("""
    <div style="display: flex; justify-content: center;">
        <div class="footer-banner-box">
            Search, Book & Track Your Medical Orders
        </div>
    </div>
    """, unsafe_allow_html=True)