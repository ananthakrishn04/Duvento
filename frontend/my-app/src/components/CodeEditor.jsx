import React, { useState } from 'react';
import CodeMirror from '@uiw/react-codemirror';
import { javascript } from '@codemirror/lang-javascript';
import { java } from '@codemirror/lang-java';
import { cpp } from '@codemirror/lang-cpp';
import { python } from '@codemirror/lang-python';

const CodeEditor = ({ initialCode = '// Type your code here' }) => {
  const [code, setCode] = useState(initialCode);
  const [language, setLanguage] = useState('javascript');
  
  // Define language extensions mapping
  const languageExtensions = {
    javascript: javascript(),
    python: python(),
    java: java(),
    cpp: cpp()
  };
  
  // Define starter templates for each language
  const languageTemplates = {
    javascript: '// JavaScript code here\n\nfunction solution() {\n  // Your code here\n}\n',
    python: '# Python code here\n\ndef solution():\n    # Your code here\n    pass\n',
    java: 'public class Main {\n    public static void main(String[] args) {\n        // Your code here\n    }\n}\n',
    cpp: '#include <iostream>\n\nint main() {\n    // Your code here\n    return 0;\n}\n'
  };
  
  const handleLanguageChange = (e) => {
    const newLanguage = e.target.value;
    setLanguage(newLanguage);
    setCode(languageTemplates[newLanguage]);
  };

  const onChange = (value) => {
    setCode(value);
  };

  return (
    <div className="w-full h-full flex flex-col">
      {/* Language selector */}
      <div className="mb-2 flex justify-end">
        <select
          value={language}
          onChange={handleLanguageChange}
          className="px-3 py-1 border border-gray-300 rounded bg-white text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="javascript">JavaScript</option>
          <option value="python">Python</option>
          <option value="java">Java</option>
          <option value="cpp">C++</option>
        </select>
      </div>
      
      {/* CodeMirror editor */}
      <div className="flex-grow border border-gray-300 rounded overflow-hidden">
        <CodeMirror
          value={code}
          height="100%"
          extensions={[languageExtensions[language]]}
          onChange={onChange}
          theme="dark"
          className="h-full"
        />
      </div>
    </div>
  );
};

export default CodeEditor; 