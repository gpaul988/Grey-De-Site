import { useState, useEffect } from "react";
import axios from "axios";
import Link from "next/link";

interface Company {
  id: number;
  name: string;
}

const CompanyList = () => {
  const [companies, setCompanies] = useState<Company[]>([]);

  useEffect(() => {
    axios
      .get("/api/companies")
      .then((response) => setCompanies(response.data))
      .catch((error) => console.error("Error fetching companies:", error));
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold">Companies</h2>
      <div className="mt-4">
        <Link href={"/admin/companies/create"} className="btn btn-primary">
          Create New Company
        </Link>
      </div>
      <ul className="mt-4">
        {companies.map((company) => (
          <li key={company.id} className="flex justify-between py-2">
            <span>{company.name}</span>
            <span>
              <Link href={`/admin/companies/${company.id}`} className="text-blue-600">Edit</Link>
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default CompanyList;