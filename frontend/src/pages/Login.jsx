import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { errMsg } from "../api";
import { useAuth } from "../auth";
import { Btn, Field, Input } from "../components/ui";
import ThemeToggle from "../components/ThemeToggle";

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/" replace />;

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(form.username.trim(), form.password);
      navigate("/");
    } catch (err) {
      setError(err.response?.status === 401 ? "Invalid username or password." : errMsg(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      {/* left side: brand panel */}
      <div className="relative hidden overflow-hidden bg-gradient-to-br from-indigo-400 to-brand-dark lg:block">
        <div className="absolute -left-24 -top-24 h-96 w-96 rounded-full bg-white/10" />
        <div className="absolute -bottom-32 -right-20 h-[28rem] w-[28rem] rounded-full bg-white/10" />
        <div className="relative flex h-full flex-col justify-center px-16 text-white">
          <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-white text-2xl font-semibold text-brand">H</div>
          <h1 className="text-4xl font-semibold">HRMS</h1>
          <p className="mt-2 text-lg text-white/90">Human Resource Management System</p>
        </div>
      </div>

      {/* right side: login form */}
      <div className="relative flex items-center justify-center bg-page p-6">
        <ThemeToggle className="absolute right-6 top-6" />
        <form onSubmit={submit} className="w-full max-w-sm space-y-5 rounded-2xl bg-card p-8 shadow-[0_2px_14px_rgba(30,41,90,0.08)]">
          <div>
            <h2 className="text-xl font-semibold text-slate-800">Sign in</h2>
            <p className="text-sm text-slate-400">Enter your account details</p>
          </div>

          {error && <div className="rounded-xl bg-rose-50 px-4 py-2 text-sm text-rose-600">{error}</div>}

          <Field label="Username or email">
            <Input autoFocus required value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
          </Field>
          <Field label="Password">
            <Input type="password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          </Field>

          <Btn className="w-full" disabled={busy}>{busy ? "Signing in..." : "Sign in"}</Btn>
        </form>
      </div>
    </div>
  );
}
