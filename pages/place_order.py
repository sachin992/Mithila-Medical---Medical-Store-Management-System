


import streamlit as st
from datetime import datetime
from b import execute_custom_query

# ================ PAGE CONFIG ================
st.set_page_config(
    page_title="Place Order - Mithila Medical",
    page_icon="💊",
    layout="wide"
)

# ================ CSS ================
st.markdown("""
<style>
    .page-header {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        padding: 40px;
        border-radius: 12px;
        margin-bottom: 30px;
        text-align: center;
    }
    
    .page-header h1 {
        margin: 0;
        font-size: 2.2em;
        font-weight: 700;
    }
    
    .navbar-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px;
        background: white;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    .navbar-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.5em;
        font-weight: 700;
        color: #0066cc;
    }
    
    .order-summary {
        background: white;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 30px;
        border-left: 5px solid #3498db;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    .order-summary h2 {
        color: #0066cc;
        margin: 0 0 15px 0;
        font-size: 1.4em;
    }
    
    .summary-row {
        display: flex;
        justify-content: space-between;
        padding: 10px 0;
        border-bottom: 1px solid #f0f0f0;
        color: #666;
    }
    
    .summary-row strong {
        color: #333;
    }
    
    .summary-total {
        display: flex;
        justify-content: space-between;
        padding: 15px 0;
        font-size: 1.2em;
        font-weight: 700;
        color: #06a77d;
        border-top: 2px solid #e0e0e0;
    }
    
    .form-section {
        background: white;
        border-radius: 12px;
        padding: 30px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    .form-section h2 {
        color: #0066cc;
        margin: 0 0 25px 0;
        font-size: 1.3em;
    }
    
    .form-group {
        margin-bottom: 20px;
    }
    
    .form-group label {
        display: block;
        margin-bottom: 8px;
        color: #333;
        font-weight: 600;
        font-size: 0.95em;
    }
    
    .form-group input, .form-group select, .form-group textarea {
        width: 100%;
        padding: 12px 15px;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        font-size: 0.95em;
        transition: all 0.3s ease;
        font-family: inherit;
    }
    
    .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
        outline: none;
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }
    
    .form-group textarea {
        resize: vertical;
        min-height: 100px;
    }
    
    .form-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
    }
    
    .btn-group {
        display: flex;
        gap: 15px;
        margin-top: 30px;
    }
    
    .btn {
        padding: 14px 30px;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 1em;
        flex: 1;
    }
    
    .btn-submit {
        background: linear-gradient(135deg, #06a77d 0%, #059b68 100%);
        color: white;
    }
    
    .btn-submit:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(6, 167, 125, 0.3);
    }
    
    .btn-cancel {
        background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
        color: white;
    }
    
    .btn-cancel:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(149, 165, 166, 0.3);
    }
    
    .divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #3498db, transparent);
        margin: 30px 0;
    }
    
    .validation-error {
        color: #e74c3c;
        font-size: 0.85em;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ================ AUTH CHECK ================
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Please login first!")
    if st.button("Go to Login"):
        st.switch_page("f.py")
    st.stop()

# ================ NAVBAR ================
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    <div class="navbar-top" style="justify-content: flex-start;">
        <div class="navbar-brand">
            <span>💊</span>
            <span>Mithila Medical</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="navbar-top" style="justify-content: flex-end;">
        <div>
            <p style="margin: 0; color: #0066cc; font-weight: 700;">{st.session_state['user_full_name']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================ PAGE HEADER ================
st.markdown("""
<div class="page-header">
    <h1>📦 Place Your Order</h1>
</div>
""", unsafe_allow_html=True)

# ================ CHECK ORDER DATA ================
if "order_data" not in st.session_state or not st.session_state["order_data"]:
    st.warning("⚠️ No medicine selected. Please search and select a medicine first.")
    if st.button("Back to Search"):
        st.switch_page("pages/search_medicines.py")
    st.stop()

order_data = st.session_state["order_data"]

# ================ ORDER SUMMARY ================
st.markdown(f"""
<div class="order-summary">
    <h2>📋 Order Summary</h2>
    <div class="summary-row">
        <strong>Medicine:</strong>
        <span>{order_data['medicine_name']}</span>
    </div>
    <div class="summary-row">
        <strong>Price per Unit:</strong>
        <span>₹{order_data['price']}</span>
    </div>
    <div class="summary-row">
        <strong>Max Available:</strong>
        <span>{order_data['max_quantity']} units</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ================ ORDER FORM ================
st.markdown('<div class="form-section">', unsafe_allow_html=True)
st.markdown('<h2>📦 Order Details</h2>', unsafe_allow_html=True)

with st.form("order_form", clear_on_submit=False):
    st.markdown('<div class="form-group">', unsafe_allow_html=True)
    st.write('<label>📊 Quantity (units)</label>', unsafe_allow_html=True)
    quantity = st.number_input(
        "Quantity",
        min_value=1,
        max_value=order_data['max_quantity'],
        value=1,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Calculate total
    total_price = order_data['price'] * quantity
    
    st.markdown(f"""
    <div class="summary-row" style="border: none; padding: 15px 0; font-size: 1.1em; font-weight: 700; color: #06a77d;">
        <strong>Total Price:</strong>
        <span>₹{total_price}</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="color: #0066cc; margin-top: 0;">👤 Delivery Details</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.write('<label>👤 Full Name</label>', unsafe_allow_html=True)
        full_name = st.text_input(
            "Full Name",
            value=st.session_state.get('user_full_name', ''),
            label_visibility="collapsed",
            placeholder="Enter your full name"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.write('<label>📱 Phone Number</label>', unsafe_allow_html=True)
        phone = st.text_input(
            "Phone",
            label_visibility="collapsed",
            placeholder="10 digit number"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="form-group">', unsafe_allow_html=True)
    st.write('<label>📍 Address</label>', unsafe_allow_html=True)
    address = st.text_area(
        "Address",
        label_visibility="collapsed",
        placeholder="Enter complete address"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.write('<label>🏙️ City</label>', unsafe_allow_html=True)
        city = st.text_input(
            "City",
            label_visibility="collapsed",
            placeholder="Enter city name"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.write('<label>📮 PIN Code</label>', unsafe_allow_html=True)
        pincode = st.text_input(
            "PIN",
            label_visibility="collapsed",
            placeholder="6 digit PIN code"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ================ SUBMIT BUTTON ================
    col1, col2 = st.columns(2)
    
    with col1:
        if st.form_submit_button("✅ Place Order", use_container_width=True):
            # Validation
            errors = []
            
            if not full_name or not full_name.strip():
                errors.append("Full name is required")
            
            if not phone or len(phone) != 10 or not phone.isdigit():
                errors.append("Phone must be 10 digits")
            
            if not address or not address.strip():
                errors.append("Address is required")
            
            if not city or not city.strip():
                errors.append("City is required")
            
            if not pincode or len(pincode) != 6 or not pincode.isdigit():
                errors.append("PIN code must be 6 digits")
            
            if errors:
                for error in errors:
                    st.error(f"❌ {error}")
            else:
                try:
                    # Insert order
                    insert_query = f"""
                    INSERT INTO orders (user_id, medicine_id, quantity, customer_name, phone, address, city, pincode, status, created_at)
                    VALUES ({st.session_state['user_id']}, {order_data['medicine_id']}, {quantity}, 
                    '{full_name}', '{phone}', '{address}', '{city}', '{pincode}', 'Pending', '{datetime.now()}')
                    """
                    execute_custom_query(insert_query)
                    
                    # Reduce medicine quantity
                    update_query = f"""
                    UPDATE medicines 
                    SET quantity = quantity - {quantity} 
                    WHERE medicine_id = {order_data['medicine_id']} AND quantity >= {quantity}
                    """
                    execute_custom_query(update_query)
                    
                    st.success("✅ Order placed successfully!")
                    st.balloons()
                    
                    # Clear order data
                    st.session_state["order_data"] = {}
                    
                    st.info(f"Your order has been placed. You will receive a confirmation SMS on {phone}")
                    
                    if st.button("Go to Home"):
                        st.switch_page("f.py")
                
                except Exception as e:
                    st.error(f"❌ Error placing order: {str(e)}")
    
    with col2:
        if st.form_submit_button("← Cancel", use_container_width=True):
            st.session_state["order_data"] = {}
            st.switch_page("pages/search_medicines.py")

st.markdown('</div>', unsafe_allow_html=True)