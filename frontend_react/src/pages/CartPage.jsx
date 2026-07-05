import React from "react";
import { useEffect, useState } from "react";
import { apiRequest } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function CartPage() {
  const { token, user } = useAuth();
  const [cart, setCart] = useState({ items: [], total: 0 });
  const [message, setMessage] = useState("");
  const [checkout, setCheckout] = useState({
    customer_name: user?.full_name || "",
    phone: "",
    address: "",
    city: "",
    pincode: "",
    payment_method: "COD",
  });

  async function loadCart() {
    const data = await apiRequest("/orders/cart", { token });
    setCart(data);
  }

  useEffect(() => {
    loadCart().catch((err) => setMessage(err.message));
  }, []);

  async function removeItem(id) {
    try {
      await apiRequest(`/orders/cart/${id}`, { method: "DELETE", token });
      await loadCart();
    } catch (err) {
      setMessage(err.message);
    }
  }

  async function placeOrder() {
    try {
      const data = await apiRequest("/orders/checkout", { method: "POST", token, body: checkout });
      setMessage(`Order #${data.id} placed. Invoice ${data.invoice.invoice_id}`);
      await loadCart();
    } catch (err) {
      setMessage(err.message);
    }
  }

  return (
    <section className="dual-grid">
      <div className="panel">
        <h2>Cart (Multi-item)</h2>
        {cart.items.map((item) => (
          <div key={item.id} className="list-row">
            <div>
              <strong>{item.medicine_name}</strong>
              <p>{item.quantity} x Rs {item.unit_price}</p>
            </div>
            <div>
              <span>Rs {item.line_total}</span>
              <button className="ghost-btn" onClick={() => removeItem(item.id)}>Remove</button>
            </div>
          </div>
        ))}
        <h3>Total: Rs {cart.total}</h3>
      </div>
      <div className="panel">
        <h2>Checkout + Payment</h2>
        <input placeholder="Full Name" value={checkout.customer_name} onChange={(e) => setCheckout({ ...checkout, customer_name: e.target.value })} />
        <input placeholder="Phone" value={checkout.phone} onChange={(e) => setCheckout({ ...checkout, phone: e.target.value })} />
        <textarea placeholder="Address" value={checkout.address} onChange={(e) => setCheckout({ ...checkout, address: e.target.value })} />
        <input placeholder="City" value={checkout.city} onChange={(e) => setCheckout({ ...checkout, city: e.target.value })} />
        <input placeholder="Pincode" value={checkout.pincode} onChange={(e) => setCheckout({ ...checkout, pincode: e.target.value })} />
        <select value={checkout.payment_method} onChange={(e) => setCheckout({ ...checkout, payment_method: e.target.value })}>
          <option value="COD">Cash on Delivery</option>
          <option value="UPI">UPI</option>
          <option value="CARD">Card</option>
        </select>
        <button className="primary-btn" onClick={placeOrder}>Place Order</button>
        {message ? <p>{message}</p> : null}
      </div>
    </section>
  );
}
