import React, { useState } from "react"; // Removed useEffect import
import axios from "axios";

interface PaymentProps {
  serviceId: string; // Explicitly define the type of serviceId
}

const Payment: React.FC<PaymentProps> = ({ serviceId }) => {
  const [currency, setCurrency] = useState("USD");
  const [convertedPrice, setConvertedPrice] = useState<number | null>(null);

  const handlePayment = async () => {
    try {
      const response = await axios.post("/api/payments/process-payment/", {
        service_id: serviceId,
        currency,
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });

      setConvertedPrice(response.data.converted_price);
      alert("Payment initiated successfully.");
    } catch (error) {
      console.error("Payment error:", error);
    }
  };

  return (
      <div>
        <h2 className="text-xl font-bold">Select Payment Currency</h2>
        <select value={currency} onChange={(e) => setCurrency(e.target.value)} className="p-2 border rounded">
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
        <button onClick={handlePayment} className="bg-blue-500 text-white p-2 rounded mt-2">
        Proceed with Payment
        </button>
        {convertedPrice && <p>Amount to be paid: {convertedPrice} {currency}</p>}
      </div>
  );
};

export default Payment;