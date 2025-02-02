import { useState, useEffect } from "react";
import axios from "axios";

interface Subscription {
  id: number;
  user: {
    username: string;
  };
  plan: {
    name: string;
  };
  status: string;
  auto_renew: boolean;
}

const AdminSubscriptionsPage = () => {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);

  const fetchSubscriptions = async () => {
    try {
      const { data } = await axios.get("/api/admin/subscriptions/");
      setSubscriptions(data);
    } catch (error) {
      console.error("Error fetching subscriptions:", error);
    }
  };

  useEffect(() => {
    fetchSubscriptions().catch((error) => {
      console.error("Error in useEffect:", error);
    });
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Admin Subscription Management</h1>
      {subscriptions.map((sub) => (
        <div key={sub.id} className="border p-4 mt-4">
          <p>User: {sub.user.username}</p>
          <p>Plan: {sub.plan.name}</p>
          <p>Status: {sub.status}</p>
          <p>Auto-Renew: {sub.auto_renew ? "Yes" : "No"}</p>
        </div>
      ))}
    </div>
  );
};

export default AdminSubscriptionsPage;