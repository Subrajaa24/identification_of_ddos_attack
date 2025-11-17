import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os

# Load authentication configuration
def load_auth_config():
    try:
        # Try to load from existing config file
        with open('auth_config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)
    except FileNotFoundError:
        # Default configuration with one test user
        config = {
            'credentials': {
                'usernames': {
                    'testuser': {
                        'email': 'test@example.com',
                        'name': 'Test User',
                        'password': '$2b$12$VRT3j2Hk9qxLVu61tDC9FOq6l2JWjTVlM1s4DLK3lka4XIcB7JHbW'  # Password: 'password'
                    }
                }
            },
            'cookie': {
                'expiry_days': 30,
                'key': 'wsn_blockchain_auth',
                'name': 'wsn_blockchain_cookie'
            }
        }
        # Save the default config
        with open('auth_config.yaml', 'w') as file:
            yaml.dump(config, file)
    
    return config

# Create the authenticator object
def get_authenticator():
    config = load_auth_config()
    return stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

# Initialize session state for user management
def init_auth_state():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'user_info' not in st.session_state:
        st.session_state['user_info'] = {}

# Authentication system
def auth_user():
    init_auth_state()
    authenticator = get_authenticator()
    
    if not st.session_state['authenticated']:
        try:
            # Display login, register, forgot password widgets
            auth_status = None
            
            tab1, tab2, tab3 = st.tabs(["Login", "Register", "Forgot Password"])
            
            with tab1:
                name, auth_status, username = authenticator.login("Login", "main")
                if auth_status:
                    st.session_state['authenticated'] = True
                    st.session_state['username'] = username
                    config = load_auth_config()
                    st.session_state['user_info'] = config['credentials']['usernames'][username]
                    st.rerun()
                elif auth_status == False:
                    st.error('Username/password is incorrect')
            
            with tab2:
                try:
                    if authenticator.register_user("Register", location="main"):
                        st.success("User registered successfully")
                except Exception as e:
                    st.error(e)
            
            with tab3:
                try:
                    username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password("Forgot password", location="main")
                    if username_forgot_pw:
                        st.success('New password sent securely')
                        st.info('Please check your email')
                    elif username_forgot_pw == False:
                        st.error('Username not found')
                except Exception as e:
                    st.error(e)
            
            return False
        
        except Exception as e:
            st.error(f"Authentication error: {e}")
            return False
    
    return True

# Logout function
def logout():
    authenticator = get_authenticator()
    authenticator.logout("Logout", "sidebar")
    
    if not st.session_state['authenticated']:
        st.session_state['username'] = None
        st.session_state['user_info'] = {}