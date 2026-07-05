import React from "react";
import { useEffect, useState } from "react";
import { apiRequest } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function SearchPage() {
  const { token } = useAuth();
  const [filters, setFilters] = useState({ q: "", category: "", manufacturer: "", min_price: "", max_price: "", exp_before: "" });
  const [medicines, setMedicines] = useState([]);
  const [status, setStatus] = useState("");

  async function loadMedicines() {
    const query = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) query.set(key, value);
    });
    const data = await apiRequest(`/medicines?${query.toString()}`, { token });
    setMedicines(data);
  }

  useEffect(() => {
    loadMedicines().catch((err) => setStatus(err.message));
  }, []);

  async function addToCart(medicineId) {
    try {
      await apiRequest("/orders/cart", {
        method: "POST",
        token,
        body: { medicine_id: medicineId, quantity: 1 },
      });
      setStatus("Added to cart");
    } catch (err) {
      setStatus(err.message);
    }
  }

  return (
    <section>
      <div className="panel hero-panel">
        <h2>Search Medicines with Advanced Filters</h2>
        <div className="filters-grid">
          <input placeholder="Name" value={filters.q} onChange={(e) => setFilters({ ...filters, q: e.target.value })} />
          <input placeholder="Category" value={filters.category} onChange={(e) => setFilters({ ...filters, category: e.target.value })} />
          <input placeholder="Manufacturer" value={filters.manufacturer} onChange={(e) => setFilters({ ...filters, manufacturer: e.target.value })} />
          <input placeholder="Min Price" type="number" value={filters.min_price} onChange={(e) => setFilters({ ...filters, min_price: e.target.value })} />
          <input placeholder="Max Price" type="number" value={filters.max_price} onChange={(e) => setFilters({ ...filters, max_price: e.target.value })} />
          <input placeholder="Expiry before" type="date" value={filters.exp_before} onChange={(e) => setFilters({ ...filters, exp_before: e.target.value })} />
        </div>
        <button className="primary-btn" onClick={() => loadMedicines().catch((err) => setStatus(err.message))}>Apply Filters</button>
        {status ? <p>{status}</p> : null}
      </div>

      <div className="cards-grid">
        {medicines.map((med) => (
          <article key={med.id} className="panel medicine-card">
            <h3>{med.medicine_name}</h3>
            <p>Category: {med.category || "N/A"}</p>
            <p>Maker: {med.manufacturer || "N/A"}</p>
            <p>Stock: {med.quantity}</p>
            <p className="price-tag">Rs {med.price}</p>
            <button className="accent-btn" onClick={() => addToCart(med.id)}>Add to Cart</button>
          </article>
        ))}
      </div>
    </section>
  );
}
