import { useState, useEffect } from "react";
import axios from "axios";

interface Subscription {
  plan_name: string;
  end_date: string;
  auto_renew: boolean;
}

const SubscriptionStatus = () => {
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [autoRenew, setAutoRenew] = useState(false);

  useEffect(() => {
    const fetchSubscription = async () => {
      try {
        const response = await axios.get("/api/subscriptions/status");
        setSubscription(response.data);
        setAutoRenew(response.data.auto_renew);
      } catch (error) {
        console.error("Error fetching subscription status", error);
      }
    };
    fetchSubscription();
  }, []);

  const toggleAutoRenew = async () => {
    try {
      await axios.post("/api/subscriptions/toggle-auto-renew");
      setAutoRenew(!autoRenew);
    } catch (error) {
      console.error("Error updating auto-renew status", error);
    }
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold">Subscription Status</h2>
      {subscription ? (
        <>
          <p>Plan: {subscription.plan_name}</p>
          <p>Expires: {new Date(subscription.end_date).toLocaleDateString()}</p>
          <p>Auto-Renewal: {autoRenew ? "Enabled" : "Disabled"}</p>
          <button
            onClick={toggleAutoRenew}
            className="mt-2 p-2 border rounded bg-blue-500 text-white"
          >
            {autoRenew ? "Disable Auto-Renew" : "Enable Auto-Renew"}
          </button>
        </>
      ) : (
        <p>No active subscription</p>
      )}
    </div>
  );
};

export default SubscriptionStatus;