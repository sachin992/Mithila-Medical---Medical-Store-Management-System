import streamlit as st
from b import execute_custom_query, llm_with_tools
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage

# ================ PAGE CONFIG ================
st.set_page_config(
    page_title="Manage Medicines - Mithila Medical",
    page_icon="💊",
    layout="wide"
)

# ================ CSS ================
st.markdown("""
<style>
    .admin-header {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 40px;
        border-radius: 12px;
        margin-bottom: 30px;
        text-align: center;
    }
    
    .admin-header h1 {
        margin: 0;
        font-size: 2.2em;
        font-weight: 700;
    }
    
    .navbar-admin {
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
        color: #e74c3c;
    }
    
    .admin-badge {
        background: #e74c3c;
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
    }
    
    .section-box {
        background: white;
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    .section-box h2 {
        color: #e74c3c;
        margin: 0 0 25px 0;
        font-size: 1.4em;
        display: flex;
        align-items: center;
        gap: 10px;
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
    
    .form-group input, .form-group textarea, .form-group select {
        width: 100%;
        padding: 12px 15px;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        font-size: 0.95em;
        transition: all 0.3s ease;
        font-family: inherit;
    }
    
    .form-group input:focus, .form-group textarea:focus, .form-group select:focus {
        outline: none;
        border-color: #e74c3c;
        box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
    }
    
    .form-row {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
    }
    
    .medicine-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 20px;
    }
    
    .medicine-table th {
        background: #f5f5f5;
        color: #333;
        padding: 12px;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid #e0e0e0;
    }
    
    .medicine-table td {
        padding: 12px;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .medicine-table tr:hover {
        background: #f9f9f9;
    }
    
    .btn-admin {
        padding: 12px 25px;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.95em;
    }
    
    .btn-add {
        background: linear-gradient(135deg, #27ae60 0%, #229954 100%);
        color: white;
    }
    
    .btn-add:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(39, 174, 96, 0.3);
    }
    
    .btn-edit {
        background: #3498db;
        color: white;
        padding: 8px 15px;
        font-size: 0.85em;
    }
    
    .btn-delete {
        background: #e74c3c;
        color: white;
        padding: 8px 15px;
        font-size: 0.85em;
    }
    
    .ai-section {
        background: linear-gradient(135deg, #f9e79f 0%, #f5b041 100%);
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 30px;
    }
    
    .ai-section h3 {
        color: #7d6608;
        margin: 0 0 15px 0;
    }
    
    .ai-input {
        width: 100%;
        padding: 12px 15px;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        font-size: 0.95em;
        margin-bottom: 15px;
    }
    
    .ai-response {
        background: white;
        border-radius: 8px;
        padding: 15px;
        margin-top: 15px;
        color: #333;
        border-left: 4px solid #f5b041;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-bottom: 30px;
    }
    
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border-top: 5px solid #e74c3c;
    }
    
    .stat-number {
        font-size: 2.5em;
        font-weight: 700;
        color: #e74c3c;
        margin: 10px 0;
    }
    
    .stat-label {
        color: #999;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# ================ AUTH CHECK ================
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.error("Please login first!")
    st.stop()

if st.session_state.get("user_role") != "staff":
    st.error("❌ Access Denied! Only store staff can access this page.")
    if st.button("Go to Home"):
        st.switch_page("f.py")
    st.stop()

# ================ NAVBAR ================
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("""
    <div class="navbar-admin">
        <div class="navbar-brand">
            <span>⚙️</span>
            <span>Admin Panel</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="navbar-admin" style="justify-content: flex-end;">
        <div>
            <span class="admin-badge">👨‍💼 {st.session_state['user_full_name']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 Logout"):
        st.session_state["authenticated"] = False
        st.rerun()

# ================ PAGE HEADER ================
st.markdown("""
<div class="admin-header">
    <h1>💊 Manage Medicines</h1>
</div>
""", unsafe_allow_html=True)

# ================ TABS ================
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🤖 AI Assistant", "➕ Add/Manage"])

# ================ TAB 1: DASHBOARD ================
with tab1:
    try:
        total_medicines = execute_custom_query("SELECT COUNT(*) FROM medicines")
        total_quantity = execute_custom_query("SELECT SUM(quantity) FROM medicines")
        low_stock = execute_custom_query("SELECT COUNT(*) FROM medicines WHERE quantity < 10")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Total Medicines</div>
                <div class="stat-number">{total_medicines[0][0] if total_medicines else 0}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Total Stock</div>
                <div class="stat-number">{total_quantity[0][0] if total_quantity and total_quantity[0][0] else 0}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Low Stock Items</div>
                <div class="stat-number">{low_stock[0][0] if low_stock else 0}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # All medicines table
        st.markdown('<div class="section-box">', unsafe_allow_html=True)
        st.markdown('<h2>📋 All Medicines</h2>', unsafe_allow_html=True)
        
        medicines = execute_custom_query("SELECT medicine_id, medicine_name, quantity, price, description FROM medicines ORDER BY medicine_id DESC")
        
        if medicines:
            st.markdown(f"""
            <table class="medicine-table">
                <tr>
                    <th>ID</th>
                    <th>Medicine Name</th>
                    <th>Quantity</th>
                    <th>Price</th>
                    <th>Status</th>
                </tr>
            """, unsafe_allow_html=True)
            
            for med in medicines:
                stock_status = "✅ In Stock" if med[2] > 10 else "⚠️ Low Stock" if med[2] > 0 else "❌ Out of Stock"
                st.markdown(f"""
                <tr>
                    <td>#{med[0]}</td>
                    <td><strong>{med[1]}</strong></td>
                    <td>{med[2]} units</td>
                    <td>₹{med[3]}</td>
                    <td>{stock_status}</td>
                </tr>
                """, unsafe_allow_html=True)
            
            st.markdown('</table>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Error loading dashboard: {str(e)}")

# ================ TAB 2: AI ASSISTANT ================
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
import uuid
import threading
import time

# Import the chatbot and utilities from b.py
from b import chatbot, ChatState

with tab2:
    st.markdown("""
    <div class="support-section">
        <h3>🤖 Staff Support Agent</h3>
        <p>Ask me anything about medicines inventory, orders, and sales data.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for chat
    if "support_thread_id" not in st.session_state:
        st.session_state.support_thread_id = str(uuid.uuid4())
    
    if "support_chat_history" not in st.session_state:
        st.session_state.support_chat_history = []
    
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False
    
    # Quick query suggestions at the top
    st.markdown("### 💡 Quick Queries")
    
    quick_cols = st.columns(3)
    
    with quick_cols[0]:
        if st.button("📦 Low Stock Medicines", use_container_width=True, key="quick_low_stock"):
            st.session_state.support_chat_history.append({"role": "user", "content": "Show low stock medicines"})
            st.session_state.is_processing = True
            st.rerun()
    
    with quick_cols[1]:
        if st.button("⏰ Pending Orders", use_container_width=True, key="quick_pending"):
            st.session_state.support_chat_history.append({"role": "user", "content": "Show pending orders"})
            st.session_state.is_processing = True
            st.rerun()
    
    with quick_cols[2]:
        if st.button("💰 Top Selling Medicines", use_container_width=True, key="quick_top_selling"):
            st.session_state.support_chat_history.append({"role": "user", "content": "Show top selling medicines"})
            st.session_state.is_processing = True
            st.rerun()
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if st.button("📋 Orders This Month", use_container_width=True, key="quick_monthly"):
            st.session_state.support_chat_history.append({"role": "user", "content": "Show delivered orders this month"})
            st.session_state.is_processing = True
            st.rerun()
    
    with col5:
        if st.button("⚠️ Expiring Soon", use_container_width=True, key="quick_expiring"):
            st.session_state.support_chat_history.append({"role": "user", "content": "Show medicines expiring soon"})
            st.session_state.is_processing = True
            st.rerun()
    
    with col6:
        if st.button("🔄 Clear Chat", use_container_width=True, key="quick_clear"):
            st.session_state.support_chat_history = []
            st.session_state.support_thread_id = str(uuid.uuid4())
            st.session_state.is_processing = False
            st.rerun()
    
    st.markdown("---")
    
    # Chat display area
    st.markdown("### 💬 Chat")
    
    # Display chat messages using st.chat_message
    for message in st.session_state.support_chat_history:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(message["content"])
    
    # Input section at bottom
    st.markdown("---")
    
    col_input, col_button = st.columns([5, 1])
    
    with col_input:
        user_input = st.text_input(
            "Your query:",
            placeholder="Example: Show pending orders | What's the stock of Aspirin?",
            key="staff_query_input",
            disabled=st.session_state.is_processing
        )
    
    with col_button:
        send_button = st.button("➤", use_container_width=True, key="send_query", 
                               help="Send query", 
                               type="primary",
                               disabled=st.session_state.is_processing)
    
    # Process user input
    if send_button and user_input:
        # Add user message to history immediately
        st.session_state.support_chat_history.append({
            "role": "user",
            "content": user_input
        })
        st.session_state.is_processing = True
        st.rerun()
    
    # Process bot response if last message is from user and we're processing
    if (st.session_state.is_processing and 
        st.session_state.support_chat_history and 
        st.session_state.support_chat_history[-1]["role"] == "user"):
        
        last_user_message = st.session_state.support_chat_history[-1]["content"]
        
        # Show loading indicator
        with st.spinner("🔍 Searching for information..."):
            try:
                # Build messages list from history
                messages_list = []
                for msg in st.session_state.support_chat_history:
                    if msg["role"] == "user":
                        messages_list.append(HumanMessage(content=msg["content"]))
                    else:
                        messages_list.append(AIMessage(content=msg["content"]))
                
                # Prepare chat state
                chat_state = ChatState(
                    messages=messages_list,
                    action_type=None,
                    action_payload=None,
                    user_id="staff_user"
                )
                
                # Invoke chatbot
                config = {"configurable": {"thread_id": st.session_state.support_thread_id}}
                result = chatbot.invoke(chat_state, config=config)
                
                # Extract bot response
                bot_response = None
                if result and "messages" in result:
                    # Get the last AI response
                    for message in reversed(result["messages"]):
                        if isinstance(message, AIMessage) and hasattr(message, 'content'):
                            content = str(message.content).strip()
                            if content and content != "" and "Error" not in content:
                                bot_response = content
                                break
                
                if not bot_response:
                    bot_response = "I couldn't retrieve the information. Please try a different query."
                
                # Add bot response to history
                st.session_state.support_chat_history.append({
                    "role": "assistant",
                    "content": bot_response
                })
                
                st.session_state.is_processing = False
                st.rerun()
                
            except Exception as e:
                error_msg = f"⚠️ Error: {str(e)}"
                st.session_state.support_chat_history.append({
                    "role": "assistant",
                    "content": error_msg
                })
                st.session_state.is_processing = False
                st.rerun()
    
    # Information section
    st.markdown("---")
    st.markdown("""
    **What I can help with:**
    - 📊 Check medicine inventory and stock levels
    - 📦 View and manage orders
    - 💰 Revenue and sales analytics
    - 🗓️ Track delivery status
    - ⚠️ Identify expiring medicines
    
    **Example queries:**
    - "What's the stock of Paracetamol?"
    - "Show order #123 details"
    - "How many orders are processing?"
    """)
# ================ TAB 3: ADD/MANAGE ================
with tab3:
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.markdown('<h2>➕ Add New Medicine</h2>', unsafe_allow_html=True)
    
    # Use AI extracted data if available
    default_name = ""
    default_qty = 1
    default_price = 0
    default_desc = ""
    
    if "ai_medicine_details" in st.session_state:
        details = st.session_state["ai_medicine_details"]
        default_name = details.get("medicine_name", "")
        default_qty = details.get("quantity", 1)
        default_price = details.get("price", 0)
        default_desc = details.get("description", "")
    
    with st.form("add_medicine_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="form-group">', unsafe_allow_html=True)
            st.write('<label>💊 Medicine Name</label>', unsafe_allow_html=True)
            medicine_name = st.text_input(
                "Name",
                value=default_name,
                placeholder="e.g., Paracetamol",
                label_visibility="collapsed"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="form-group">', unsafe_allow_html=True)
            st.write('<label>📦 Quantity (units)</label>', unsafe_allow_html=True)
            quantity = st.number_input(
                "Qty",
                value=int(default_qty),   # Convert to int
                min_value=1,              # Int
                step=1,                   # Int ← All integers
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="form-group">', unsafe_allow_html=True)
            st.write('<label>💰 Price (₹)</label>', unsafe_allow_html=True)
            price = st.number_input(
                "Price",
                value=float(default_price),  # Convert to float
                min_value=0.0,               # Float
                step=1.0,                    # Float ← All floats
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-group">', unsafe_allow_html=True)
        st.write('<label>📝 Description</label>', unsafe_allow_html=True)
        description = st.text_area(
            "Desc",
            value=default_desc,
            placeholder="Medicine description, usage, side effects, etc.",
            height=80,
            label_visibility="collapsed"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("✅ Add Medicine", use_container_width=True):
                if medicine_name and quantity and price:
                    try:
                        insert_query = f"""
                        INSERT INTO medicines (medicine_name, quantity, price, description)
                        VALUES ('{medicine_name}', {quantity}, {price}, '{description}')
                        """
                        execute_custom_query(insert_query)
                        
                        st.success("✅ Medicine added successfully!")
                        st.balloons()
                        
                        # Clear AI details
                        if "ai_medicine_details" in st.session_state:
                            del st.session_state["ai_medicine_details"]
                        
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error adding medicine: {str(e)}")
                else:
                    st.error("Please fill in all required fields!")
        
        with col2:
            if st.form_submit_button("🔄 Clear Form", use_container_width=True):
                if "ai_medicine_details" in st.session_state:
                    del st.session_state["ai_medicine_details"]
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)