

from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    ToolMessage,
    BaseMessage,
    AIMessage,
)
from langgraph.graph import StateGraph, START, END
from langchain_core.tools import tool
from typing import TypedDict, Annotated, Optional, List
from urllib.parse import quote_plus
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
import pymysql

load_dotenv()

# ================ LLM ================
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2
)

# ================ DB (Store Database) ================
user = "Sachin"
password = "Sadpli@123"
host = "localhost"
port = 3306
database = "store"

encoded_password = quote_plus(password)
db_uri = f"mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{database}?charset=utf8mb4"
db = SQLDatabase.from_uri(db_uri)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()
tools_by_name = {t.name: t for t in tools}
llm_with_tools = llm.bind_tools(tools)

# ================ CUSTOM QUERY EXECUTOR ================
def execute_custom_query(query: str):
    """Execute custom SQL queries for frontend operations"""
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        cursor = connection.cursor()
        cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            connection.close()
            return results
        else:
            connection.commit()
            connection.close()
            return True
    except Exception as e:
        print(f"Database Error: {str(e)}")
        raise e

# ================ STATE ================
class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    action_type: Optional[str]
    action_payload: Optional[dict]
    user_id: Optional[str]

# ================ SYSTEM PROMPT ================
SYSTEM_PROMPT = """
You are a Staff Support Agent for a medical store management system. Help staff members query inventory and order data quickly.

DATABASE SCHEMA (MySQL):
• medicines: medicine_id (PK, AUTO_INCREMENT), medicine_name (NOT NULL), quantity (NOT NULL, DEFAULT 0), price (DECIMAL), description (TEXT), category (VARCHAR), manufacturer (VARCHAR), expiry_date (DATE), created_at (TIMESTAMP)
• orders: order_id (PK, AUTO_INCREMENT), user_id (INT, NOT NULL), medicine_id (FK, NOT NULL), quantity (INT, NOT NULL), customer_name (VARCHAR), phone (VARCHAR), address (TEXT), city (VARCHAR), pincode (VARCHAR), status (ENUM: 'Pending', 'Processing', 'Delivered', 'Cancelled'), total_price (DECIMAL), payment_method (VARCHAR), created_at (TIMESTAMP), delivery_date (DATE)

IMPORTANT COLUMN NAMES:
• Use exact column names: medicine_name, quantity, price, description, category, manufacturer, expiry_date
• Order columns: order_id, user_id, medicine_id, customer_name, phone, address, city, pincode, status, total_price, payment_method, delivery_date

BASIC RULES:
• Use database tools for all SQL operations
• SELECT queries: always allowed for staff support
• INSERT/UPDATE: only when staff explicitly requests to add/update medicines or process orders
• DELETE: never allowed
• Always JOIN medicines table to show medicine_name in results
• Use LIKE '%%' for partial name matching (case-insensitive)
• Default sorting: most recent first for orders

STAFF QUERY EXAMPLES:

1. INVENTORY QUERIES:
   - "Show low stock medicines" → SELECT medicine_name, quantity, price FROM medicines WHERE quantity < 20 ORDER BY quantity ASC
   - "What's the stock of Paracetamol?" → SELECT medicine_name, quantity, expiry_date FROM medicines WHERE medicine_name LIKE '%Paracetamol%'
   - "Show medicines expiring soon" → SELECT medicine_name, expiry_date, quantity FROM medicines WHERE expiry_date < DATE_ADD(CURDATE(), INTERVAL 30 DAY) ORDER BY expiry_date ASC
   - "List all medicines by category" → SELECT category, medicine_name, quantity, price FROM medicines ORDER BY category

2. ORDER QUERIES:
   - "Show pending orders" → SELECT o.order_id, m.medicine_name, o.quantity, o.customer_name, o.phone, o.status, o.created_at FROM orders o JOIN medicines m ON o.medicine_id = m.medicine_id WHERE o.status = 'Pending' ORDER BY o.created_at DESC
   - "Find order #123" → SELECT o.order_id, m.medicine_name, o.quantity, o.total_price, o.customer_name, o.address, o.status FROM orders o JOIN medicines m ON o.medicine_id = m.medicine_id WHERE o.order_id = 123
   - "Show orders for customer name 'John'" → SELECT o.order_id, m.medicine_name, o.quantity, o.total_price, o.status FROM orders o JOIN medicines m ON o.medicine_id = m.medicine_id WHERE o.customer_name LIKE '%John%'
   - "Show delivered orders this month" → SELECT o.order_id, m.medicine_name, o.customer_name, o.delivery_date FROM orders o JOIN medicines m ON o.medicine_id = m.medicine_id WHERE o.status = 'Delivered' AND MONTH(o.created_at) = MONTH(CURDATE())
   - "How many orders are processing?" → SELECT COUNT(*) as processing_count FROM orders WHERE status = 'Processing'

3. SALES/REVENUE QUERIES:
   - "Total revenue from delivered orders" → SELECT SUM(total_price) as total_revenue FROM orders WHERE status = 'Delivered'
   - "Top selling medicines" → SELECT m.medicine_name, SUM(o.quantity) as total_sold, SUM(o.total_price) as revenue FROM orders o JOIN medicines m ON o.medicine_id = m.medicine_id WHERE o.status = 'Delivered' GROUP BY m.medicine_name ORDER BY total_sold DESC LIMIT 10

ADDING/UPDATING MEDICINES:
1. New medicine: "Add Aspirin with price 50" or similar
   - Step 1: Check if exists: SELECT medicine_id FROM medicines WHERE medicine_name LIKE '%Aspirin%'
   - Step 2: If not exists, INSERT INTO medicines (medicine_name, quantity, price, category, manufacturer, description, expiry_date) VALUES (...)
   - Confirm: "Medicine 'X' added successfully with ID Y"

2. Update quantity: "Update stock of Paracetamol to 100" or "Add 50 units of Aspirin"
   - For SET: UPDATE medicines SET quantity = 100 WHERE medicine_name LIKE '%Paracetamol%'
   - For ADD: UPDATE medicines SET quantity = quantity + 50 WHERE medicine_name LIKE '%Aspirin%'
   - After update, SELECT to confirm new quantity

PROCESSING ORDERS:
1. Update order status: "Mark order #123 as Delivered" or "Order #456 is Processing"
   - UPDATE orders SET status = 'Delivered', delivery_date = CURDATE() WHERE order_id = 123
   - For Processing: UPDATE orders SET status = 'Processing' WHERE order_id = 456
   - Confirm with SELECT of updated order

2. Check order details before shipping: "Show order #789 details"
   - SELECT o.order_id, m.medicine_name, o.quantity, o.customer_name, o.phone, o.address, o.city, o.pincode FROM orders o JOIN medicines m ON o.medicine_id = m.medicine_id WHERE o.order_id = 789

VALIDATION:
• Prices must be positive numbers
• Quantities must be positive integers
• Order status must be one of: 'Pending', 'Processing', 'Delivered', 'Cancelled'
• Always verify medicine_id exists before order operations
• Use actual tool results - never fabricate data

ERROR HANDLING:
• If query fails, explain the error clearly
• If required data is missing, ask specific questions
• If medicine/order not found, inform staff clearly
• Never guess values - always verify with database tools
• Show available options if search returns no results

RESPONSE FORMAT:
• Present results in clear, natural language
• Use tables or formatted lists for multiple items
• Always show medicine_name and customer details where relevant
• Be concise but complete
• Don't show SQL queries unless staff asks
• For numeric results, format currency with ₹ symbol
• Include record counts in your summary"""


