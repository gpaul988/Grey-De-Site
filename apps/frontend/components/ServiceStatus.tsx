import { useState } from "react";
import axios from "axios";

const ServiceStatus = () => {
  const [bookingId, setBookingId] = useState("");
  const [status, setStatus] = useState("in_progress");

  const handleStatusUpdate = async () => {
    const { data } = await axios.post(`/api/services/update-status/${bookingId}`, { status });
    console.log("Service Status Updated:", data);
  };

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold">Update Service Status</h1>
      <input type="text" placeholder="Booking ID" value={bookingId} onChange={(e) => setBookingId(e.target.value)} className="border p-2 w-full mt-2" />
      <select value={status} onChange={(e) => setStatus(e.target.value)} className="border p-2 w-full mt-2">
        <option value="pending">Pending</option>
        <option value="in_progress">In Progress</option>
        <option value="completed">Completed</option>
        <option value="canceled">Canceled</option>
      </select>
      <button onClick={handleStatusUpdate} className="btn mt-4">Update Status</button>
    </div>
  );
};

export default ServiceStatus;