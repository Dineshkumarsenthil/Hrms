import { createContext, useContext, useEffect, useState } from "react";
import api, { tokens } from "./api";

const Ctx = createContext(null);
export const useAuth = () => useContext(Ctx);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!tokens.access);

  useEffect(() => {
    if (!tokens.access) return;
    api.get("/auth/me/").then((r) => setUser(r.data)).catch(() => tokens.clear()).finally(() => setLoading(false));
  }, []);

  const login = async (username, password) => {
    const { data } = await api.post("/auth/login/", { username, password });
    tokens.set(data);
    setUser(data.user);
    return data.user;
  };

  const logout = async () => {
    try { await api.post("/auth/logout/", { refresh: tokens.refresh }); } catch { /* token may already be invalid */ }
    tokens.clear();
    setUser(null);
  };

  const isStaff = user && (user.role === "ADMIN" || user.role === "HR");
  const isAdmin = user && user.role === "ADMIN";
  return <Ctx.Provider value={{ user, loading, login, logout, isStaff, isAdmin, refreshUser: () => api.get("/auth/me/").then((r) => setUser(r.data)) }}>{children}</Ctx.Provider>;
}
