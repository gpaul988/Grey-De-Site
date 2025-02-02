import { useState } from "react";
import axios from "axios";

const PaymentPage = () => {
  const [amount, setAmount] = useState("");
  const [currency, setCurrency] = useState("USD");
  const [gateway, setGateway] = useState("paystack");
  const [paymentUrl, setPaymentUrl] = useState("");

  const handlePayment = async () => {
    try {
      const { data } = await axios.post("/api/payments/initiate", {
        amount,
        currency,
        gateway,
      });

      setPaymentUrl(data.payment_url);
    } catch (error) {
        console.error("Payment initiation failed:", error);
      alert("Payment initiation failed!");
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Make a Payment</h1>
      <input type="number" value={amount} onChange={(e) => setAmount(e.target.value)} className="border p-2" placeholder="Enter amount" />
      <select value={currency} onChange={(e) => setCurrency(e.target.value)} className="border p-2">
          <option value="USD">USD</option>
          <option value="NGN">NGN</option>
          <option value="GHS">GHS</option>
          <option value="ZAR">ZAR</option>
          <option value="EUR">EUR</option>
          <option value="GBP">GBP</option>
          <option value="INR">INR</option>
          <option value="JPY">JPY</option>
          <option value="CAD">CAD</option>
      </select>
      <select value={gateway} onChange={(e) => setGateway(e.target.value)} className="border p-2">
        <option value="paystack">Paystack</option>
        <option value="flutterwave">Flutterwave</option>
      </select>
      <button onClick={handlePayment} className="btn mt-4">Proceed to Payment</button>

      {paymentUrl && (
        <div className="mt-4">
          <a href={paymentUrl} target="_blank" className="text-blue-500 underline">Complete Payment</a>
        </div>
      )}
    </div>
  );
};

export default PaymentPage;
