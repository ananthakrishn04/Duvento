import React from 'react';
import Header from './Header';
import EventsSection from './EventsSection';
import HistorySection from './HistorySection';

const LandingPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0acffe] to-[#2a5cff] p-5">
      <div className="max-w-7xl mx-auto">
        <Header />
        <EventsSection />
        <HistorySection />
      </div>
    </div>
  );
};

export default LandingPage; 