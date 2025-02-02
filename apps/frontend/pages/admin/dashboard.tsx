import useRole from "@/hooks/useRole";
import { useEffect } from "react";
import { useRouter } from "next/router";

const AdminDashboard = () => {
  const role = useRole();
  const router = useRouter();

  useEffect(() => {
    if (role === "user") {
      router.push("/403"); // Redirect to Access Denied if user tries to access the admin dashboard
    }
  }, [role, router]);

  return (
    <div>
      <h1>Welcome to the Admin Dashboard</h1>
      {role === "super_admin" && (
        <div>
          <h2>Super Admin Features</h2>
          <button>Create New Company</button>
        </div>
      )}

      {role === "admin" && (
        <div>
          <h2>Admin Features</h2>
          <button>Manage Users</button>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;