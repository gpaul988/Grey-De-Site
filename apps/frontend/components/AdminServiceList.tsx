import { useState, useEffect } from "react";
import axios from "axios";

interface Booking {
  id: number;
  user: string;
  service_name: string;
  status: string;
  booking_date: string;
}

const AdminServiceList = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

useEffect(() => {
  const fetchBookings = async () => {
    try {
      const response = await axios.get("/api/admin/bookings");
      setBookings(response.data.bookings);
    } catch {
      setError("Error fetching bookings.");
    } finally {
      setLoading(false);
    }
  };

  fetchBookings();
}, []);

  const updateStatus = async (bookingId: number, newStatus: string) => {
    try {
      await axios.patch(`/api/admin/bookings/${bookingId}`, { status: newStatus });
      setBookings((prev) =>
        prev.map((booking) =>
          booking.id === bookingId ? { ...booking, status: newStatus } : booking
        )
      );
    } catch (error) {
      console.error("Failed to update status", error);
    }
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p className="text-red-500">{error}</p>;

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold">Manage Service Bookings</h1>
      {bookings.length === 0 ? (
        <p>No service bookings available.</p>
      ) : (
        <ul className="mt-4 space-y-4">
          {bookings.map((booking) => (
            <li key={booking.id} className="border p-4 rounded-lg">
              <h2 className="font-semibold">{booking.service_name}</h2>
              <p>User: {booking.user}</p>
              <p>Status: {booking.status}</p>
              <p>Booking Date: {new Date(booking.booking_date).toLocaleDateString()}</p>
              <select
                className="mt-2 border p-2 rounded"
                value={booking.status}
                onChange={(e) => updateStatus(booking.id, e.target.value)}
              >
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default AdminServiceList;