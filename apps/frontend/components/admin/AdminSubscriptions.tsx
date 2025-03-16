import { useEffect, useState } from "react";
import axios from "axios";

type Subscription = {
  user: string;
  plan_name: string;
  status: string;
  auto_renewal: boolean;
};

const AdminSubscriptions = () => {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);

  useEffect(() => {
    axios
      .get("/api/payments/admin-subscriptions-overview/", {
        headers: { Authorization: `Bearer ${localStorage.getItem("adminToken")}` },
      })
      .then((response) => setSubscriptions(response.data))
      .catch((error) => console.error("Error fetching subscriptions", error));
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold">All Subscriptions</h2>
      {subscriptions.length === 0 ? (
        <p>No subscriptions found.</p>
      ) : (
        <ul>
          {subscriptions.map((sub) => (
            <li key={sub.user} className="p-3 border rounded mb-2">
              <p>User: {sub.user}</p>
              <p>Plan: {sub.plan_name}</p>
              <p>Status: <span className="text-blue-500">{sub.status}</span></p>
              <p>Auto Renewal: {sub.auto_renewal ? "Yes" : "No"}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default AdminSubscriptions;