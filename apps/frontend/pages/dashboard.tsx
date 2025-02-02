import { getSession } from "next-auth/react";
import { useRouter } from "next/router";
import { useEffect, useState } from "react";
import FileUpload from "@/components/FileUpload";

interface User {
  id: string;
  role: string;
  email: string;
  accessToken: string;
}

const Dashboard = () => {
  const [user, setUser] = useState<User | null>(null);
  const router = useRouter();

  useEffect(() => {
    const loadSession = async () => {
      const session = await getSession();
      if (!session) router.push("/login");
      else setUser(session.user as User);
    };
    loadSession();
  }, [router]);

  if (!user) return <p>Loading...</p>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Welcome, {user.email}</h1>
      <p>Your role: {user.role}</p>
      <FileUpload />
    </div>
  );
};

export default Dashboard;