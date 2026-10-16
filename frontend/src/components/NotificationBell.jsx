import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api";
import Icon from "./Icons";
import { fmtAgo } from "./ui";

// Bell in the top bar: unread badge (refreshed every 30 s) + a dropdown with the latest notifications
export default function NotificationBell() {
  const navigate = useNavigate();
  const box = useRef(null);
  const [open, setOpen] = useState(false);
  const [unread, setUnread] = useState(0);
  const [items, setItems] = useState([]);

  const loadCount = useCallback(() => {
    api.get("/notifications/unread-count/").then((r) => setUnread(r.data.unread)).catch(() => {});
  }, []);

  useEffect(() => {
    loadCount();
    const timer = setInterval(loadCount, 30000);
    return () => clearInterval(timer);
  }, [loadCount]);

  // close the dropdown when clicking anywhere else
  useEffect(() => {
    const onClick = (e) => box.current && !box.current.contains(e.target) && setOpen(false);
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const toggle = async () => {
    setOpen(!open);
    if (!open) {
      const { data } = await api.get("/notifications/", { params: { page_size: 6 } });
      setItems(data.results);
      loadCount();
    }
  };

  const openItem = async (n) => {
    if (!n.is_read) {
      await api.post(`/notifications/${n.id}/mark-read/`).catch(() => {});
      loadCount();
    }
    setOpen(false);
    if (n.link) navigate(n.link);
  };

  const markAll = async () => {
    await api.post("/notifications/mark-all-read/");
    setItems(items.map((n) => ({ ...n, is_read: true })));
    setUnread(0);
  };

  return (
    <div className="relative" ref={box}>
      <button onClick={toggle} title="Notifications" className="relative text-slate-500 hover:text-brand">
        <Icon name="bell" />
        {unread > 0 && (
          <span className="absolute -right-2 -top-2 flex h-4 min-w-4 items-center justify-center rounded-full bg-rose-500 px-1 text-[10px] font-medium text-white">
            {unread > 99 ? "99+" : unread}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-9 z-40 w-80 max-w-[85vw] rounded-xl bg-card shadow-lg ring-1 ring-slate-100">
          <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
            <span className="text-sm font-semibold text-slate-800">Notifications</span>
            <button onClick={markAll} disabled={unread === 0} className="text-xs font-medium text-brand disabled:text-slate-300">Mark all read</button>
          </div>
          <div className="max-h-80 overflow-y-auto">
            {items.length === 0 && <div className="p-6 text-center text-sm text-slate-400">You are all caught up.</div>}
            {items.map((n) => (
              <button key={n.id} onClick={() => openItem(n)} className="flex w-full gap-2 border-b border-slate-100 px-4 py-3 text-left last:border-0 hover:bg-slate-50">
                <span className={`mt-1.5 h-2 w-2 shrink-0 rounded-full ${n.is_read ? "bg-transparent" : "bg-brand"}`} />
                <span className="min-w-0">
                  <span className={`block truncate text-sm ${n.is_read ? "text-slate-600" : "font-semibold text-slate-800"}`}>{n.title}</span>
                  <span className="line-clamp-2 text-xs text-slate-500">{n.message}</span>
                  <span className="text-[11px] text-slate-400">{fmtAgo(n.created_at)}</span>
                </span>
              </button>
            ))}
          </div>
          <Link to="/notifications" onClick={() => setOpen(false)} className="block border-t border-slate-100 px-4 py-3 text-center text-sm font-medium text-brand hover:bg-slate-50">
            View all
          </Link>
        </div>
      )}
    </div>
  );
}
