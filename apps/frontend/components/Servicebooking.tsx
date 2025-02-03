import { useState } from "react";
import axios from "axios";

const ServiceBooking = () => {
  const [serviceId, setServiceId] = useState("");
  const [amount, setAmount] = useState("");
  const [currency, setCurrency] = useState("USD");
  const [gateway, setGateway] = useState("paystack");
  const [scheduledDate, setScheduledDate] = useState("");

  const handleBooking = async () => {
    const { data } = await axios.post("/api/services/book", { service_id: serviceId, amount, currency, gateway, scheduled_date: scheduledDate });
    console.log("Booking Created:", data);
  };

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold">Book a Service</h1>
      <input type="text" placeholder="Service ID" value={serviceId} onChange={(e) => setServiceId(e.target.value)} className="border p-2 w-full mt-2" />
      <input type="number" placeholder="Enter amount" value={amount} onChange={(e) => setAmount(e.target.value)} className="border p-2 w-full mt-2" />
      <input type="datetime-local" value={scheduledDate} onChange={(e) => setScheduledDate(e.target.value)} className="border p-2 w-full mt-2" />
      <select value={currency} onChange={(e) => setCurrency(e.target.value)} className="border p-2 w-full mt-2">
        <option value="USD">USD</option>
        <option value="NGN">NGN</option>
      </select>
      <select value={gateway} onChange={(e) => setGateway(e.target.value)} className="border p-2 w-full mt-2">
        <option value="paystack">Paystack</option>
        <option value="flutterwave">Flutterwave</option>
      </select>
      <button onClick={handleBooking} className="btn mt-4">Book Service</button>
    </div>
  );
};

export default ServiceBooking;