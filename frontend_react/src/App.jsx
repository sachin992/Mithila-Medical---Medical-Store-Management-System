import React from "react";
import { Link, Navigate, Route, Routes, useNavigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import SearchPage from "./pages/SearchPage";
import CartPage from "./pages/CartPage";
import OrdersPage from "./pages/OrdersPage";
import StaffPage from "./pages/StaffPage";
import AssistantPage from "./pages/AssistantPage";
import { useAuth } from "./context/AuthContext";

function PrivateRoute({ children }) {
  const { token } = useAuth();
  return token ? children : <Navigate to="/login" replace />;
}

function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <h1>Mithila Medical</h1>
          <p>Fast, Safe Pharmacy Operations</p>
        </div>
        <nav>
          <Link to="/search">Search</Link>
          <Link to="/cart">Cart</Link>
          <Link to="/orders">Orders</Link>
          {user?.role === "admin" ? <Link to="/staff">Admin</Link> : null}
          {user?.role === "admin" ? <Link to="/assistant">Analytics Chat</Link> : null}
        </nav>
        <button
          className="ghost-btn"
          onClick={() => {
            logout();
            navigate("/login");
          }}
        >
          Logout
        </button>
      </header>
      <main className="content-wrap">
        <Routes>
          <Route path="/search" element={<SearchPage />} />
          <Route path="/cart" element={<CartPage />} />
          <Route path="/orders" element={<OrdersPage />} />
          <Route path="/staff" element={<StaffPage />} />
          <Route path="/assistant" element={<AssistantPage />} />
          <Route path="*" element={<Navigate to="/search" replace />} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <PrivateRoute>
            <AppLayout />
          </PrivateRoute>
        }
      />
    </Routes>
  );
}
