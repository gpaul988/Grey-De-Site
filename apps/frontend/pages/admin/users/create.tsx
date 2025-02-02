import { useState } from "react";
import axios from "axios";
import { useRouter } from "next/router";

const CreateUser = () => {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("user");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post("/api/users", { username, email, role });
      router.push("/admin/users");
    } catch (error) {
      console.error("Error creating user:", error);
    }
  };

  return (
    <div className={'bg-gray-50/50 lg:max-w-7xl w-full mx-auto'}>
      <h2 className="text-[3em] font-bold">Create User</h2>
      <form onSubmit={handleSubmit} className="mt-4">
        <div>
          <label>Username</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-2 mt-2 border rounded"
            required
          />
        </div>
        <div className="mt-4">
          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2 mt-2 border rounded"
            required
          />
        </div>
        <div className="mt-4">
          <label>Role</label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-full px-4 py-2 mt-2 border rounded"
          >
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
        </div>
        <button type="submit" className="btn btn-primary mt-4">
          Create User
        </button>
      </form>
    </div>
  );
};

export default CreateUser;