import { useState } from "react";
import axios from "axios";

const PaymentForm = () => {
  const [amount, setAmount] = useState("");
  const [currency, setCurrency] = useState("USD");
  const [gateway, setGateway] = useState("paystack");

  const handlePayment = async () => {
    const { data } = await axios.post("/api/payments/create", { amount, currency, gateway });
    console.log("Payment Created:", data);
  };

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold">Make a Payment</h1>
      <input
        type="number"
        placeholder="Enter amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        className="border p-2 w-full mt-2"
      />
      <select value={currency} onChange={(e) => setCurrency(e.target.value)} className="border p-2 w-full mt-2">
        <option value="USD">USD</option>
        <option value="NGN">NGN</option>
        <option value="EUR">EUR</option>
      </select>
      <select value={gateway} onChange={(e) => setGateway(e.target.value)} className="border p-2 w-full mt-2">
        <option value="paystack">Paystack</option>
        <option value="flutterwave">Flutterwave</option>
        <option value="interswitch">Interswitch</option>
        <option value="payu">PayU</option>
        <option value="vogupay">VoguPay</option>
      </select>
      <button onClick={handlePayment} className="btn mt-4">Proceed to Pay</button>
    </div>
  );
};

export default PaymentForm;