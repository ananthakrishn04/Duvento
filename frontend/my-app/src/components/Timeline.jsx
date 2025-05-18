import React from 'react';
import { Clock } from 'lucide-react';

const Timeline = () => {
  // Sample timeline data
  const timelineEvents = [
    { id: 1, time: '10:00', event: 'Started coding', color: 'bg-blue-200' },
    { id: 2, time: '10:15', event: 'Added functionality', color: 'bg-green-200' },
    { id: 3, time: '10:30', event: 'Fixed bug', color: 'bg-yellow-200' },
    { id: 4, time: '10:45', event: 'Code review', color: 'bg-purple-200' },
  ];

  return (
    <div className="h-full flex flex-col">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-700">Progress Timeline</h3>
        <div className="flex items-center text-xs text-gray-500">
          <Clock size={14} className="mr-1" />
          <span>Time progress</span>
        </div>
      </div>
      
      <div className="flex-grow overflow-auto">
        {/* Vertical timeline */}
        <div className="relative">
          {/* Vertical line */}
          <div className="absolute left-[15px] top-0 bottom-0 w-[2px] bg-gray-300"></div>
          
          {/* Timeline events */}
          {timelineEvents.map((event) => (
            <div key={event.id} className="mb-4 pl-8 relative">
              {/* Circle marker */}
              <div className={`absolute left-[9px] top-[6px] w-[14px] h-[14px] rounded-full border-2 border-white ${event.color}`}></div>
              
              {/* Event content */}
              <div className="bg-white p-2 rounded border border-gray-200 shadow-sm">
                <div className="text-xs font-medium text-gray-800 mb-1">{event.time}</div>
                <div className="text-sm text-gray-600">{event.event}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Timeline controls */}
      <div className="mt-2 flex justify-between items-center">
        <button className="text-xs px-2 py-1 border border-gray-300 rounded flex items-center">
          <span className="mr-1">+</span> Add Event
        </button>
        <div className="flex">
          <button className="text-xs px-2 py-1 bg-gray-100 border border-gray-300 rounded-l">Zoom Out</button>
          <button className="text-xs px-2 py-1 bg-gray-100 border-t border-b border-r border-gray-300 rounded-r">Zoom In</button>
        </div>
      </div>
    </div>
  );
};

export default Timeline; 