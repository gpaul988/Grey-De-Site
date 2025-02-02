import { useState } from "react";
import axios from "axios";

const AdminDashboard = () => {
  const [bookingId, setBookingId] = useState("");
  const [status, setStatus] = useState("in_progress");
  const [message, setMessage] = useState("");

  const handleStatusUpdate = async () => {
    const { data } = await axios.post("/api/services/update-status", { booking_id: bookingId, status });
    setMessage(data.message);
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Admin Service Management</h1>
      <input type="text" value={bookingId} onChange={(e) => setBookingId(e.target.value)} className="border p-2" placeholder="Enter Booking ID" />
      <select value={status} onChange={(e) => setStatus(e.target.value)} className="border p-2">
        <option value="in_progress">In Progress</option>
        <option value="completed">Completed</option>
        <option value="canceled">Canceled</option>
      </select>
      <button onClick={handleStatusUpdate} className="btn mt-4">Update Status</button>
      {message && <p className="mt-4">{message}</p>}
    </div>
  );
};

export default AdminDashboard;
