import React, { useState } from "react";
import axios from "axios";

interface RefundFormProps {
  transactionId: string;
}

const RefundForm: React.FC<RefundFormProps> = ({ transactionId }) => {
  const [reason, setReason] = useState("");
  const [message, setMessage] = useState("");

  const handleRefundRequest = async () => {
    try {
      const response = await axios.post(
        "/api/payments/request-refund/",
        { transaction_id: transactionId, reason },
        { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
      );
      setMessage(response.data.message);
    } catch {
      setMessage("Refund request failed.");
    }
  };

  return (
    <div>
      <h2 className="text-lg font-bold">Request a Refund</h2>
      <textarea value={reason} onChange={(e) => setReason(e.target.value)} className="border p-2 w-full" placeholder="Reason for refund" />
      <button className="bg-red-500 text-white px-4 py-2 rounded mt-3" onClick={handleRefundRequest}>
        Submit Request
      </button>
      {message && <p className="mt-2">{message}</p>}
    </div>
  );
};

export default RefundForm;