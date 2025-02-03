import { useState } from "react";
import axios from "axios";

const RefundForm = () => {
  const [paymentId, setPaymentId] = useState("");
  const [reason, setReason] = useState("");

  const handleRefundRequest = async () => {
    const { data } = await axios.post("/api/payments/refund", { payment_id: paymentId, reason });
    console.log("Refund Requested:", data);
  };

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold">Request a Refund</h1>
      <input type="text" placeholder="Payment ID" value={paymentId} onChange={(e) => setPaymentId(e.target.value)} className="border p-2 w-full mt-2" />
      <textarea placeholder="Reason for refund" value={reason} onChange={(e) => setReason(e.target.value)} className="border p-2 w-full mt-2" />
      <button onClick={handleRefundRequest} className="btn mt-4">Submit Refund Request</button>
    </div>
  );
};

export default RefundForm;