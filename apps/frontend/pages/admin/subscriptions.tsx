import { useState, useEffect } from "react";
import axios from "axios";

interface Subscription {
  user__email: string;
  plan__name: string;
  status: string;
  end_date: string;
  user_id: string;
}

const AdminSubscriptions = () => {
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);

  useEffect(() => {
    axios.get("/api/admin/subscriptions").then(res => setSubscriptions(res.data));
  }, []);

  const cancelSubscription = async (userId: string) => {
    await axios.post("/api/admin/subscription/cancel", { user_id: userId });
    alert("Subscription cancelled.");
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Manage User Subscriptions</h1>
      <table>
        <thead>
          <tr>
            <th>User</th>
            <th>Plan</th>
            <th>Status</th>
            <th>Expires</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {subscriptions.map((sub) => (
            <tr key={sub.user__email}>
              <td>{sub.user__email}</td>
              <td>{sub.plan__name}</td>
              <td>{sub.status}</td>
              <td>{sub.end_date}</td>
              <td>
                <button onClick={() => cancelSubscription(sub.user_id)} className="btn">Cancel</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AdminSubscriptions;