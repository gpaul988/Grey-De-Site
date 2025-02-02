import { useState } from "react";
import axios from "axios";

const FileUpload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const [recommendedService, setRecommendedService] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files ? e.target.files[0] : null);
  };

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://localhost:8000/api/upload-file/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      setRecommendedService(response.data.recommended_service);
      setError(""); // Clear any previous errors
    } catch (error) {
      setError("Failed to upload file. Please try again.");
    }
  };

  return (
    <div className="p-6 max-w-lg mx-auto">
      <form onSubmit={handleFileUpload} className="space-y-4">
        <input
          type="file"
          onChange={handleFileChange}
          className="border p-2 w-full"
        />
        <button type="submit" className="bg-blue-500 text-white py-2 px-4 w-full">
          Upload File
        </button>
      </form>

      {error && <p className="text-red-500">{error}</p>}
      {recommendedService && <p className="text-green-500 mt-4">Recommended Service: {recommendedService}</p>}
    </div>
  );
};

export default FileUpload;