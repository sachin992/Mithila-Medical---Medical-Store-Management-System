import React from "react";
import { useEffect, useState } from "react";
import { apiRequest } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function OrdersPage() {
  const { token } = useAuth();
  const [orders, setOrders] = useState([]);
  const [msg, setMsg] = useState("");

  async function loadOrders() {
    const data = await apiRequest("/orders", { token });
    setOrders(data);
  }

  useEffect(() => {
    loadOrders().catch((err) => setMsg(err.message));
  }, []);

  async function cancelOrder(id) {
    try {
      await apiRequest(`/orders/${id}/cancel`, { method: "POST", token });
      setMsg(`Order #${id} cancelled`);
      await loadOrders();
    } catch (err) {
      setMsg(err.message);
    }
  }

  return (
    <section>
      <h2>Order Tracking + Timeline + Invoice</h2>
      {msg ? <p>{msg}</p> : null}
      <div className="cards-grid">
        {orders.map((order) => (
          <article className="panel" key={order.id}>
            <h3>Order #{order.id}</h3>
            <p>Status: {order.status}</p>
            <p>Total: Rs {order.total_price}</p>
            <p>Invoice: {order.invoice?.invoice_id}</p>
            <h4>Medicines</h4>
            <ul>
              {order.items.map((item) => (
                <li key={`${order.id}-${item.medicine_id}`}>{item.medicine_name} ({item.quantity})</li>
              ))}
            </ul>
            <h4>Timeline</h4>
            <ul>
              {order.timeline.map((event, idx) => (
                <li key={`${order.id}-t-${idx}`}>{event.event_type} - {new Date(event.created_at).toLocaleString()}</li>
              ))}
            </ul>
            {order.status === "Pending" || order.status === "Processing" ? (
              <button className="ghost-btn" onClick={() => cancelOrder(order.id)}>Cancel in Window</button>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}
