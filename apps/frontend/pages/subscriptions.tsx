import { useEffect, useState } from "react";

interface SubscriptionPlan {
    id: number;
    name: string;
    price: number;
}

const Subscriptions = () => {
    const [plans, setPlans] = useState<SubscriptionPlan[]>([]);

    useEffect(() => {
        fetch("/api/subscriptions")
            .then((res) => res.json())
            .then((data) => setPlans(data));
    }, []);

    return (
        <div>
            <h2>Choose a Subscription Plan</h2>
            <ul>
                {plans.map((plan) => (
                    <li key={plan.id}>
                        {plan.name} - ${plan.price}
                        <button>Subscribe</button>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Subscriptions;