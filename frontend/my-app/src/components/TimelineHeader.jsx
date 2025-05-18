import React from 'react';
import { Clock, ChevronDown, ChevronUp, ZoomIn, ZoomOut } from 'lucide-react';

const TimelineHeader = () => {
  return (
    <div className="flex justify-between items-center mb-3">
      <div className="flex items-center">
        <span className="text-xs bg-purple-200 text-purple-800 px-2 py-1 rounded font-medium">Timeline</span>
        <div className="ml-4 flex">
          <button className="p-1 border border-gray-300 rounded-l hover:bg-gray-100">
            <ChevronDown size={12} />
          </button>
          <button className="p-1 border-t border-b border-r border-gray-300 rounded-r hover:bg-gray-100">
            <ChevronUp size={12} />
          </button>
        </div>
        <div className="ml-2 flex">
          <button className="p-1 border border-gray-300 rounded-l hover:bg-gray-100">
            <ZoomOut size={12} />
          </button>
          <button className="p-1 border-t border-b border-r border-gray-300 rounded-r hover:bg-gray-100">
            <ZoomIn size={12} />
          </button>
        </div>
      </div>
      
      <div className="flex items-center text-xs text-gray-600">
        <Clock size={12} className="mr-1" />
        <span>Timeline view</span>
      </div>
    </div>
  );
};

export default TimelineHeader; 