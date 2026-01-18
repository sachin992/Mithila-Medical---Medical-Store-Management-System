# import streamlit as st
# from b import execute_custom_query

# # ================ PAGE CONFIG ================
# st.set_page_config(
#     page_title="Track Order - Mithila Medical",
#     page_icon="💊",
#     layout="wide"
# )

# # ================ CSS ================
# st.markdown("""
# <style>
#     .page-header {
#         background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
#         color: white;
#         padding: 40px;
#         border-radius: 12px;
#         margin-bottom: 30px;
#         text-align: center;
#     }
    
#     .page-header h1 {
#         margin: 0;
#         font-size: 2.2em;
#         font-weight: 700;
#     }
    
#     .navbar-top {
#         display: flex;
#         justify-content: space-between;
#         align-items: center;
#         padding: 20px;
#         background: white;
#         border-radius: 12px;
#         margin-bottom: 30px;
#         box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
#     }
    
#     .navbar-brand {
#         display: flex;
#         align-items: center;
#         gap: 12px;
#         font-size: 1.5em;
#         font-weight: 700;
#         color: #0066cc;
#     }
    
#     .order-card {
#         background: white;
#         border-radius: 12px;
#         padding: 25px;
#         margin-bottom: 20px;
#         border-left: 5px solid #3498db;
#         box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
#         transition: all 0.3s ease;
#     }
    
#     .order-card:hover {
#         transform: translateX(5px);
#         box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
#     }
    
#     .order-header {
#         display: flex;
#         justify-content: space-between;
#         align-items: center;
#         margin-bottom: 15px;
#         padding-bottom: 15px;
#         border-bottom: 2px solid #f0f0f0;
#     }
    
#     .order-id {
#         color: #0066cc;
#         font-weight: 700;
#         font-size: 1.2em;
#     }
    
#     .status-badge {
#         display: inline-block;
#         padding: 8px 16px;
#         border-radius: 20px;
#         font-size: 0.85em;
#         font-weight: 600;
#     }
    
#     .status-pending {
#         background: #fff3cd;
#         color: #856404;
#     }
    
#     .status-processing {
#         background: #d1ecf1;
#         color: #0c5460;
#     }
    
#     .status-delivered {
#         background: #d4edda;
#         color: #155724;
#     }
    
#     .order-details {
#         display: grid;
#         grid-template-columns: repeat(2, 1fr);
#         gap: 15px;
#         margin-bottom: 15px;
#     }
    
#     .detail-row {
#         padding: 10px 0;
#     }
    
#     .detail-label {
#         color: #999;
#         font-size: 0.9em;
#         margin-bottom: 3px;
#     }
    
#     .detail-value {
#         color: #333;
#         font-weight: 600;
#         font-size: 0.95em;
#     }
    
#     .timeline {
#         margin-top: 20px;
#         padding-top: 15px;
#         border-top: 2px solid #f0f0f0;
#     }
    
#     .timeline-item {
#         display: flex;
#         gap: 15px;
#         margin-bottom: 15px;
#     }
    
#     .timeline-dot {
#         width: 12px;
#         height: 12px;
#         background: #3498db;
#         border-radius: 50%;
#         margin-top: 4px;
#         flex-shrink: 0;
#     }
    
#     .timeline-text {
#         color: #666;
#         font-size: 0.9em;
#     }
    
#     .no-orders {
#         background: white;
#         border-radius: 12px;
#         padding: 60px 20px;
#         text-align: center;
#         box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
#     }
    
#     .no-orders h2 {
#         color: #666;
#         margin: 0 0 10px 0;
#     }
    
#     .no-orders p {
#         color: #999;
#         margin: 0 0 20px 0;
#     }
    
#     .btn-back {
#         background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
#         color: white;
#         padding: 12px 25px;
#         border: none;
#         border-radius: 8px;
#         font-weight: 600;
#         cursor: pointer;
#         transition: all 0.3s ease;
#     }
    
