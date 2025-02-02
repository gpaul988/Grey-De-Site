import { useEffect, useState } from "react";
import useRole from "../hooks/useRole";
import { useRouter } from "next/router";

const AdminPage = () => {
  const role = useRole();
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (role) {
      if (role !== "admin" && role !== "super_admin") {
        router.push("/403");  // Redirect to "Access Denied" page if not admin or super admin
      }
      setLoading(false);
    }
  }, [role, router]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return <div>Admin Dashboard</div>;
};

export default AdminPage;