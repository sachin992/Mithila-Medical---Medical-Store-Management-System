import React from "react";
import { useEffect, useState } from "react";
import { apiRequest } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function StaffPage() {
  const { token, user } = useAuth();
  const [suggestions, setSuggestions] = useState([]);
  const [medicineId, setMedicineId] = useState("");
  const [patchData, setPatchData] = useState({ quantity: "", price: "" });
  const [status, setStatus] = useState("");

  useEffect(() => {
    if (user?.role === "admin") {
      apiRequest("/staff/inventory/reorder-suggestions", { token })
        .then(setSuggestions)
        .catch((err) => setStatus(err.message));
    }
  }, [token, user]);

  if (user?.role !== "admin") {
    return <p>Admin access only.</p>;
  }

  async function applyPatch() {
    try {
      await apiRequest(`/staff/medicines/${medicineId}`, {
        method: "PATCH",
        token,
        body: {
          quantity: patchData.quantity ? Number(patchData.quantity) : undefined,
          price: patchData.price ? Number(patchData.price) : undefined,
        },
      });
      setStatus("Medicine updated");
    } catch (err) {
      setStatus(err.message);
    }
  }

  async function uploadCsv(file) {
    const formData = new FormData();
    formData.append("file", file);
    try {
      const data = await apiRequest("/staff/medicines/bulk-import", {
        method: "POST",
        token,
        body: formData,
        isFormData: true,
      });
      setStatus(`CSV import done. Created: ${data.created}, Updated: ${data.updated}`);
    } catch (err) {
      setStatus(err.message);
    }
  }

  return (
    <section className="dual-grid">
      <div className="panel">
        <h2>Admin Inventory Tools</h2>
        <input placeholder="Medicine ID" value={medicineId} onChange={(e) => setMedicineId(e.target.value)} />
        <input placeholder="New Quantity" type="number" value={patchData.quantity} onChange={(e) => setPatchData({ ...patchData, quantity: e.target.value })} />
        <input placeholder="New Price" type="number" value={patchData.price} onChange={(e) => setPatchData({ ...patchData, price: e.target.value })} />
        <button className="primary-btn" onClick={applyPatch}>Edit Medicine</button>

        <label className="file-input">
          Bulk Import CSV
          <input type="file" accept=".csv" onChange={(e) => e.target.files?.[0] && uploadCsv(e.target.files[0])} />
        </label>
        {status ? <p>{status}</p> : null}
      </div>

      <div className="panel">
        <h2>Low-Stock Reorder Suggestions</h2>
        <ul>
          {suggestions.map((s) => (
            <li key={s.medicine_id}>{s.medicine_name}: stock {s.current_quantity}, reorder {s.suggested_reorder}</li>
          ))}
        </ul>
      </div>
    </section>
  );
}