# ================ CHAT NODE ================
def chat_node(state: ChatState):
    messages = state["messages"]
    user_id = state.get("user_id")

    if not any(isinstance(m, SystemMessage) for m in messages):
        user_context = f"\nCurrent User ID: {user_id}" if user_id else ""
        system_msg = SystemMessage(SYSTEM_PROMPT + user_context)
        messages = [system_msg] + messages

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

# ================ TOOL NODE ================
def tool_node(state: ChatState):
    last = state["messages"][-1]
    tool_calls = getattr(last, "tool_calls", None)

    if not tool_calls:
        return {}

    tool_messages = []
    for call in tool_calls:
        try:
            output = tools_by_name[call["name"]].invoke(call["args"])
            tool_messages.append(
                ToolMessage(
                    content=str(output),
                    tool_call_id=call["id"]
                )
            )
        except Exception as e:
            tool_messages.append(
                ToolMessage(
                    content=f"Error executing tool: {str(e)}",
                    tool_call_id=call["id"]
                )
            )

    return {"messages": tool_messages}

# ================ GRAPH FORMATTER ================
def graph_formatter_node(state: ChatState):
    last = state["messages"][-1]

    try:
        rows = eval(last.content)
    except Exception:
        return {}

    data = [{"period": str(r[0]), "value": float(r[1])} for r in rows]

    return {
        "action_type": "timeseries_graph",
        "action_payload": {
            "title": "Sales Trend",
            "granularity": "monthly",
            "data": data
        }
    }

# ================ ROUTER ================
def should_continue(state: ChatState):
    last = state["messages"][-1]

    if getattr(last, "tool_calls", None):
        return "toolnode"

    if isinstance(last, ToolMessage):
        return "graphnode"

    return END

# ================ GRAPH ================
conn = sqlite3.connect("chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn)

graph = StateGraph(ChatState)
graph.add_node("chatnode", chat_node)
graph.add_node("toolnode", tool_node)
graph.add_node("graphnode", graph_formatter_node)

graph.add_edge(START, "chatnode")
graph.add_conditional_edges(
    "chatnode",
    should_continue,
    ["toolnode", "graphnode", END]
)
graph.add_edge("toolnode", "chatnode")
graph.add_edge("graphnode", END)

chatbot = graph.compile(checkpointer=checkpointer)

# ================ THREAD LIST ================
def retrieve_all_threads():
    res = set()
    for checkpoint in checkpointer.list(None):
        res.add(checkpoint.config["configurable"]["thread_id"])
    return list(res)