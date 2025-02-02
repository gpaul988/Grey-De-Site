import { useState } from "react";
import axios from "axios";
import { useRouter } from "next/router";

const CreateCompany = () => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post("/api/companies", { name, description });
      router.push("/admin/companies");
    } catch (error) {
      console.error("Error creating company:", error);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold">Create New Company</h2>
      <form onSubmit={handleSubmit} className="mt-4">
        <div>
          <label htmlFor="name">Company Name</label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full px-4 py-2 mt-2 border rounded"
            required
          />
        </div>
        <div className="mt-4">
          <label htmlFor="description">Description</label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-4 py-2 mt-2 border rounded"
            required
          />
        </div>
        <button type="submit" className="btn btn-primary mt-4">
          Create Company
        </button>
      </form>
    </div>
  );
};

export default CreateCompany;