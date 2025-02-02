import { useState } from "react";
import { initializePayment } from "@/utils/api";

const PaymentButton = () => {
    const [gateway, setGateway] = useState("paystack");
    const [amount, setAmount] = useState(1000);

    const handlePayment = async () => {
        const response = await initializePayment(gateway, amount);
        if (response.status === "success") {
            window.location.href = response.data.authorization_url;
        }
    };

    return (
        <div>
            <select onChange={(e) => setGateway(e.target.value)}>
                <option value="paystack">Paystack</option>
                <option value="flutterwave">Flutterwave</option>
            </select>
            <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(Number(e.target.value))}
            />
            <button onClick={handlePayment}>Pay Now</button>
        </div>
    );
};

export default PaymentButton;