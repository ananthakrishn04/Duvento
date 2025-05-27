import React, { useState, useEffect } from 'react';

const HistorySection = () => {
  const [historyData, setHistoryData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchGameHistory = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/profiles/game_history/', {
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch game history');
        }

        const data = await response.json();
        setHistoryData(data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching game history:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchGameHistory();
  }, []);

  // Loading state
  if (loading) {
    return (
      <section className="bg-white rounded-xl p-5 shadow-sm">
        <h2 className="text-xl font-semibold text-gray-800 relative pb-1.5 mb-5 after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-12 after:h-0.75 after:bg-pink-500 after:rounded">
          History
        </h2>
        <div className="py-8 text-center text-gray-600">
          <div className="animate-pulse flex justify-center mb-3">
            <div className="h-10 w-10 rounded-full bg-blue-200"></div>
          </div>
          <p>Loading game history...</p>
        </div>
      </section>
    );
  }

  // Error state
  if (error) {
    return (
      <section className="bg-white rounded-xl p-5 shadow-sm">
        <h2 className="text-xl font-semibold text-gray-800 relative pb-1.5 mb-5 after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-12 after:h-0.75 after:bg-pink-500 after:rounded">
          History
        </h2>
        <div className="py-6 text-center text-red-600">
          <p className="mb-2">Failed to load game history.</p>
          <p className="text-sm text-gray-600">{error}</p>
        </div>
      </section>
    );
  }

  // No history state
  if (historyData.length === 0) {
    return (
      <section className="bg-white rounded-xl p-5 shadow-sm">
        <h2 className="text-xl font-semibold text-gray-800 relative pb-1.5 mb-5 after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-12 after:h-0.75 after:bg-pink-500 after:rounded">
          History
        </h2>
        <div className="py-8 text-center text-gray-600">
          <p>You haven't played any games yet.</p>
          <p className="mt-2 text-sm">Join or create a game to get started!</p>
        </div>
      </section>
    );
  }

  return (
    <section className="bg-white rounded-xl p-5 shadow-sm">
      <h2 className="text-xl font-semibold text-gray-800 relative pb-1.5 mb-5 after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-12 after:h-0.75 after:bg-pink-500 after:rounded">
        History
      </h2>
      
      <table className="w-full">
        <thead>
          <tr>
            <th className="text-left py-3 px-4 border-b border-gray-100 text-gray-600 font-semibold">Date</th>
            <th className="text-left py-3 px-4 border-b border-gray-100 text-gray-600 font-semibold">Problem</th>
            <th className="text-left py-3 px-4 border-b border-gray-100 text-gray-600 font-semibold">Opponent</th>
            <th className="text-left py-3 px-4 border-b border-gray-100 text-gray-600 font-semibold">Result</th>
          </tr>
        </thead>
        <tbody>
          {historyData.map((item, index) => (
            <tr key={index} className="hover:bg-gray-50">
              <td className="py-3 px-4 border-b border-gray-50 text-gray-600">{item.date}</td>
              <td className="py-3 px-4 border-b border-gray-50 text-gray-600">
                {item.problem ? item.problem.title : 'Unknown Problem'}
              </td>
              <td className="py-3 px-4 border-b border-gray-50 text-gray-600">
                {item.opponent ? item.opponent.display_name : 'Multiple Players'}
              </td>
              <td className="py-3 px-4 border-b border-gray-50">
                <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                  item.result === 'WIN' 
                    ? 'bg-green-100 text-green-600'
                    : item.result === 'LOSE'
                    ? 'bg-red-100 text-red-600'
                    : 'bg-yellow-100 text-yellow-600'
                }`}>
                  {item.result}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
};

export default HistorySection; 