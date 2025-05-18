import React from 'react';
import PropTypes from 'prop-types';

const EventCard = ({ image, title, time, badge, onJoin }) => {
  return (
    <div 
      className="relative h-[180px] rounded-lg overflow-hidden shadow-md transition-all duration-300 cursor-pointer hover:transform hover:-translate-y-1 hover:shadow-lg"
      onClick={onJoin}
    >
      <img src={image} alt={title} className="w-full h-full object-cover" />
      {badge && (
        <div className="absolute top-2.5 right-2.5 bg-pink-500 text-white text-xs px-2 py-1 rounded-full">
          {badge}
        </div>
      )}
      <div className="absolute bottom-0 left-0 right-0 p-4 bg-gradient-to-t from-black/80 to-transparent text-white">
        <div className="font-semibold mb-1">{title}</div>
        <div className="text-sm opacity-80">{time}</div>
      </div>
    </div>
  );
};

EventCard.propTypes = {
  image: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  time: PropTypes.string.isRequired,
  badge: PropTypes.string,
  onJoin: PropTypes.func.isRequired,
};

export default EventCard; 