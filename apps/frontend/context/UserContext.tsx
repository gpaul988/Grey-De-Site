import { createContext, useContext, useEffect, useState } from "react";
import axios from "axios";

interface User {
  id: number;
  username: string;
  role: string;
  company: number | null;
}

interface UserContextType {
  user: User | null;
  loading: boolean;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get("/api/auth/me")
      .then(response => setUser(response.data))
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  return (
    <UserContext.Provider value={{ user, loading }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) throw new Error("useUser must be used within UserProvider");
  return context;
};