#     .btn-back:hover {
#         transform: translateY(-2px);
#         box-shadow: 0 8px 20px rgba(52, 152, 219, 0.3);
#     }
    
#     .filter-section {
#         background: white;
#         border-radius: 12px;
#         padding: 20px;
#         margin-bottom: 30px;
#         box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
#         display: flex;
#         gap: 15px;
#         align-items: center;
#         flex-wrap: wrap;
#     }
    
#     .filter-btn {
#         padding: 10px 20px;
#         border: 2px solid #e0e0e0;
#         background: white;
#         border-radius: 8px;
#         cursor: pointer;
#         font-weight: 600;
#         transition: all 0.3s ease;
#         color: #666;
#     }
    
#     .filter-btn:hover, .filter-btn.active {
#         background: #3498db;
#         color: white;
#         border-color: #3498db;
#     }
# </style>
# """, unsafe_allow_html=True)

# # ================ AUTH CHECK ================
# if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
#     st.error("Please login first!")
#     if st.button("Go to Login"):
#         st.switch_page("f.py")
#     st.stop()

# # ================ NAVBAR ================
# col1, col2 = st.columns([1, 1])

# with col1:
#     st.markdown("""
#     <div class="navbar-top" style="justify-content: flex-start;">
#         <div class="navbar-brand">
#             <span>💊</span>
#             <span>Mithila Medical</span>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

# with col2:
#     st.markdown(f"""
#     <div class="navbar-top" style="justify-content: flex-end;">
#         <div>
#             <p style="margin: 0; color: #0066cc; font-weight: 700;">{st.session_state['user_full_name']}</p>
#         </div>
#     </div>
#     """, unsafe_allow_html=True)

# # ================ PAGE HEADER ================
# st.markdown("""
# <div class="page-header">
#     <h1>📍 Track Your Orders</h1>
# </div>
# """, unsafe_allow_html=True)

# # ================ BACK BUTTON ================
# col1, col2, col3 = st.columns([5, 0.5, 0.5])

# with col3:
#     if st.button("🏠 Back Home", use_container_width=True):
#         st.switch_page("f.py")

# # ================ FILTER SECTION ================
# st.markdown('<div class="filter-section">', unsafe_allow_html=True)
# st.write("**Filter by Status:**")

# col1, col2, col3, col4 = st.columns(4)

# with col1:
#     show_all = st.checkbox("All Orders", value=True)
# with col2:
#     show_pending = st.checkbox("Pending")
# with col3:
#     show_processing = st.checkbox("Processing")
# with col4:
#     show_delivered = st.checkbox("Delivered")

# st.markdown('</div>', unsafe_allow_html=True)

# # ================ FETCH ORDERS ================
# try:
#     # Build status filter
#     status_list = []
#     if show_all or (show_pending and show_processing and show_delivered):
#         query = f"""
#         SELECT order_id, medicine_id, quantity, status, created_at, delivery_date, customer_name, phone, address
#         FROM orders 
#         WHERE user_id = {st.session_state['user_id']}
#         ORDER BY created_at DESC
#         """
#     else:
#         if show_pending:
#             status_list.append("'Pending'")
#         if show_processing:
#             status_list.append("'Processing'")
#         if show_delivered:
#             status_list.append("'Delivered'")
        
#         if status_list:
#             status_filter = ", ".join(status_list)
#             query = f"""
#             SELECT order_id, medicine_id, quantity, status, created_at, delivery_date, customer_name, phone, address
#             FROM orders 
#             WHERE user_id = {st.session_state['user_id']} AND status IN ({status_filter})
#             ORDER BY created_at DESC
#             """
#         else:
#             st.info("Select at least one status to filter orders.")
#             st.stop()
    
#     results = execute_custom_query(query)
    
#     if results:
#         st.success(f"✅ You have {len(results)} order(s)")
        
#         for order in results:
#             order_id, med_id, qty, status, created_at, delivery_date, cust_name, cust_phone, cust_addr = order
            
