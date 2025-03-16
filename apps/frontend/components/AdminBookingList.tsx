import { useEffect, useState } from "react";
import axios from "axios";

interface Booking {
  id: number;
  user: {
    username: string;
  };
  service: {
    name: string;
  };
  status: string;
}

const AdminBookingList = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);

  useEffect(() => {
    axios.get("/api/admin/bookings/", { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } })
      .then((res) => setBookings(res.data.bookings));
  }, []);

  const updateStatus = async (bookingId: number, status: string) => {
    await axios.patch(
      `/api/bookings/update/${bookingId}/`,
      { status },
      { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
    );
    setBookings((prev) =>
      prev.map((b) => (b.id === bookingId ? { ...b, status } : b))
    );
  };

  return (
    <div>
      <h2 className="text-lg font-bold">Manage Bookings</h2>
      {bookings.map((booking) => (
        <div key={booking.id} className="border p-2 my-2">
          <p>{booking.user.username} booked {booking.service.name}</p>
          <p>Status: {booking.status}</p>
          <button onClick={() => updateStatus(booking.id, "approved")} className="bg-blue-500 text-white px-3 py-1">
            Approve
          </button>
        </div>
      ))}
    </div>
  );
};

export default AdminBookingList;