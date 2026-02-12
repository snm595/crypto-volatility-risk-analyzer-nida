import streamlit as st
import hashlib
import json
import os
from datetime import datetime

# Simple authentication system
USERS_FILE = "users.json"

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    """Load users from file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {
        "admin": {
            "password": hash_password("admin123"),
            "email": "admin@example.com",
            "created_at": "2024-01-01T00:00:00",
            "role": "admin"
        },
        "user": {
            "password": hash_password("user123"),
            "email": "user@example.com",
            "created_at": "2024-01-01T00:00:00",
            "role": "user"
        }
    }  # Default users

def save_users(users):
    """Save users to file"""
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def authenticate(username, password):
    """Authenticate user"""
    users = load_users()
    hashed_password = hash_password(password)
    return username in users and users[username]["password"] == hashed_password

def get_user_info(username):
    """Get user information"""
    users = load_users()
    if username in users:
        return users[username]
    return None

def login_page():
    """Display login/registration page"""
    st.markdown("""
    <style>
    .auth-container {
        max-width: 450px;
        margin: 50px auto;
        padding: 30px;
        border-radius: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
        color: white;
        text-align: center;
    }
    .tab-container {
        display: flex;
        justify-content: center;
        margin-bottom: 30px;
        gap: 10px;
    }
    .tab-button {
        background: rgba(255,255,255,0.2);
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        color: white;
        cursor: pointer;
        transition: all 0.3s;
        font-weight: bold;
        flex: 1;
    }
    .tab-button.active {
        background: rgba(255,255,255,0.3);
        transform: translateY(-2px);
    }
    .form-content {
        margin-top: 20px;
    }
    .input-group {
        margin-bottom: 20px;
        text-align: left;
    }
    .input-group label {
        display: block;
        margin-bottom: 8px;
        font-weight: bold;
    }
    .input-group input {
        width: 100%;
        padding: 12px;
        border: none;
        border-radius: 8px;
        background-color: rgba(255,255,255,0.9);
        color: black;
        box-sizing: border-box;
    }
    .submit-btn {
        width: 100%;
        padding: 12px 24px;
        border: none;
        border-radius: 8px;
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s;
        margin-top: 20px;
    }
    .submit-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    .form-title {
        margin-bottom: 30px;
    }
    .form-footer {
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid rgba(255,255,255,0.3);
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize tab state
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = 'login'
    
    # Tab selection using Streamlit buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Login", key="login_tab", use_container_width=True):
            st.session_state.current_tab = 'login'
            st.rerun()
    with col2:
        if st.button("📝 Register", key="register_tab", use_container_width=True):
            st.session_state.current_tab = 'register'
            st.rerun()
    
    # Purple container with content
    if st.session_state.current_tab == 'login':
        st.markdown("""
        <div class="auth-container">
            <h2 class="form-title">🔐 Welcome Back</h2>
            <div class="form-content">
        </div>
        """, unsafe_allow_html=True)
        
        # Handle login with Streamlit inputs (now visible)
        username = st.text_input("👤 Username", placeholder="Enter your username", key="login_username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_password")
        
        if st.button("🚀 Login", key="login_submit", use_container_width=True):
            if authenticate(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
        
        st.markdown("""
            <div class="form-footer">
                <p>Don't have an account? Click 'Register' above!</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    else:  # Register form
        st.markdown("""
        <div class="auth-container">
            <h2 class="form-title">📝 Create Account</h2>
            <div class="form-content">
        </div>
        """, unsafe_allow_html=True)
        
        # Handle registration with Streamlit inputs (now visible)
        username = st.text_input("👤 Choose Username", placeholder="Pick a unique username", key="reg_username")
        email = st.text_input("📧 Email", placeholder="your@email.com", key="reg_email")
        password = st.text_input("🔒 Password", type="password", placeholder="Create a strong password", key="reg_password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Re-enter your password", key="reg_confirm")
        
        if st.button("🎉 Create Account", key="register_submit", use_container_width=True):
            # Validation
            if not username or not password:
                st.error("❌ Username and password are required!")
            elif len(username) < 3:
                st.error("❌ Username must be at least 3 characters long!")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters long!")
            elif password != confirm_password:
                st.error("❌ Passwords do not match!")
            elif not email or "@" not in email or "." not in email:
                st.error("❌ Please enter a valid email address!")
            else:
                # Check if username already exists
                users = load_users()
                if username in users:
                    st.error("❌ Username already exists! Please choose another.")
                else:
                    # Create new user
                    users[username] = {
                        "password": hash_password(password),
                        "email": email,
                        "created_at": datetime.now().isoformat(),
                        "role": "user"
                    }
                    save_users(users)
                    
                    st.success("✅ Account created successfully! You can now login.")
                    st.session_state.current_tab = 'login'
                    st.rerun()
        
        st.markdown("""
            <div class="form-footer">
                <p>Already have an account? Click 'Login' above!</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

def logout():
    """Logout user"""
    st.session_state.logged_in = False
    st.session_state.username = None
    st.rerun()
