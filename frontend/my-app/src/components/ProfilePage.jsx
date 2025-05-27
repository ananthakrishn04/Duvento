import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import HistorySection from './HistorySection';

const ProfilePage = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!isAuthenticated) {
      navigate('/login');
      return;
    }

    // Fetch user profile data
    const fetchProfileData = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:8000/api/auth/me/', {
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch profile data');
        }

        const data = await response.json();
        setProfileData(data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching profile data:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchProfileData();
  }, [isAuthenticated, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0acffe] to-[#2a5cff] p-5">
        <div className="max-w-5xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <button 
              onClick={() => navigate('/landing')}
              className="px-4 py-2 text-white bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
            >
              ← Back to Home
            </button>
          </div>
          <div className="bg-white rounded-xl p-8 shadow-sm">
            <div className="animate-pulse flex flex-col items-center">
              <div className="h-24 w-24 rounded-full bg-blue-200 mb-4"></div>
              <div className="h-6 w-40 bg-blue-200 rounded mb-3"></div>
              <div className="h-4 w-60 bg-blue-100 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-[#0acffe] to-[#2a5cff] p-5">
        <div className="max-w-5xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <button 
              onClick={() => navigate('/landing')}
              className="px-4 py-2 text-white bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
            >
              ← Back to Home
            </button>
          </div>
          <div className="bg-white rounded-xl p-8 shadow-sm">
            <div className="text-center text-red-600">
              <p className="text-xl font-semibold mb-2">Error Loading Profile</p>
              <p className="text-gray-600">{error}</p>
              <button 
                onClick={() => window.location.reload()}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0acffe] to-[#2a5cff] p-5">
      <div className="max-w-5xl mx-auto">
        {/* Header with back button */}
        <div className="flex justify-between items-center mb-8">
          <button 
            onClick={() => navigate('/landing')}
            className="px-4 py-2 text-white bg-white/20 rounded-lg hover:bg-white/30 transition-colors"
          >
            ← Back to Home
          </button>
        </div>

        {/* Profile card */}
        <div className="bg-white rounded-xl p-8 shadow-lg mb-8">
          <div className="flex flex-col md:flex-row items-center md:items-start gap-8">
            {/* Profile picture */}
            <div className="w-32 h-32 rounded-full bg-gradient-to-br from-pink-500 to-blue-500 flex items-center justify-center text-white text-3xl font-bold">
              {profileData?.display_name?.charAt(0) || user?.username?.charAt(0) || '?'}
            </div>
            
            {/* Profile info */}
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-800 mb-2">
                {profileData?.display_name || user?.username || 'User'}
              </h1>
              <p className="text-gray-600 mb-4">
                @{user?.username || 'username'} · Member since {new Date(profileData?.joined_at || Date.now()).toLocaleDateString()}
              </p>
              
              {/* Stats cards */}
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-6">
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg text-center border-2 border-blue-200 shadow-sm">
                  <p className="text-gray-600 text-sm font-medium">ELO Rating</p>
                  <p className="text-3xl font-bold text-blue-600">{profileData?.rating || 1500}</p>
                  <div className="mt-1 text-xs">
                    {profileData?.rank && (
                      <span className="inline-block px-2 py-1 bg-blue-200 text-blue-800 rounded-full font-medium">
                        Rank #{profileData.rank}
                      </span>
                    )}
                  </div>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg text-center">
                  <p className="text-gray-500 text-sm">Problems Solved</p>
                  <p className="text-2xl font-bold text-green-600">{profileData?.problems_solved || 0}</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg text-center">
                  <p className="text-gray-500 text-sm">Current Streak</p>
                  <p className="text-2xl font-bold text-orange-600">{profileData?.streak || 0} days</p>
                </div>
              </div>
              
              {/* Rating description */}
              <div className="mt-6 bg-blue-50 p-4 rounded-lg border border-blue-200">
                <h3 className="font-semibold text-blue-800 mb-2">About ELO Rating</h3>
                <p className="text-sm text-gray-700">
                  Your ELO rating represents your skill level in competitive coding. Win matches against higher-rated players to gain more points.
                  Ratings are updated after every match based on match outcome and opponent ratings.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Badges section - if implemented */}
        {profileData?.badges && profileData.badges.length > 0 && (
          <div className="bg-white rounded-xl p-6 shadow-sm mb-8">
            <h2 className="text-xl font-semibold text-gray-800 relative pb-1.5 mb-5 after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-12 after:h-0.75 after:bg-pink-500 after:rounded">
              Badges
            </h2>
            <div className="flex flex-wrap gap-4">
              {profileData.badges.map((badge, index) => (
                <div key={index} className="flex items-center gap-2 bg-gray-50 px-3 py-2 rounded-full">
                  <span className="text-blue-500">
                    <i className={badge.icon}></i>
                  </span>
                  <span className="font-medium text-gray-700">{badge.name}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Game history section */}
        <HistorySection />
      </div>
    </div>
  );
};

export default ProfilePage; 