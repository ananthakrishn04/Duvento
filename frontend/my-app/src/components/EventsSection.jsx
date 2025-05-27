import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import EventCard from './EventCard';
import WaitingRoom from './WaitingRoom';
import { authService } from '../services/authService';
import { sessionService } from '../services/sessionService';

const EventsSection = () => {
  const navigate = useNavigate();
  const [joinSessionId, setJoinSessionId] = useState('');
  const [showJoinInput, setShowJoinInput] = useState(false);
  const [showWaitingRoom, setShowWaitingRoom] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState(null);
  
  const events = [
    {
      image: 'code-sample-code-challenge.png',
      title: 'Coding Challenge',
      time: 'Live Now',
      badge: 'GAME'
    },
    {
      image: 'algorithm-workshop.jpg',
      title: 'Algorithm Workshop',
      time: 'Today, 3:00 PM'
    },
    {
      image: 'mlworkshop.jpg',
      title: 'ML Session',
      time: 'May 20, 5:00 PM'
    },
    {
      image: 'webdevelopment.webp',
      title: 'Web Development',
      time: 'May 22, 2:00 PM'
    }
  ];

  const handleJoinRoom = async () => {
    if (!authService.isAuthenticated()) {
      navigate('/login', { state: { returnTo: '/editor', action: 'join' } });
      return;
    }

    setShowJoinInput(true);
  };

  const handleJoinSession = async () => {
    try {
      await sessionService.joinSession(joinSessionId);
      setCurrentSessionId(joinSessionId);
      setShowJoinInput(false);
      setShowWaitingRoom(true);
    } catch (error) {
      console.error('Failed to join session:', error);
      // Handle error (show message to user)
    }
  };

  const handleCreateRoom = async () => {
    if (!authService.isAuthenticated()) {
      navigate('/login', { state: { returnTo: '/editor', action: 'create' } });
      return;
    }

    try {
      const session = await sessionService.createSession();
      setCurrentSessionId(session.id);
      setShowWaitingRoom(true);
    } catch (error) {
      console.error('Failed to create session:', error);
      // Handle error (show message to user)
    }
  };

  return (
    <>
      <section className="bg-white rounded-xl p-5 mb-5 shadow-sm">
        <div className="flex justify-between items-center mb-5">
          <h2 className="text-xl font-semibold text-gray-800 relative pb-1.5 after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-12 after:h-0.75 after:bg-pink-500 after:rounded">
            Events
          </h2>
          <div className="flex gap-2.5 items-center">
            {showJoinInput ? (
              <div className="flex gap-2">
                <input
                  type="text"
                  value={joinSessionId}
                  onChange={(e) => setJoinSessionId(e.target.value)}
                  placeholder="Enter Session ID"
                  className="px-3 py-2 rounded-lg border border-gray-200 focus:outline-none focus:border-blue-500"
                />
                <button
                  onClick={handleJoinSession}
                  className="px-4 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors"
                >
                  Join
                </button>
              </div>
            ) : (
              <>
                <button className="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center shadow-md">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                  </svg>
                </button>
                <button 
                  onClick={handleJoinRoom}
                  className="px-4 py-2 rounded-lg bg-gray-100 text-gray-800 font-medium hover:bg-gray-200 transition-colors"
                >
                  Join Room
                </button>
                <button 
                  onClick={handleCreateRoom}
                  className="px-4 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors"
                >
                  Create Room
                </button>
              </>
            )}
          </div>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {events.map((event, index) => (
            <EventCard
              key={index}
              image={event.image}
              title={event.title}
              time={event.time}
              badge={event.badge}
              onJoin={handleCreateRoom}
            />
          ))}
        </div>
      </section>

      <WaitingRoom
        isOpen={showWaitingRoom}
        onClose={() => setShowWaitingRoom(false)}
        sessionId={currentSessionId}
      />
    </>
  );
};

export default EventsSection; 