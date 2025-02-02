import { useState } from "react";
import axios from "axios";

const ServiceRecommendation = () => {
  const [file, setFile] = useState<File | null>(null);
  const [recommendation, setRecommendation] = useState("");

  const handleFileUpload = async () => {
    if (!file) return alert("Please select a file!");

    const formData = new FormData();
    formData.append("file", file);

    const { data } = await axios.post("/api/llm/analyze-file", formData);
    setRecommendation(data.recommendation);
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold">Find the Best Service for You</h1>
      <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} className="p-2 border" />
      <button onClick={handleFileUpload} className="btn mt-4">Analyze</button>
      {recommendation && <p className="mt-4 bg-gray-100 p-4">{recommendation}</p>}
    </div>
  );
};

export default ServiceRecommendation;
