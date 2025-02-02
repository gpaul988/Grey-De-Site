import { useState, useEffect } from "react";
import axios from "axios";
import Link from "next/link";

const UserList = () => {
  const [users, setUsers] = useState<any[]>([]);

  useEffect(() => {
    axios
      .get("/api/users")
      .then((response) => setUsers(response.data))
      .catch((error) => console.error("Error fetching users:", error));
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold">Users</h2>
        <div className="mt-4">
            <Link href={"/admin/users/create"} className="btn btn-primary">
                Create New User
            </Link>
        </div>
      <ul className="mt-4">
        {users.map((user) => (
          <li key={user.id} className="flex justify-between py-2">
            <span>{user.username}</span>
            <span>
              <Link href={`/admin/users/${user.id}`} className="text-blue-600">Edit</Link>
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default UserList;