import streamlit as st
from b import execute_custom_query

# ================ PAGE CONFIG ================
st.set_page_config(
    page_title="Search Medicines - Mithila Medical",
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
    
    .user-section {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .btn-back {
        background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-back:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(149, 165, 166, 0.3);
    }
    
    .search-container {
        margin-bottom: 30px;
    }
    
    .search-input {
        width: 100%;
        padding: 15px 20px;
        font-size: 1.1em;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .search-input:focus {
        outline: none;
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }
    
    .medicine-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 25px;
        margin-bottom: 30px;
    }
    
    .medicine-card {
        background: white;
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border-left: 5px solid #06a77d;
        transition: all 0.3s ease;
    }
    
    .medicine-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }
    
    .medicine-card h3 {
        color: #0066cc;
        margin: 0 0 12px 0;
        font-size: 1.3em;
    }
    
    .medicine-card p {
        color: #666;
        margin: 8px 0;
        font-size: 0.95em;
    }
    
    .price-tag {
        color: #06a77d;
        font-weight: 700;
        font-size: 1.2em;
        margin: 10px 0;
    }
    
    .stock-info {
        background: #f0f8f5;
        padding: 8px 12px;
        border-radius: 6px;
        color: #06a77d;
        font-weight: 600;
        margin: 10px 0;
        font-size: 0.9em;
    }
    
    .btn-group {
        display: flex;
        gap: 10px;
        margin-top: 15px;
    }
    
    .btn-add-order {
        flex: 1;
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        padding: 12px;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-add-order:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 20px rgba(52, 152, 219, 0.3);
    }
    
    .no-results {
        text-align: center;
        padding: 60px 20px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
    }
    
    .no-results h2 {
        color: #666;
        margin-bottom: 10px;
    }
    
    .no-results p {
        color: #999;
        font-size: 0.95em;
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
    <div class="navbar-top" style="justify-content: flex-end; gap: 20px;">
        <div class="user-section">
            <div>
                <p style="margin: 0; color: #0066cc; font-weight: 700;">{st.session_state['user_full_name']}</p>
                <p style="margin: 0; color: #999; font-size: 0.85em;">{st.session_state['user_email']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ================ PAGE HEADER ================
st.markdown("""
<div class="page-header">
    <h1>🔍 Search Medicines</h1>
</div>
""", unsafe_allow_html=True)

# ================ SEARCH SECTION ================
col1, col2 = st.columns([5, 1])

with col1:
    search_term = st.text_input(
        "Search medicines by name or type:",
        placeholder="e.g., Paracetamol, Aspirin, Cough Syrup",
        key="medicine_search"
    )

with col2:
    if st.button("🏠 Back Home", use_container_width=True):
        st.switch_page("f.py")

# ================ SEARCH RESULTS ================
if search_term:
    try:
        query = f"""
        SELECT medicine_id, medicine_name, quantity, price, description 
        FROM medicines 
        WHERE quantity > 0 AND medicine_name LIKE '%{search_term}%'
        LIMIT 50
        """
        results = execute_custom_query(query)
        
        if results:
            st.success(f"✅ Found {len(results)} medicine(s)")
            
            st.markdown('<div class="medicine-grid">', unsafe_allow_html=True)
            
            cols = st.columns(3)
            
            for idx, medicine in enumerate(results):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div class="medicine-card">
                        <h3>{medicine[1]}</h3>
                        <p><strong>Medicine ID:</strong> #{medicine[0]}</p>
                        <div class="price-tag">₹{medicine[3]}</div>
                        <div class="stock-info">📦 {medicine[2]} units available</div>
                        <p><strong>Description:</strong></p>
                        <p>{medicine[4] if medicine[4] else 'No description available'}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"➕ Add to Order", key=f"add_med_{idx}", use_container_width=True):
                        st.session_state["order_data"] = {
                            "medicine_id": medicine[0],
                            "medicine_name": medicine[1],
                            "price": medicine[3],
                            "max_quantity": medicine[2]
                        }
                        st.switch_page("pages/place_order.py")
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="no-results">
                <h2>❌ No medicines found</h2>
                <p>Try searching with different keywords</p>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Error searching medicines: {str(e)}")
else:
    st.markdown("""
    <div class="no-results" style="padding: 100px 20px;">
        <h2>🔍 Start Searching</h2>
        <p>Enter a medicine name to see available products</p>
    </div>
    """, unsafe_allow_html=True)