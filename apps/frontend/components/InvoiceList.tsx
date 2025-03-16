import { useEffect, useState } from "react";
import axios from "axios";

interface Invoice {
  invoice_number: string;
  total_amount: number;
  issued_at: string;
  due_date: string;
}

const InvoiceList = () => {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInvoices = async () => {
      try {
        const { data } = await axios.get("/api/payments/invoices");
        setInvoices(data.invoices);
        setError(null); // Clear any previous errors
      } catch (error) {
        setError("Error fetching invoices. Please try again later.");
        console.error("Error fetching invoices:", error);
      }
    };
    fetchInvoices().catch((error) => console.error("Error in useEffect:", error));
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold">Your Invoices</h1>
      {error && <p className="text-red-500">{error}</p>}
      {invoices.map((invoice) => (
        <div key={invoice.invoice_number} className="border p-4 mt-2">
          <p>Invoice No: {invoice.invoice_number}</p>
          <p>Amount: ${invoice.total_amount}</p>
          <p>Issued At: {new Date(invoice.issued_at).toLocaleDateString()}</p>
          <p>Due Date: {new Date(invoice.due_date).toLocaleDateString()}</p>
        </div>
      ))}
    </div>
  );
};

export default InvoiceList;