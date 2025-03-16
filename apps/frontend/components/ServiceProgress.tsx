import { useState, useEffect } from "react";
import axios from "axios";

interface ServiceProgressProps {
  serviceId: string;
}

const ServiceProgress: React.FC<ServiceProgressProps> = ({ serviceId }) => {
  const [progress, setProgress] = useState<number>(0);

  useEffect(() => {
    const fetchService = async () => {
      const response = await axios.get(`/api/services/${serviceId}`);
      setProgress(response.data.progress);
    };
    fetchService();
  }, [serviceId]);

  const updateProgress = async (newProgress: number) => {
    try {
      await axios.post("/api/services/update-progress", { service_id: serviceId, progress: newProgress });
      setProgress(newProgress);
    } catch {
      console.error("Error updating progress");
    }
  };

  return (
    <div className="p-4 border rounded">
      <h2 className="text-lg font-bold">Service Progress</h2>
      <p>Current Progress: {progress}%</p>
      <input
        type="range"
        min="0"
        max="100"
        value={progress}
        onChange={(e) => updateProgress(Number(e.target.value))}
        className="w-full mt-2"
      />
    </div>
  );
};

export default ServiceProgress;