import { useUser } from "@/context/UserContext"
import Link from "next/link"
import CompanyList from "@/components/admin/CompanyList";

const AdminDashboard = () => {
  const { user, loading } = useUser();

  if (loading) return <p>Loading...</p>;
  if (!user || user.role === "user") return <p>Access Denied</p>;

  return (
    <div>
      <h1 className="text-2xl font-bold">Admin Dashboard</h1>

      {user.role === "super_admin" && (
        <div className="mt-4">
          <h2 className="text-xl">Super Admin Features</h2>
          <Link href="/admin/companies">Manage Companies</Link>
          <Link href="/admin/users">Manage Users</Link>
        </div>
      )}

      <CompanyList />

      {user.role === "admin" && (
        <div className="mt-4">
          <h2 className="text-xl">Admin Features</h2>
          <Link href="/admin/users">Manage Users (Your Company Only)</Link>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;