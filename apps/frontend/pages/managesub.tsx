import { useState, useEffect } from "react";
import axios from "axios";

interface Plan {
  id: string;
  name: string;
  price: number;
}

interface UserSubscription {
  plan: {
    name: string;
  };
  end_date: string;
}

const SubscriptionPage = () => {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null);
  const [userSubscription, setUserSubscription] = useState<UserSubscription | null>(null);

  const fetchPlans = async () => {
    try {
      const res = await axios.get("/api/subscription/plans");
      if (Array.isArray(res.data)) {
        setPlans(res.data);
      } else {
        console.error("Unexpected response format for plans:", res.data);
      }
    } catch (err) {
      handleAxiosError(err, "Error fetching plans");
    }
  };

  const fetchUserSubscription = async () => {
    try {
      const res = await axios.get("/api/subscription/user");
      if (res.data && typeof res.data === 'object') {
        setUserSubscription(res.data);
      } else {
        console.error("Unexpected response format for user subscription:", res.data);
      }
    } catch (err) {
      handleAxiosError(err, "Error fetching user subscription");
    }
  };

  useEffect(() => {
    fetchPlans();
    fetchUserSubscription();
  }, []);

  const handleUpgrade = async () => {
    if (selectedPlan) {
      try {
        const response = await axios.post("/api/subscription/upgrade", {
          new_plan_id: selectedPlan.id
        });
        alert(response.data.message);
      } catch (err) {
        handleAxiosError(err, "Error upgrading subscription");
      }
    }
  };

  const handleDowngrade = async () => {
    if (selectedPlan) {
      try {
        const response = await axios.post("/api/subscription/downgrade", {
          new_plan_id: selectedPlan.id
        });
        alert(response.data.message);
      } catch (err) {
        handleAxiosError(err, "Error downgrading subscription");
      }
    }
  };

  const handleAxiosError = (err: unknown, context: string) => {
    console.error(context, err);
    if (axios.isAxiosError(err)) {
      console.error("Response data:", err.response?.data);
      console.error("Response status:", err.response?.status);
      console.error("Response headers:", err.response?.headers);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Manage Subscription</h1>
      <div>
        <p>Current Plan: {userSubscription?.plan.name}</p>
        <p>Expires on: {userSubscription?.end_date}</p>
      </div>
      <select onChange={(e) => {
        const selected = plans.find(p => p.id === e.target.value) || null;
        setSelectedPlan(selected);
      }}>
        {plans.map(plan => (
          <option key={plan.id} value={plan.id}>{plan.name} - ${plan.price}</option>
        ))}
      </select>
      <button onClick={handleUpgrade} className="btn">Upgrade</button>
      <button onClick={handleDowngrade} className="btn">Downgrade</button>
    </div>
  );
};

export default SubscriptionPage;