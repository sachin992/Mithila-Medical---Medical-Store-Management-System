import React from "react";
import { createContext, useContext, useMemo, useState } from "react";
import { apiRequest } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("user");
    return raw ? JSON.parse(raw) : null;
  });

  const login = async (payload, mode) => {
    const endpoint = mode === "signup" ? "/auth/signup" : "/auth/login";
    const data = await apiRequest(endpoint, { method: "POST", body: payload });
    setToken(data.access_token);
    setUser({ user_id: data.user_id, full_name: data.full_name, role: data.role });
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("user", JSON.stringify({ user_id: data.user_id, full_name: data.full_name, role: data.role }));
  };

  const logout = () => {
    setToken("");
    setUser(null);
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  };

  const value = useMemo(() => ({ token, user, login, logout }), [token, user]);
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("AuthContext missing");
  return ctx;
}
