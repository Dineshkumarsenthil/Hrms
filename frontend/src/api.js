import axios from "axios";

export const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";
const api = axios.create({ baseURL: API });

export const tokens = {
  get access() { return localStorage.getItem("access"); },
  get refresh() { return localStorage.getItem("refresh"); },
  set({ access, refresh }) {
    if (access) localStorage.setItem("access", access);
    if (refresh) localStorage.setItem("refresh", refresh);
  },
  clear() { localStorage.removeItem("access"); localStorage.removeItem("refresh"); },
};

api.interceptors.request.use((cfg) => {
  if (tokens.access) cfg.headers.Authorization = `Bearer ${tokens.access}`;
  return cfg;
});

let refreshing = null;
api.interceptors.response.use(
  (r) => r,
  async (err) => {
    const orig = err.config;
    const isAuthCall = orig?.url?.includes("/auth/login") || orig?.url?.includes("/auth/refresh");
    if (err.response?.status === 401 && !orig._retry && tokens.refresh && !isAuthCall) {
      orig._retry = true;
      try {
        refreshing = refreshing || axios.post(`${API}/auth/refresh/`, { refresh: tokens.refresh }).finally(() => (refreshing = null));
        const { data } = await refreshing;
        tokens.set(data);
        orig.headers.Authorization = `Bearer ${data.access}`;
        return api(orig);
      } catch {
        tokens.clear();
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);

// Turn any API error into one readable string
export function errMsg(e) {
  const d = e?.response?.data;
  if (!d) return e?.message || "Something went wrong";
  const flat = (v) => (Array.isArray(v) ? v.map(flat).join(" ") : typeof v === "object" && v ? Object.entries(v).map(([k, x]) => `${k}: ${flat(x)}`).join(" | ") : String(v));
  if (d.details) return `${d.error ? d.error + " - " : ""}${flat(d.details)}`;
  return d.error || d.detail || flat(d);
}

// Authenticated file download (blobs)
export async function download(url, filename, params) {
  const res = await api.get(url, { params, responseType: "blob" });
  const href = URL.createObjectURL(res.data);
  const a = document.createElement("a");
  a.href = href;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(href);
}

export default api;
