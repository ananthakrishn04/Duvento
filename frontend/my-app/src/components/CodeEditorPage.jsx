import React from 'react';
import { Clock, BellIcon, UserIcon, ChevronRight, LogOut } from 'lucide-react';
import CodeEditor from './CodeEditor';

const CodeEditorPage = () => {
  return (
    <div className="w-full min-h-screen" style={{
      background: 'linear-gradient(120deg, #00bcd4 0%, #2196f3 100%)',
      backgroundSize: 'cover',
      overflow: 'hidden'
    }}>
      {/* Background decoration - subtle waves */}
      <div className="absolute w-full h-full inset-0 z-0" 
        style={{
          backgroundImage: "url('https://c.animaapp.com/maihfzolvngpdA/img/decoration---line---wing-mask.png')",
          backgroundSize: 'cover',
          opacity: 0.3
        }}
      />

      {/* Main container */}
      <div className="relative z-10 container mx-auto py-4 px-4 flex flex-col h-screen">
        {/* Top header with app name and user profile */}
        <div className="flex justify-between items-center mb-4">
          <div className="font-['Open_Sans',Helvetica] font-bold text-white text-xl">
            <img 
              src="https://c.animaapp.com/maihfzolvngpdA/img/untitled-1.png" 
              alt="Duvento" 
              className="h-10 inline-block"
            />
          </div>
          <div className="flex items-center gap-4">
            <div className="w-8 h-8 flex items-center justify-center cursor-pointer bg-white bg-opacity-20 rounded-full">
              <BellIcon size={20} className="text-white" />
            </div>
            <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center cursor-pointer">
              <UserIcon size={18} className="text-blue-600" />
            </div>
          </div>
        </div>

        {/* Main white card content */}
        <div className="bg-white rounded-[20px] shadow-lg flex-grow flex flex-col overflow-hidden">
          {/* User info row */}
          <div className="w-full bg-white h-16 border-b border-[#00000029] px-6 py-3 flex justify-between items-center">
            <div className="flex items-center">
              <div className="mr-12">
                <div className="text-sm text-gray-500">You</div>
                <div className="font-semibold text-gray-800">Player1</div>
              </div>
              <div className="flex items-center">
                <Clock size={18} className="text-blue-600 mr-2" />
                <div className="font-semibold text-xl text-gray-800">10:00</div>
              </div>
            </div>
            <div className="flex items-center">
              <div className="flex items-center mr-12">
                <Clock size={18} className="text-red-600 mr-2" />
                <div className="font-semibold text-xl text-gray-800">05:30</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">Opponent</div>
                <div className="font-semibold text-gray-800">Player2</div>
              </div>
            </div>
          </div>

          {/* Main content with two panels */}
          <div className="flex flex-grow">
            {/* Left panel - Description */}
            <div className="w-1/2 p-6 flex flex-col">
              <div className="mb-6">
                <h3 className="font-['Open_Sans',Helvetica] font-semibold text-gray-800 mb-2">Description</h3>
                <div className="w-full h-40 bg-gray-50 border border-[#00000029] rounded p-3 text-sm text-gray-700 overflow-auto">
                  <p>Write a function that finds the longest substring without repeating characters in a given string.</p>
                  <p className="mt-2">Example:</p>
                  <p className="mt-1">Input: "abcabcbb"</p>
                  <p>Output: 3 (The answer is "abc", with the length of 3)</p>
                </div>
              </div>
              
              <div className="mb-6">
                <h3 className="font-['Open_Sans',Helvetica] font-semibold text-gray-800 mb-2">Example</h3>
                <div className="w-full h-32 bg-gray-50 border border-[#00000029] rounded p-3 font-mono text-sm text-gray-700 overflow-auto">
                  <pre>{`function lengthOfLongestSubstring(s) {
  let maxLength = 0;
  let start = 0;
  let charMap = {};
  
  for (let i = 0; i < s.length; i++) {
    if (charMap[s[i]] >= start) {
      start = charMap[s[i]] + 1;
    }
    charMap[s[i]] = i;
    maxLength = Math.max(maxLength, i - start + 1);
  }
  
  return maxLength;
}`}</pre>
                </div>
              </div>
              
              <div className="flex-grow">
                <h3 className="font-['Open_Sans',Helvetica] font-semibold text-gray-800 mb-2">Constraints</h3>
                <div className="w-full h-32 bg-gray-50 border border-[#00000029] rounded p-3 text-sm text-gray-700 overflow-auto">
                  <ul className="list-disc pl-4">
                    <li>0 &lt;= s.length &lt;= 5 * 10^4</li>
                    <li>s consists of English letters, digits, symbols and spaces</li>
                    <li>Your solution should run in O(n) time complexity</li>
                    <li>You must handle edge cases like empty strings</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Timeline separator - vertical time progress */}
            <div className="h-full w-[5px] bg-gray-100 relative">
              <div className="absolute left-0 top-0 bottom-[60%] w-full bg-blue-500"></div>
              <div className="absolute left-[-6px] top-[40%] w-4 h-4 rounded-full bg-blue-600 border-2 border-white"></div>
            </div>
            
            {/* Right panel - Code editor */}
            <div className="w-1/2 p-6 flex flex-col">
              <h3 className="font-['Open_Sans',Helvetica] font-semibold text-gray-800 mb-2">Code Editor</h3>
              <div className="flex-grow">
                <CodeEditor initialCode={`// Type your solution here

function longestSubstring(s) {
  // Your implementation
  
}`} />
              </div>
            </div>
          </div>

          {/* Bottom action bar */}
          <div className="w-full h-14 bg-white border-t border-[#00000029] px-6 flex justify-between items-center">
            <div className="flex items-center gap-4">
              <div className="font-['Open_Sans',Helvetica] text-gray-700">
                <span className="font-semibold">Hidden Case:</span> 3/5 Passed
              </div>
              <div className="font-['Open_Sans',Helvetica] text-gray-700">
                <span className="font-semibold">Game ID:</span> GC-12345
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <button className="px-4 py-2 bg-gray-200 rounded flex items-center text-gray-700 hover:bg-gray-300 transition-colors">
                <span className="font-['Open_Sans',Helvetica] font-semibold text-sm">Submit</span>
                <ChevronRight size={16} className="ml-1" />
              </button>
              <button className="px-4 py-2 bg-[#c5051d] rounded flex items-center text-white hover:bg-red-700 transition-colors">
                <LogOut size={16} className="mr-1" />
                <span className="font-['Open_Sans',Helvetica] font-semibold text-sm">Quit Game</span>
              </button>
            </div>
          </div>
        </div>

        {/* Bottom text */}
        <div className="text-center text-white text-xs mt-2">
          <p>Where Coders Clash &amp; Legends Rise</p>
        </div>
      </div>
    </div>
  );
};

export default CodeEditorPage; 