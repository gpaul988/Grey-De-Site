import React, { useState } from "react";
import axios from "axios";

interface PaymentFormProps {
  bookingId: string; // or the appropriate type
}

const PaymentForm: React.FC<PaymentFormProps> = ({ bookingId }) => {
  const [provider, setProvider] = useState("paystack");
  const [message, setMessage] = useState("");

  const handlePayment = async () => {
    try {
      const response = await axios.post(
        "/api/payments/initiate/",
        { booking_id: bookingId, provider },
        { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
      );
      window.location.href = response.data.payment_url; // Redirect to payment gateway
    } catch (error) {
      console.error(error); // Log the error or remove this line if not needed
      setMessage("Payment initiation failed.");
    }
  };

  return (
    <div>
      <h2 className="text-lg font-bold">Make Payment</h2>
      <select value={provider} onChange={(e) => setProvider(e.target.value)} className="border p-2">
        <option value="paystack">Paystack</option>
        <option value="flutterwave">Flutterwave</option>
      </select>

      <button className="bg-green-500 text-white px-4 py-2 rounded mt-3" onClick={handlePayment}>
        Pay Now
      </button>

      {message && <p className="mt-2">{message}</p>}
    </div>
  );
};

export default PaymentForm;