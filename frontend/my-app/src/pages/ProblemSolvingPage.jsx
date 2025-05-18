import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { sessionService } from '../services/sessionService';
import CodeEditor from '../components/CodeEditor';

const ProblemSolvingPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [sessionId, setSessionId] = useState(null);
  const [problem, setProblem] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [winner, setWinner] = useState(null);
  const [sessionEnded, setSessionEnded] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const sid = params.get('sessionId');
    
    if (!sid) {
      navigate('/');
      return;
    }
    
    setSessionId(sid);
    
    // Make sure WebSocket is connected
    sessionService.webSocketManager.connect(sid);
    
    // Set up WebSocket listeners
    const leaderboardListener = sessionService.webSocketManager.addListener(
      'leaderboardUpdate',
      (data) => {
        setLeaderboard(data);
      }
    );

    const sessionEndListener = sessionService.webSocketManager.addListener(
      'sessionEnd',
      (data) => {
        setWinner(data.winner);
        setSessionEnded(true);
      }
    );
    
    // Fetch the problem for this session
    const fetchProblem = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/sessions/${sid}/problems/`, {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Token ${localStorage.getItem('authToken')}`,
          },
        });
        const data = await response.json();
        setProblem(data[0]); // Assuming the API returns an array of problems
      } catch (error) {
        console.error('Failed to fetch problem:', error);
      }
    };
    
    fetchProblem();
    
    // Cleanup function
    return () => {
      leaderboardListener();
      sessionEndListener();
    };
  }, [location.search, navigate]);

  const handleSubmitSolution = async (code, language) => {
    try {
      const response = await fetch("http://localhost:8000/api/submissions/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Token ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify({
          problem_id: problem?.id,
          session_id: sessionId,
          code: code,
          language: language,
          submit: true
        })
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to submit solution:', error);
      return { error: error.message };
    }
  };

  const handleRunCode = async (code, language) => {
    try {
      const response = await fetch("http://localhost:8000/api/submissions/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Token ${localStorage.getItem("authToken")}`,
        },
        body: JSON.stringify({
          problem_id: problem?.id,
          session_id: sessionId,
          code: code,
          language: language,
          submit: false
        })
      });
      
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Failed to run code:', error);
      return { error: error.message };
    }
  };

  const renderLeaderboard = () => {
    if (!leaderboard || leaderboard.length === 0) return null;
    
    return (
      <div className="leaderboard">
        <h3>Leaderboard</h3>
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>User</th>
              <th>Problems Solved</th>
              <th>Time</th>
              <th>Score</th>
            </tr>
          </thead>
          <tbody>
            {leaderboard.map((entry, index) => (
              <tr 
                key={entry.username}
                className={entry.username === winner ? 'winner' : ''}
              >
                <td>{index + 1}</td>
                <td>{entry.username}</td>
                <td>{entry.problems_solved}</td>
                <td>{entry.formatted_time}</td>
                <td>{entry.score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  if (!problem) {
    return <div className="loading">Loading problem...</div>;
  }

  return (
    <div className="problem-solving-page">
      <div className="problem-content">
        <div className="problem-description">
          <h2>{problem.title}</h2>
          <div dangerouslySetInnerHTML={{ __html: problem.description }} />
          
          <div className="test-cases">
            <h3>Test Cases</h3>
            {problem.test_cases && problem.test_cases.map((testCase, index) => (
              <div key={index} className="test-case">
                <p><strong>Test Case {index + 1}</strong></p>
                <p>Input: {JSON.stringify(testCase.input)}</p>
                <p>Expected Output: {JSON.stringify(testCase.expected_output)}</p>
              </div>
            ))}
          </div>
          
          {renderLeaderboard()}
          
          {sessionEnded && (
            <div className="session-ended">
              <h3>Session has ended!</h3>
              {winner && <p>Winner: {winner}</p>}
              <button onClick={() => navigate('/')}>Back to Home</button>
            </div>
          )}
        </div>
      </div>
      
      <div className="code-editor-container">
        <CodeEditor 
          onSubmit={handleSubmitSolution}
          onRun={handleRunCode}
          disabled={sessionEnded}
        />
      </div>
    </div>
  );
};

export default ProblemSolvingPage; 