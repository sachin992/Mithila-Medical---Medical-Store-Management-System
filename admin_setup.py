import sqlite3
import hashlib

# ================ ADMIN DATABASE SETUP ================
def init_admin_db():
    """Initialize admin database with roles"""
    conn = sqlite3.connect("auth.db")
    cursor = conn.cursor()
    
    # Add role column to existing users table if it doesn't exist
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'customer'")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def signup_admin(email: str, password: str, full_name: str, store_name: str) -> tuple[bool, str]:
    """Register a store admin/staff member"""
    try:
        conn = sqlite3.connect("auth.db")
        cursor = conn.cursor()
        
        hashed_pw = hash_password(password)
        cursor.execute(
            """INSERT INTO users (email, password, full_name, role, created_at) 
               VALUES (?, ?, ?, 'staff', datetime('now'))""",
            (email, hashed_pw, full_name)
        )
        conn.commit()
        conn.close()
        return True, "Staff account created successfully! Please login."
    except sqlite3.IntegrityError:
        return False, "Email already registered."
    except Exception as e:
        return False, f"Error: {str(e)}"

def verify_login_with_role(email: str, password: str) -> tuple[bool, str, str, str, str]:
    """Returns (success, message, user_id, full_name, role)"""
    try:
        conn = sqlite3.connect("auth.db")
        cursor = conn.cursor()
        
        hashed_pw = hash_password(password)
        cursor.execute(
            """SELECT user_id, full_name, role FROM users 
               WHERE email = ? AND password = ?""",
            (email, hashed_pw)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            role = result[2] if result[2] else "customer"
            return True, f"Welcome {result[1]}!", str(result[0]), result[1], role
        else:
            return False, "Invalid email or password.", "", "", ""
    except Exception as e:
        return False, f"Error: {str(e)}", "", "", ""

# Initialize on import
init_admin_db()