#             # Determine status styling
#             if status == "Pending":
#                 status_class = "status-pending"
#                 status_icon = "⏳"
#             elif status == "Processing":
#                 status_class = "status-processing"
#                 status_icon = "🚚"
#             else:
#                 status_class = "status-delivered"
#                 status_icon = "✅"
            
#             st.markdown(f"""
#             <div class="order-card">
#                 <div class="order-header">
#                     <div class="order-id">Order #{order_id}</div>
#                     <span class="status-badge {status_class}">{status_icon} {status}</span>
#                 </div>
                
#                 <div class="order-details">
#                     <div class="detail-row">
#                         <div class="detail-label">Medicine ID</div>
#                         <div class="detail-value">#{med_id}</div>
#                     </div>
#                     <div class="detail-row">
#                         <div class="detail-label">Quantity</div>
#                         <div class="detail-value">{qty} units</div>
#                     </div>
#                     <div class="detail-row">
#                         <div class="detail-label">Customer Name</div>
#                         <div class="detail-value">{cust_name}</div>
#                     </div>
#                     <div class="detail-row">
#                         <div class="detail-label">Phone</div>
#                         <div class="detail-value">{cust_phone}</div>
#                     </div>
#                     <div class="detail-row">
#                         <div class="detail-label">Order Date</div>
#                         <div class="detail-value">{created_at}</div>
#                     </div>
#                     <div class="detail-row">
#                         <div class="detail-label">Expected Delivery</div>
#                         <div class="detail-value">{delivery_date if delivery_date else 'Being processed'}</div>
#                     </div>
#                 </div>
                
#                 <div class="timeline">
#                     <div class="timeline-item">
#                         <div class="timeline-dot"></div>
#                         <div class="timeline-text">Order Placed on {created_at}</div>
#                     </div>
#                     {f'<div class="timeline-item"><div class="timeline-dot"></div><div class="timeline-text">Expected delivery on {delivery_date}</div></div>' if delivery_date else ''}
#                 </div>
#             </div>
#             """, unsafe_allow_html=True)
    
#     else:
#         st.markdown("""
#         <div class="no-orders">
#             <h2>📭 No Orders Found</h2>
#             <p>You haven't placed any orders yet. Start by searching for medicines!</p>
#         </div>
#         """, unsafe_allow_html=True)
        
#         if st.button("Search Medicines", use_container_width=True):
#             st.switch_page("pages/search_medicines.py")

# except Exception as e:
#     st.error(f"❌ Error fetching orders: {str(e)}")


import streamlit as st
from b import execute_custom_query

