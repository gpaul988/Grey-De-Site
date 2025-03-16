import axios from "axios";
import React from "react";

interface RefundButtonProps {
  serviceId: string;
}

const RefundButton: React.FC<RefundButtonProps> = ({ serviceId }) => {
  const processRefund = async () => {
    try {
      const response = await axios.post("/api/services/refund", { service_id: serviceId });
      alert(response.data.message);
    } catch {
      alert("Refund failed");
    }
  };

  return (
    <button onClick={processRefund} className="bg-red-500 text-white px-4 py-2 rounded">
      Issue Refund
    </button>
  );
};

export default RefundButton;