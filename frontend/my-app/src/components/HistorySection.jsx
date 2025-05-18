import React from 'react';

const HistorySection = () => {
  const historyData = [
    {
      date: 'May 18, 2025 · 11:30 AM',
      qid: 'ABC123',
      opponent: 'CodeMaster42',
      result: 'WIN'
    },
    {
      date: 'May 17, 2025 · 4:15 PM',
      qid: 'DEF456',
      opponent: 'AlgoNinja',
      result: 'LOSE'
    },
    {
      date: 'May 16, 2025 · 2:45 PM',
      qid: 'GHI789',
      opponent: 'ByteWizard',
      result: 'WIN'
    },
    {
      date: 'May 15, 2025 · 6:20 PM',
      qid: 'JKL012',
      opponent: 'QuantumCoder',
      result: 'WIN'
    },
    {
      date: 'May 14, 2025 · 10:10 AM',
      qid: 'MNO345',
      opponent: 'DevExpert',
      result: 'LOSE'
    }
  ];

  return (
    <section className="bg-white rounded-xl p-5 shadow-sm">
      <h2 className="text-xl font-semibold text-gray-800 relative pb-1.5 mb-5 after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-12 after:h-0.75 after:bg-pink-500 after:rounded">
        History
      </h2>
      
      <table className="w-full">
        <thead>
          <tr>
            <th className="text-left py-3 px-4 border-b border-gray-100 text-gray-600 font-semibold">History</th>
            <th className="text-left py-3 px-4 border-b border-gray-100 text-gray-600 font-semibold">QID</th>
            <th className="text-left py-3 px-4 border-b border-gray-100 text-gray-600 font-semibold">Opponent</th>
            <th className="text-left py-3 px-4 border-b border-gray-100 text-gray-600 font-semibold">Win/Lose</th>
          </tr>
        </thead>
        <tbody>
          {historyData.map((item, index) => (
            <tr key={index} className="hover:bg-gray-50">
              <td className="py-3 px-4 border-b border-gray-50 text-gray-600">{item.date}</td>
              <td className="py-3 px-4 border-b border-gray-50 text-gray-600">{item.qid}</td>
              <td className="py-3 px-4 border-b border-gray-50 text-gray-600">{item.opponent}</td>
              <td className="py-3 px-4 border-b border-gray-50">
                <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                  item.result === 'WIN' 
                    ? 'bg-green-100 text-green-600'
                    : 'bg-red-100 text-red-600'
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