# ================ PAGE CONFIG ================
st.set_page_config(
    page_title="Track Order - Mithila Medical",
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
    
    .order-card {
        background: white;
        border-radius: 12px;
        padding: 25px;
        margin-bottom: 20px;
        border-left: 5px solid #3498db;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
    }
    
    .order-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }
    
    .order-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        padding-bottom: 15px;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .order-id {
        color: #0066cc;
        font-weight: 700;
        font-size: 1.2em;
    }
    
    .status-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 0.85em;
        font-weight: 600;
    }
    
    .status-pending {
        background: #fff3cd;
        color: #856404;
    }
    
    .status-processing {
        background: #d1ecf1;
        color: #0c5460;
    }
    
    .status-delivered {
        background: #d4edda;
        color: #155724;
    }
    
    .order-details {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 15px;
        margin-bottom: 15px;
    }
    
    .detail-row {
        padding: 10px 0;
    }
    
    .detail-label {
        color: #999;
        font-size: 0.9em;
        margin-bottom: 3px;
    }
    
    .detail-value {
        color: #333;
        font-weight: 600;
        font-size: 0.95em;
    }
    
    .no-orders {
        background: white;
        border-radius: 12px;
        padding: 60px 20px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    .no-orders h2 {
        color: #666;
        margin: 0 0 10px 0;
    }
    
    .no-orders p {
        color: #999;
        margin: 0 0 20px 0;
    }
    
    .filter-section {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
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
    <h1>📍 Track Your Orders</h1>
</div>
""", unsafe_allow_html=True)

# ================ BACK BUTTON ================
col1, col2, col3 = st.columns([5, 0.5, 0.5])

with col3:
    if st.button("🏠 Back Home", use_container_width=True):
        st.switch_page("f.py")

# ================ FILTER SECTION ================
st.markdown('<div class="filter-section">', unsafe_allow_html=True)
st.write("**Filter by Status:**")

col1, col2, col3, col4 = st.columns(4)

with col1:
    show_all = st.checkbox("All Orders", value=True, key="filter_all")
with col2:
    show_pending = st.checkbox("Pending", key="filter_pending")
with col3:
    show_processing = st.checkbox("Processing", key="filter_processing")
with col4:
    show_delivered = st.checkbox("Delivered", key="filter_delivered")

st.markdown('</div>', unsafe_allow_html=True)

# ================ FETCH ORDERS ================
try:
    # Build status filter
    if show_all:
        query = f"""
        SELECT order_id, medicine_id, quantity, status, created_at, delivery_date, customer_name, phone, address
        FROM orders 
        WHERE user_id = {st.session_state['user_id']}
        ORDER BY created_at DESC
        """
    else:
        status_list = []
        if show_pending:
            status_list.append("'Pending'")
        if show_processing:
            status_list.append("'Processing'")
        if show_delivered:
            status_list.append("'Delivered'")
        
        if status_list:
            status_filter = ", ".join(status_list)
            query = f"""
            SELECT order_id, medicine_id, quantity, status, created_at, delivery_date, customer_name, phone, address
            FROM orders 
            WHERE user_id = {st.session_state['user_id']} AND status IN ({status_filter})
            ORDER BY created_at DESC
            """
        else:
            st.info("Select at least one status to filter orders.")
            st.stop()
    
    results = execute_custom_query(query)
    
    if results:
        st.success(f"✅ You have {len(results)} order(s)")
        
        for order in results:
            order_id, med_id, qty, status, created_at, delivery_date, cust_name, cust_phone, cust_addr = order
            
            # Determine status styling
            if status == "Pending":
                status_class = "status-pending"
                status_icon = "⏳"
            elif status == "Processing":
                status_class = "status-processing"
                status_icon = "🚚"
            else:
                status_class = "status-delivered"
                status_icon = "✅"
            
            # Render order card
            with st.container():
                st.markdown("""
                <div class="order-card">
                    <div class="order-header">
                        <div class="order-id">Order #{}</div>
                        <span class="status-badge {}">{} {}</span>
                    </div>
                </div>
                """.format(order_id, status_class, status_icon, status), unsafe_allow_html=True)
                
                # Create columns for order details
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="detail-row">
                        <div class="detail-label">🏥 Medicine ID</div>
                        <div class="detail-value">#{med_id}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="detail-row">
                        <div class="detail-label">📦 Quantity</div>
                        <div class="detail-value">{qty} units</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="detail-row">
                        <div class="detail-label">📅 Order Date</div>
                        <div class="detail-value">{created_at}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="detail-row">
                        <div class="detail-label">👤 Customer Name</div>
                        <div class="detail-value">{cust_name}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="detail-row">
                        <div class="detail-label">📱 Phone</div>
                        <div class="detail-value">{cust_phone}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="detail-row">
                        <div class="detail-label">🚚 Expected Delivery</div>
                        <div class="detail-value">{delivery_date if delivery_date else 'Being processed'}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.divider()
    
    else:
        st.markdown("""
        <div class="no-orders">
            <h2>📭 No Orders Found</h2>
            <p>You haven't placed any orders yet. Start by searching for medicines!</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Search Medicines", use_container_width=True):
            st.switch_page("pages/search_medicines.py")

except Exception as e:
    st.error(f"❌ Error fetching orders: {str(e)}")