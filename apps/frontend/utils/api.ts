import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

export const updateStatus = async (bookingId: string, status: string) => {
  const response = await api.post("/services/update-status", { booking_id: bookingId, status });
  return response.data;
};

export const initializePayment = async (gateway: string, amount: number) => {
  const token = localStorage.getItem("token");
  if (!token) {
    throw new Error("Authorization token is missing");
  }

  const response = await fetch(`/api/payment/${gateway}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ amount }),
  });
  return response.json();
};

export default api;