import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth";
import Layout from "./components/Layout";
import { Spinner } from "./components/ui";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Profile from "./pages/Profile";
import Employees from "./pages/Employees";
import Attendance from "./pages/Attendance";
import Leaves from "./pages/Leaves";
import Payroll from "./pages/Payroll";
import Reports from "./pages/Reports";
import Holidays from "./pages/Holidays";
import Shifts from "./pages/Shifts";
import Notifications from "./pages/Notifications";
import { AuditLogs, EmailLogs, Users } from "./pages/Admin";

function Guard({ children, staff, admin }) {
  const { user, loading, isStaff, isAdmin } = useAuth();
  if (loading) return <Spinner />;
  if (!user) return <Navigate to="/login" replace />;
  if ((staff && !isStaff) || (admin && !isAdmin)) return <Navigate to="/" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<Guard><Layout /></Guard>}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/attendance" element={<Attendance />} />
        <Route path="/leaves" element={<Leaves />} />
        <Route path="/payroll" element={<Payroll />} />
        <Route path="/holidays" element={<Holidays />} />
        <Route path="/shifts" element={<Shifts />} />
        <Route path="/notifications" element={<Notifications />} />
        <Route path="/employees" element={<Guard staff><Employees /></Guard>} />
        <Route path="/reports" element={<Guard staff><Reports /></Guard>} />
        <Route path="/audit" element={<Guard staff><AuditLogs /></Guard>} />
        <Route path="/emails" element={<Guard staff><EmailLogs /></Guard>} />
        <Route path="/users" element={<Guard admin><Users /></Guard>} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
