import React, { useEffect, useState } from "react";
import axios from "axios";
import CurrencySelector from "./CurrencySelector"; // Import the CurrencySelector component

interface CheckoutProps {
  basePriceUSD: number;
}

interface Currency {
  code: string;
  exchange_rate: number;
}

const Checkout: React.FC<CheckoutProps> = ({ basePriceUSD }) => {
  const [currencies, setCurrencies] = useState<Currency[]>([]);
  const [selectedCurrency, setSelectedCurrency] = useState("USD");
  const [exchangeRate, setExchangeRate] = useState(1);

  useEffect(() => {
    axios.get("/api/currencies/").then((response) => {
      setCurrencies(response.data.currencies);
    });
  }, []);

  useEffect(() => {
    const currency = currencies.find((c) => c.code === selectedCurrency);
    if (currency) {
      setExchangeRate(currency.exchange_rate);
    }
  }, [selectedCurrency, currencies]);

  return (
    <div>
      <h2 className="text-lg font-bold">Checkout</h2>
      <CurrencySelector setSelectedCurrency={setSelectedCurrency} />
      <p className="mt-2 text-xl">
        Total: {(basePriceUSD * exchangeRate).toFixed(2)} {selectedCurrency}
      </p>
      <button className="bg-green-500 text-white px-4 py-2 rounded">Proceed to Payment</button>
    </div>
  );
};

export default Checkout;