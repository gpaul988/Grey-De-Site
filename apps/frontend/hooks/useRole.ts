import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import axios from "axios";

// Hook to get the current user's role
const useRole = () => {
  const [role, setRole] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const getUserRole = async () => {
      try {
        const response = await axios.get("/api/current-user");
        setRole(response.data.role);
      } catch {
        setRole(null);
        router.push("/login");
      }
    };

    getUserRole();
  }, [router]);

  return role;
};

export default useRole;