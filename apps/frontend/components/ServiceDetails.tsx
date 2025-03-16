import { useState, useEffect } from "react";
import axios from "axios";

interface Booking {
  service_name: string;
  status: string;
  booking_date: string;
  completion_date: string;
}

const ServiceDetails = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);

  // Fetch user bookings from API
useEffect(() => {
  const fetchBookings = async () => {
    try {
      const response = await axios.get("/api/services/user_bookings");
      setBookings(response.data.bookings);
    } catch (error) {
      if (axios.isAxiosError(error)) {
        console.error("Error fetching bookings", error.response ? error.response.data : error.message);
      } else {
        console.error("Unexpected error", error);
      }
    }
  };

  fetchBookings();
}, []);

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold">My Booked Services</h1>
      {bookings.length === 0 ? (
        <p>No bookings found.</p>
      ) : (
        <ul className="mt-4 space-y-4">
          {bookings.map((booking, index) => (
            <li key={index} className="border p-4 rounded-lg">
              <h2 className="font-semibold">{booking.service_name}</h2>
              <p>Status: {booking.status}</p>
              <p>Booking Date: {new Date(booking.booking_date).toLocaleDateString()}</p>
              {booking.completion_date && (
                <p>Completion Date: {new Date(booking.completion_date).toLocaleDateString()}</p>
              )}
              {booking.status === "completed" && (
                <p className="text-green-500 mt-2">Your service is completed!</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ServiceDetails;
