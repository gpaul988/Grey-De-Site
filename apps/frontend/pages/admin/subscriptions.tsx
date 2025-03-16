import { useEffect, useState } from "react";
import axios from "axios";

interface Subscription {
  user: string;
  plan: string;
  expires: string;
  auto_renew: boolean;
}

const AdminSubscriptions = () => {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);

  useEffect(() => {
    const fetchSubscriptions = async () => {
      const response = await axios.get("/api/admin/subscriptions");
      setSubscriptions(response.data.subscriptions);
    };
    fetchSubscriptions();
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold">Manage Subscriptions</h1>
      <table className="w-full mt-4 border">
        <thead>
          <tr>
            <th>User</th>
            <th>Plan</th>
            <th>Expires</th>
            <th>Auto-Renew</th>
          </tr>
        </thead>
        <tbody>
          {subscriptions.map((sub, index) => (
            <tr key={index} className="border">
              <td>{sub.user}</td>
              <td>{sub.plan}</td>
              <td>{new Date(sub.expires).toLocaleDateString()}</td>
              <td>{sub.auto_renew ? "Yes" : "No"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AdminSubscriptions;