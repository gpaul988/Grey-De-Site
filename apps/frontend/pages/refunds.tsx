import { useState } from "react";
import axios from "axios";

const RefundPage = () => {
  const [reference, setReference] = useState("");
  const [reason, setReason] = useState("");
  const [message, setMessage] = useState("");

  const handleRefundRequest = async () => {
    try {
      const { data } = await axios.post("/api/payments/request-refund", { reference, reason });
      setMessage(data.message);
    } catch (error) {
      setMessage("Refund request failed!");
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Request a Refund</h1>
      <input type="text" value={reference} onChange={(e) => setReference(e.target.value)} className="border p-2" placeholder="Enter payment reference" />
      <textarea value={reason} onChange={(e) => setReason(e.target.value)} className="border p-2 mt-2" placeholder="Reason for refund" />
      <button onClick={handleRefundRequest} className="btn mt-4">Submit Refund Request</button>
      {message && <p className="mt-4">{message}</p>}
    </div>
  );
};

export default RefundPage;