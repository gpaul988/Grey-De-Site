import { useState } from "react";
import axios from "axios";

const ServiceBooking = () => {
  const [serviceName, setServiceName] = useState("");
  const [expectedCompletion, setExpectedCompletion] = useState("");

  const handleBooking = async () => {
    try {
      const response = await axios.post("/api/services/book-service/", {
        service_name: serviceName,
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });

      setExpectedCompletion(response.data.expected_completion);
      alert("Service booked successfully.");
    } catch (error) {
      console.error("Booking error:", error);
    }
  };

  return (
    <div>
      <h2 className="text-xl font-bold">Book a Service</h2>
      <select value={serviceName} onChange={(e) => setServiceName(e.target.value)} className="p-2 border rounded">
        <option value="">Select a Service</option>
        <option value="Web Development">Web Development</option>
        <option value="Mobile App Development">Mobile App Development</option>
        <option value="Blockchain Development">Blockchain Development</option>
      </select>
      <button onClick={handleBooking} className="bg-green-500 text-white p-2 rounded mt-2">
        Book Service
      </button>
      {expectedCompletion && <p>Expected Completion Date: {expectedCompletion}</p>}
    </div>
  );
};

export default ServiceBooking;
