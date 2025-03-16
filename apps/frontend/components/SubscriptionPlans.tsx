import { useState, useEffect } from "react";
import axios from "axios";

interface Plan {
  id: number;
  name: string;
  price: string;
  duration_days: number;
  features: string;
}

const SubscriptionPlans = () => {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [selectedPlan, setSelectedPlan] = useState<number | null>(null);

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        const response = await axios.get("/api/subscriptions/plans");
        setPlans(response.data.plans);
      } catch (error) {
        console.error("Failed to fetch subscription plans:", error);
      }
    };
    fetchPlans();
  }, []);

  const purchaseSubscription = async () => {
    if (!selectedPlan) return;
    try {
      await axios.post("/api/subscriptions/purchase", { plan_id: selectedPlan });
      alert("Subscription activated successfully");
    } catch (error) {
      console.error("Failed to purchase subscription:", error);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold">Choose a Subscription Plan</h1>
      <div className="grid grid-cols-3 gap-4 mt-4">
        {plans.map((plan) => (
          <div key={plan.id} className="border p-4 rounded-lg">
            <h2 className="font-semibold">{plan.name}</h2>
            <p>${plan.price} for {plan.duration_days} days</p>
            <p>{plan.features}</p>
            <button
              onClick={() => setSelectedPlan(plan.id)}
              className={`mt-2 p-2 border rounded ${
                selectedPlan === plan.id ? "bg-blue-500 text-white" : ""
              }`}
            >
              Select Plan
            </button>
          </div>
        ))}
      </div>
      {selectedPlan && (
        <button
          onClick={purchaseSubscription}
          className="mt-4 p-2 bg-green-500 text-white rounded"
        >
          Confirm Purchase
        </button>
      )}
    </div>
  );
};

export default SubscriptionPlans;
