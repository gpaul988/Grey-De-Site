import { useState } from "react";
import axios from "axios";

const BookService = () => {
  const [service, setService] = useState("Web Development");
  const [price, setPrice] = useState("500");
  const [currency, setCurrency] = useState("USD");

  const handleBooking = async () => {
    const { data } = await axios.post("/api/services/book", { service, price, currency });
    alert(`Service booked! Booking ID: ${data.booking_id}`);
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Book a Service</h1>
        <input type="text" value={service} onChange={(e) => setService(e.target.value)} className="border p-2" />
        <input type="number" value={price} onChange={(e) => setPrice(e.target.value)} className="border p-2" />
        <input type="text" value={currency} onChange={(e) => setCurrency(e.target.value)} className="border p-2" />
        <button onClick={handleBooking} className="btn mt-4">Book Now</button>
    </div>
  );
};

export default BookService;