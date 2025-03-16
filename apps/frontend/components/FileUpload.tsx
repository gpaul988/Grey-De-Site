import { useState } from "react";
import axios from "axios";

const FileUpload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [analysisResult, setAnalysisResult] = useState("");

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFile(event.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return alert("Please select a file");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("/api/upload-file", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setAnalysisResult(response.data.analysis);
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Error uploading file");
    }
  };

  return (
    <div className="p-4 border rounded">
      <h2 className="text-lg font-bold">Upload a File for Analysis</h2>
      <input type="file" onChange={handleFileChange} className="mt-2" />
      <button onClick={handleUpload} className="bg-blue-500 text-white px-4 py-2 rounded mt-2">
        Upload & Analyze
      </button>
      {analysisResult && (
        <div className="mt-4 p-2 border rounded bg-gray-100">
          <h3 className="font-bold">LLM Analysis Result:</h3>
          <p>{analysisResult}</p>
        </div>
      )}
    </div>
  );
};

export default FileUpload;