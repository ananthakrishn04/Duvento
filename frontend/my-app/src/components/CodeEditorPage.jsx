import React, { useState, useEffect } from 'react';
import { Clock, BellIcon, UserIcon, ChevronRight, LogOut } from 'lucide-react';
import CodeEditor from './CodeEditor';
import { useLocation, useNavigate } from 'react-router-dom';

const CodeEditorPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [problem, setProblem] = useState(null);
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('javascript');
  const [submissionStatus, setSubmissionStatus] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showQuitWarning, setShowQuitWarning] = useState(false);
  const [passedTests, setPassedTests] = useState(0);
  const [showWinnerPopup, setShowWinnerPopup] = useState(false);
  const [winnerData, setWinnerData] = useState(null);
  const [leaderboardData, setLeaderboardData] = useState(null);
  const [socket, setSocket] = useState(null);
  const [timeRemaining, setTimeRemaining] = useState(15 * 60); // 15 minutes in seconds

  // Convert seconds to minutes:seconds format
  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
  };

  // Timer effect
  useEffect(() => {
    let timerInterval;
    
    if (location.state?.problem) {
      // Start the timer
      timerInterval = setInterval(() => {
        setTimeRemaining(prevTime => {
          if (prevTime <= 1) {
            // Timer has reached zero, clear interval
            clearInterval(timerInterval);
            // End the session
            handleTimeUp();
            return 0;
          }
          return prevTime - 1;
        });
      }, 1000);
    }
    
    // Cleanup timer on unmount
    return () => {
      if (timerInterval) {
        clearInterval(timerInterval);
      }
    };
  }, [location.state?.problem]);

  // Handle time up
  const handleTimeUp = async () => {
    // Only proceed if we haven't already shown the winner popup
    if (showWinnerPopup) return;
    
    try {
      // Call an API to mark the session as ended due to timeout
      if (location.state?.sessionId) {
        const response = await fetch(`http://localhost:8000/api/sessions/${location.state.sessionId}/timeout/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Token ${localStorage.getItem('token')}`,
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          // Show the timeout notification
          setWinnerData({
            display_name: "Time's up!",
            isTimeout: true
          });
          if (data.leaderboard) {
            setLeaderboardData(data.leaderboard);
          }
          setShowWinnerPopup(true);
        }
      } else {
        // If no session ID, just show a generic timeout popup
        setWinnerData({
          display_name: "Time's up!",
          isTimeout: true
        });
        setShowWinnerPopup(true);
      }
    } catch (error) {
      console.error('Error handling time up:', error);
      // Show a generic timeout popup even if the API call fails
      setWinnerData({
        display_name: "Time's up!",
        isTimeout: true
      });
      setShowWinnerPopup(true);
    }
  };

  useEffect(() => {
    // Get problem data from location state
    if (location.state?.problem) {
      console.log('Problem data received:', location.state.problem);
      setProblem(location.state.problem);
      
      // Log profile information for debugging
      console.log('Current user profile:', location.state?.profile);

      // Setup WebSocket connection for game updates
      if (location.state?.sessionId) {
        const sessionId = location.state.sessionId;
        // Connect to WebSocket for real-time updates
        const ws = new WebSocket(`ws://localhost:8000/ws/game/${sessionId}/`);
        
        ws.onopen = () => {
          console.log('WebSocket connection established');
        };
        
        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          console.log('WebSocket message received:', data);
          
          // Handle different message types
          if (data.type === 'game_ended') {
            // Game has ended with a winner
            console.log('Game ended notification received', data);
            
            // Update timeout status if this was a timeout
            if (data.timeout) {
              // Set timer to 0 to update progress bar
              setTimeRemaining(0);
              setWinnerData({
                ...data.winner,
                isTimeout: true
              });
            } else {
              setWinnerData(data.winner);
            }
            
            setLeaderboardData(data.leaderboard);
            setShowWinnerPopup(true);
          }
        };
        
        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
        
        setSocket(ws);
        
        // Cleanup WebSocket connection when component unmounts
        return () => {
          if (ws) {
            ws.close();
          }
        };
      }
    } else {
      console.warn('No problem data in location state:', location.state);
    }
  }, [location]);

  const handleCodeChange = ({ code: newCode, language: newLanguage }) => {
    setCode(newCode);
    setLanguage(newLanguage);
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setSubmissionStatus(null);

    // Check if we have a valid problem ID
    if (!problem?.id) {
      setSubmissionStatus({
        error: true,
        message: 'Invalid problem ID. Please try again.',
      });
      setIsSubmitting(false);
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/solve/${problem.id}/submit/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({
          code: code,
          language: language,
          session_id: location.state?.sessionId,
          profile_id: location.state?.profile?.id // Include profile ID for better tracking
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit code');
      }

      const data = await response.json();
      
      // Format the submission status message
      let statusMessage = '';
      if (data.result.error && data.result.error !== 'No errors') {
        statusMessage = `Error: ${data.result.error}`;
      } else {
        statusMessage = `Status: ${data.result.status}\nOutput: ${data.result.output}\nExecution Time: ${data.result.time}\nMemory Usage: ${data.result.memory}`;
      }

      setSubmissionStatus({
        error: data.result.error && data.result.error !== 'No errors',
        message: statusMessage,
        ...data
      });

      // Update the passed tests count if available in the response
      if (data.passed !== undefined) {
        setPassedTests(data.passed);
      }

      // If the session ended (problem solved), handle that
      if (data.session_ended) {
        console.log('Session ended - Problem solved!', data.leaderboard);
        setWinnerData(data.winner);
        setLeaderboardData(data.leaderboard);
        setShowWinnerPopup(true);
      }
    } catch (error) {
      console.error('Submission error:', error);
      setSubmissionStatus({
        error: true,
        message: error.message || 'Failed to submit code. Please try again.',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuit = async () => {
    try {
      // Call the API to leave the session
      const response = await fetch(`http://localhost:8000/api/sessions/${location.state?.sessionId}/leave/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Token ${localStorage.getItem('token')}`,
        },
      });

      if(!response.ok)
      {
        throw new Error('Failed to leave session');
      }

      // Close WebSocket if it exists
      if (socket) {
        socket.close();
      }

      // Navigate back to landing page
      navigate('/landing');
    } catch (error) {
      console.error('Error leaving session:', error);
      alert('Failed to leave session. Please try again.');
    }
  };

  const handleWinnerContinue = () => {
    setShowWinnerPopup(false);
    navigate('/landing');
  };

  return (
    <div className="w-full min-h-screen" style={{
      background: 'linear-gradient(120deg, #00bcd4 0%, #2196f3 100%)',
      backgroundSize: 'cover',
      overflow: 'hidden'
    }}>
      {/* Quit Warning Modal */}
      {showQuitWarning && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">Quit Game?</h3>
            <p className="text-gray-600 mb-6">
              Are you sure you want to quit the game? This action cannot be undone and you will lose your progress.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowQuitWarning(false)}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleQuit}
                className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
              >
                Quit Game
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Winner Popup Modal */}
      {showWinnerPopup && winnerData && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="text-center mb-4">
              <div className="w-20 h-20 mx-auto bg-blue-100 rounded-full flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={winnerData.isTimeout ? "M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" : "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"} />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-gray-800 mb-2">Game Over!</h3>
              {winnerData.isTimeout ? (
                <p className="text-lg text-orange-600 font-semibold mb-4">
                  Time's up! The game has ended.
                </p>
              ) : winnerData.id === (location.state?.profile?.id || -1) ? (
                <p className="text-lg text-green-600 font-semibold mb-4">
                  Congratulations! You won the game!
                </p>
              ) : (
                <p className="text-lg text-blue-600 font-semibold mb-4">
                  {winnerData.display_name} has won the game!
                </p>
              )}
              <p className="text-sm text-gray-600 mb-2">
                ELO ratings have been updated based on match results.
              </p>
            </div>
            
            {leaderboardData && leaderboardData.length > 0 && (
              <div className="mb-6">
                <h4 className="font-semibold text-gray-700 mb-2">Leaderboard</h4>
                <div className="bg-gray-50 rounded p-3 max-h-40 overflow-auto">
                  {leaderboardData.map((player, index) => (
                    <div key={index} className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                      <span className="font-medium">{index + 1}. {player.username}</span>
                      <div className="flex flex-col items-end">
                        <span className="text-sm text-gray-500">Score: {player.score}</span>
                        {player.rating && (
                          <span className="text-xs font-medium">
                            Rating: {player.rating}
                            {player.rating_change > 0 && (
                              <span className="text-green-600 ml-1">+{player.rating_change}</span>
                            )}
                            {player.rating_change < 0 && (
                              <span className="text-red-600 ml-1">{player.rating_change}</span>
                            )}
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div className="text-center">
              <button
                onClick={handleWinnerContinue}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
              >
                Back to Home
              </button>
            </div>
          </div>
        </div>
      )}

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
            </div>
            <div className="flex items-center justify-center">
              <div className="flex items-center">
                <Clock size={20} className="text-blue-600 mr-2" />
                <div className="font-semibold text-2xl text-gray-800">{formatTime(timeRemaining)}</div>
              </div>
            </div>
            <div className="flex items-center">
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
                <h3 className="font-['Open_Sans',Helvetica] font-semibold text-gray-800 mb-2">
                  {problem ? problem.title : 'Description'}
                </h3>
                <div className="w-full h-40 bg-gray-50 border border-[#00000029] rounded p-3 text-sm text-gray-700 overflow-auto">
                  {problem ? (
                    <div>
                      <p>{problem.description}</p>
                      <p className="mt-2">Difficulty: {problem.difficulty}</p>
                      <p className="mt-2">Time Limit: {problem.time_limit}s</p>
                      <p>Memory Limit: {problem.memory_limit}MB</p>
                    </div>
                  ) : (
                    <p>Loading problem description...</p>
                  )}
                </div>
              </div>
              
              <div className="mb-6">
                <h3 className="font-['Open_Sans',Helvetica] font-semibold text-gray-800 mb-2">Example Test Cases</h3>
                <div className="w-full h-32 bg-gray-50 border border-[#00000029] rounded p-3 font-mono text-sm text-gray-700 overflow-auto">
                  {problem ? (
                    <div>
                      {problem.test_cases.map((testCase, index) => (
                        <div key={index} className="mb-2">
                          <p>Test Case {index + 1}:</p>
                          <p>Input: {testCase.input}</p>
                          <p>Expected Output: {testCase.expected_output}</p>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p>Loading test cases...</p>
                  )}
                </div>
              </div>
              
              <div className="flex-grow">
                <h3 className="font-['Open_Sans',Helvetica] font-semibold text-gray-800 mb-2">Constraints</h3>
                <div className="w-full h-32 bg-gray-50 border border-[#00000029] rounded p-3 text-sm text-gray-700 overflow-auto">
                  <ul className="list-disc pl-4">
                    <li>Time Limit: {problem?.time_limit || 1} second</li>
                    <li>Memory Limit: {problem?.memory_limit || 128} MB</li>
                    <li>Input must match the format shown in test cases</li>
                    <li>Output must exactly match the expected output</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Timeline separator - vertical time progress */}
            <div className="h-full w-[5px] bg-gray-100 relative">
              {/* Calculate progress from 0% (15 min) to 100% (0 min) */}
              {(() => {
                // When timeRemaining = 15*60, progressPercent = 0
                // When timeRemaining = 0, progressPercent = 100
                const totalTime = 15 * 60; // 15 minutes in seconds
                const elapsedTime = totalTime - timeRemaining;
                const progressPercent = (elapsedTime / totalTime) * 100;
                
                return (
                  <div 
                    className="absolute left-0 top-0 w-full bg-blue-500 transition-all duration-1000" 
                    style={{ height: `${progressPercent}%` }}
                  ></div>
                );
              })()}
              <div 
                className="absolute left-[-6px] w-4 h-4 rounded-full bg-blue-600 border-2 border-white transition-all duration-1000"
                style={{ 
                  top: `${((15 * 60 - timeRemaining) / (15 * 60)) * 100}%`, 
                  transform: 'translateY(-50%)' 
                }}
              ></div>
            </div>
            
            {/* Right panel - Code editor */}
            <div className="w-1/2 p-6 flex flex-col">
              <h3 className="font-['Open_Sans',Helvetica] font-semibold text-gray-800 mb-2">Code Editor</h3>
              <div className="flex-grow">
                <CodeEditor 
                  initialCode={`// Write your solution for ${problem?.title || 'the problem'} here\n\n`}
                  onCodeChange={handleCodeChange}
                />
              </div>
              {submissionStatus && (
                <div className={`mt-4 p-4 rounded ${
                  submissionStatus.error 
                    ? 'bg-red-100 text-red-700 border border-red-300' 
                    : 'bg-green-100 text-green-700 border border-green-300'
                }`}>
                  <pre className="whitespace-pre-wrap font-mono text-sm">
                    {submissionStatus.message}
                  </pre>
                </div>
              )}
            </div>
          </div>

          {/* Bottom action bar */}
          <div className="w-full h-14 bg-white border-t border-[#00000029] px-6 flex justify-between items-center">
            <div className="flex items-center gap-4">
              <div className="font-['Open_Sans',Helvetica] text-gray-700">
                <span className="font-semibold">Hidden Case:</span> {passedTests}/{problem?.test_cases?.length || 0} Passed
              </div>
              <div className="font-['Open_Sans',Helvetica] text-gray-700">
                <span className="font-semibold">Game ID:</span> GC-12345
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <button 
                className={`px-4 py-2 rounded flex items-center transition-colors ${
                  isSubmitting 
                    ? 'bg-gray-300 cursor-not-allowed' 
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
                onClick={handleSubmit}
                disabled={isSubmitting}
              >
                <span className="font-['Open_Sans',Helvetica] font-semibold text-sm">
                  {isSubmitting ? 'Submitting...' : 'Submit'}
                </span>
                <ChevronRight size={16} className="ml-1" />
              </button>
              <button 
                className="px-4 py-2 bg-[#c5051d] rounded flex items-center text-white hover:bg-red-700 transition-colors"
                onClick={() => setShowQuitWarning(true)}
              >
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