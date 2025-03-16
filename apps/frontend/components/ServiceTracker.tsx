import { useEffect, useState } from "react";
import axios from "axios";

interface Service {
  service_name: string;
  status: string;
  expected_completion: string;
}

const ServiceTracker = () => {
  const [services, setServices] = useState<Service[]>([]);

  useEffect(() => {
    axios
      .get("/api/services/track-service/", {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      })
      .then((response) => setServices(response.data))
      .catch((error) => console.error("Error fetching services", error));
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold">Service Progress</h2>
      {services.length === 0 ? (
        <p>No services booked yet.</p>
      ) : (
        <ul>
          {services.map((service) => (
            <li key={service.service_name} className="p-3 border rounded mb-2">
              <p className="font-bold">{service.service_name}</p>
              <p>Status: <span className="text-blue-500">{service.status}</span></p>
              <p>Expected Completion: {new Date(service.expected_completion).toLocaleDateString()}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ServiceTracker;