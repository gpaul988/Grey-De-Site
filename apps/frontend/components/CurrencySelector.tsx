import React, { useEffect, useState } from "react";
import axios from "axios";

interface Currency {
  code: string;
  name: string;
  symbol: string;
}

interface CurrencySelectorProps {
  setSelectedCurrency: React.Dispatch<React.SetStateAction<string>>;
}

const CurrencySelector: React.FC<CurrencySelectorProps> = ({ setSelectedCurrency }) => {  const [currencies, setCurrencies] = useState<Currency[]>([]);
    const handleCurrencyChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCurrency(event.target.value);
  };
  useEffect(() => {
    axios.get<{ currencies: Currency[] }>("/api/currencies/").then((response) => {
      setCurrencies(response.data.currencies);
    });
  }, []);

  return (
    <div>
      <label className="text-sm font-bold">Select Currency:</label>
      <select
        onChange={handleCurrencyChange}
        className="border rounded p-2"
      >
        {currencies.map((currency) => (
          <option key={currency.code} value={currency.code}>
            {currency.name} ({currency.symbol})
          </option>
        ))}
      </select>
    </div>
  );
};

export default CurrencySelector;