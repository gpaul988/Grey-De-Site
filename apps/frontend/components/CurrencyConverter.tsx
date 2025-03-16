import React, { useState } from 'react';
import { convertCurrency }  from '@/utils/currencyConverter';

const CurrencyConverter: React.FC = () => {
  const [amount, setAmount] = useState<number>(0);
  const [fromCurrency, setFromCurrency] = useState<string>('USD');
  const [toCurrency, setToCurrency] = useState<string>('EUR');
  const [result, setResult] = useState<number | null>(null);

  const handleConvert = async () => {
    const convertedAmount = await convertCurrency(amount, fromCurrency, toCurrency);
    setResult(convertedAmount);
  };

  return (
    <div>
      <input
        type="number"
        value={amount}
        onChange={(e) => setAmount(Number(e.target.value))}
        placeholder="Amount"
      />
      <input
        type="text"
        value={fromCurrency}
        onChange={(e) => setFromCurrency(e.target.value)}
        placeholder="From Currency"
      />
      <input
        type="text"
        value={toCurrency}
        onChange={(e) => setToCurrency(e.target.value)}
        placeholder="To Currency"
      />
      <button onClick={handleConvert}>Convert</button>
      {result !== null && <p>Converted Amount: {result}</p>}
    </div>
  );
};

export default CurrencyConverter;