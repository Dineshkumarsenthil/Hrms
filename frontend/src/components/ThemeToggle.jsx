import { useState } from "react";
import Icon from "./Icons";

const STORAGE_KEY = "hrms-theme";

// Sun / moon button that switches between light and dark mode.
// The choice is saved in the browser, so it is remembered next time.
export default function ThemeToggle({ className = "" }) {
  const [dark, setDark] = useState(document.documentElement.classList.contains("dark"));

  const toggle = () => {
    const next = !dark;
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem(STORAGE_KEY, next ? "dark" : "light");
    setDark(next);
  };

  return (
    <button
      onClick={toggle}
      title={dark ? "Switch to light mode" : "Switch to dark mode"}
      className={`flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 text-slate-500 hover:text-brand ${className}`}
    >
      <Icon name={dark ? "sun" : "moon"} className="h-4 w-4" />
    </button>
  );
}
