import { useState, useEffect } from "react";
import axios from "axios";

interface Service {
  id: string;
  name: string;
}

interface Currency {
  code: string;
  name: string;
  symbol: string;
}

const BookingForm = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [currencies, setCurrencies] = useState<Currency[]>([]);
  const [selectedService, setSelectedService] = useState("");
  const [selectedCurrency, setSelectedCurrency] = useState("USD");
  const [autoRenewal, setAutoRenewal] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    axios.get("/api/services/").then((res) => setServices(res.data.services));
    axios.get("/api/currencies/").then((res) => setCurrencies(res.data.currencies));
  }, []);

  const handleBooking = async () => {
  try {
    const response = await axios.post(
      "/api/bookings/book/",
      { service_id: selectedService, currency_code: selectedCurrency, auto_renewal: autoRenewal },
      { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
    );
    setMessage(response.data.message);
  } catch (error) {
    console.error(error); // Log the error message
    setMessage("Booking failed. Try again.");
  }
};

  return (
    <div>
      <h2 className="text-lg font-bold">Book a Service</h2>
      <select value={selectedService} onChange={(e) => setSelectedService(e.target.value)} className="border p-2">
        {services.map((service) => (
          <option key={service.id} value={service.id}>
            {service.name}
          </option>
        ))}
      </select>

      <select value={selectedCurrency} onChange={(e) => setSelectedCurrency(e.target.value)} className="border p-2">
        {currencies.map((currency) => (
          <option key={currency.code} value={currency.code}>
            {currency.name} ({currency.symbol})
          </option>
        ))}
      </select>

      <label className="block mt-2">
        <input type="checkbox" checked={autoRenewal} onChange={() => setAutoRenewal(!autoRenewal)} />
        Enable Auto-Renewal
      </label>

      <button className="bg-green-500 text-white px-4 py-2 rounded mt-3" onClick={handleBooking}>
        Book Now
      </button>

      {message && <p className="mt-2">{message}</p>}
    </div>
  );
};

export default BookingForm;