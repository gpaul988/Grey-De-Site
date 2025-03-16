import { useEffect, useState } from "react";
import axios from "axios";

interface Payment {
  transaction_id: string;
  user: string;
  amount: number;
  currency: string;
  status: string;
}

const AdminPayments = () => {
  const [payments, setPayments] = useState<Payment[]>([]);

  useEffect(() => {
    axios
      .get("/api/payments/admin-payments-overview/", {
        headers: { Authorization: `Bearer ${localStorage.getItem("adminToken")}` },
      })
      .then((response) => setPayments(response.data))
      .catch((error) => console.error("Error fetching payments", error));
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold">All Payments</h2>
      {payments.length === 0 ? (
        <p>No payments found.</p>
      ) : (
        <ul>
          {payments.map((payment) => (
            <li key={payment.transaction_id} className="p-3 border rounded mb-2">
              <p>User: {payment.user}</p>
              <p>Transaction ID: {payment.transaction_id}</p>
              <p>Amount: {payment.amount} {payment.currency}</p>
              <p>Status: <span className="text-green-500">{payment.status}</span></p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default AdminPayments;