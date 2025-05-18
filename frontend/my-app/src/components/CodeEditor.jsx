import React, { useState } from 'react';

const CodeEditor = ({ initialCode = '// Type your code here' }) => {
  const [code, setCode] = useState(initialCode);
  const [lineCount, setLineCount] = useState(1);

  const handleCodeChange = (e) => {
    const newCode = e.target.value;
    setCode(newCode);
    
    // Update line count
    const lines = newCode.split('\n').length;
    setLineCount(lines);
  };

  // Generate line numbers
  const lineNumbers = Array.from({ length: lineCount }, (_, i) => i + 1).join('\n');

  return (
    <div className="w-full h-full rounded border border-gray-300 bg-gray-800 flex overflow-hidden font-mono text-sm">
      {/* Line numbers */}
      <div className="py-2 px-2 bg-gray-900 text-gray-500 text-right select-none min-w-[40px]">
        {lineNumbers}
      </div>
      
      {/* Actual editor */}
      <textarea
        value={code}
        onChange={handleCodeChange}
        className="flex-grow bg-gray-800 text-gray-100 p-2 resize-none focus:outline-none"
        spellCheck="false"
      />
    </div>
  );
};

export default CodeEditor; 