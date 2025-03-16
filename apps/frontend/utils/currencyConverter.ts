import axios from 'axios';

const API_KEY = 'your-fixer.io-api-key';  // Replace with your API key

export const convertCurrency = async (amount: number, fromCurrency: string, toCurrency: string): Promise<number> => {
  const { data } = await axios.get(`https://data.fixer.io/api/convert`, {
    params: {
      access_key: API_KEY,
      from: fromCurrency,
      to: toCurrency,
      amount,
    }
  });
  return data.result;
};