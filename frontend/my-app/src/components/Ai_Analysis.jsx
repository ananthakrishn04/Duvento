import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const AIKnowledgeAnalysis = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const gameData = location.state?.gameData;

  // If no game data is provided, show an error state
  if (!gameData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-cyan-400 via-blue-500 to-blue-600 p-5">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-8 text-center">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">No Game Data Available</h2>
            <p className="text-gray-600 mb-6">Please select a game from your history to view its analysis.</p>
            <button
              onClick={() => navigate('/profile')}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
            >
              Return to Profile
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Progress Bar Component
  const ProgressBar = ({ percentage, color = 'blue', label, description }) => {
    const getColorClasses = (color) => {
      switch (color) {
        case 'blue':
          return 'bg-blue-500';
        case 'red':
          return 'bg-red-500';
        case 'green':
          return 'bg-green-500';
        default:
          return 'bg-blue-500';
      }
    };

    return (
      <div className="mb-4">
        <div className="flex justify-between items-center mb-1">
          <span className="text-sm font-medium text-gray-700">{label}</span>
          <span className="text-sm font-bold text-gray-800">{percentage}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
          <div 
            className={`h-2 rounded-full ${getColorClasses(color)}`}
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
        {description && (
          <p className="text-xs text-gray-600">{description}</p>
        )}
      </div>
    );
  };

  // Course Recommendation Card Component
  const CourseCard = ({ title, description, weeks, modules, completionRate }) => {
    return (
      <div className="bg-gray-50 rounded-lg p-4 mb-4 border border-gray-200">
        <h4 className="text-blue-600 font-medium mb-2">{title}</h4>
        <p className="text-sm text-gray-600 mb-3">{description}</p>
        <div className="flex justify-between text-xs text-gray-500">
          <span>{weeks} weeks • {modules} modules</span>
          <span className="font-medium">{completionRate}% completion rate</span>
        </div>
      </div>
    );
  };

  // Generate analysis based on game data
  const generateAnalysis = (gameData) => {
    const strengths = [];
    const gaps = [];
    
    // Analyze based on game result
    if (gameData.result === 'WIN') {
      strengths.push({
        label: "Problem Solving Speed",
        percentage: 90,
        description: "Excellent performance in solving the problem quickly and efficiently."
      });
    } else {
      gaps.push({
        label: "Problem Solving Speed",
        percentage: 60,
        description: "There's room for improvement in solving problems more quickly."
      });
    }

    // Add problem-specific analysis
    if (gameData.problem) {
      strengths.push({
        label: `${gameData.problem.title} Concepts`,
        percentage: gameData.result === 'WIN' ? 85 : 70,
        description: `Understanding of concepts related to ${gameData.problem.title}.`
      });
    }

    // Add competitive analysis
    if (gameData.opponent) {
      const competitiveScore = gameData.result === 'WIN' ? 95 : 75;
      strengths.push({
        label: "Competitive Programming",
        percentage: competitiveScore,
        description: "Ability to solve problems under time pressure in competitive scenarios."
      });
    }

    return {
      strengths,
      gaps
    };
  };

  const analysis = generateAnalysis(gameData);

  // Course recommendations based on game performance
  const courseRecommendations = [
    {
      title: "Advanced Problem Solving Techniques",
      description: "Master advanced algorithms and problem-solving strategies for competitive programming.",
      weeks: 4,
      modules: 12,
      completionRate: 94
    },
    {
      title: "Time Management in Coding Challenges",
      description: "Learn to optimize your approach and manage time effectively during coding competitions.",
      weeks: 2,
      modules: 8,
      completionRate: 96
    },
    {
      title: "Data Structures Deep Dive",
      description: "Comprehensive coverage of essential data structures for efficient problem solving.",
      weeks: 6,
      modules: 15,
      completionRate: 92
    }
  ];

  const handleDownloadReport = () => {
    // In a real app, this would trigger a file download
    alert('Report download functionality would be implemented here');
  };

  const handleCreateLearningPlan = () => {
    // In a real app, this would navigate to learning plan creation
    alert('Learning plan creation functionality would be implemented here');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-400 via-blue-500 to-blue-600 p-5">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          {/* Header */}
          <div className="bg-white p-6 border-b border-gray-100">
            <div className="flex justify-between items-start">
              <div>
                <div className="flex items-center gap-4 mb-4">
                  <div className="text-2xl font-bold text-cyan-500">
                    Duvento
                  </div>
                  <div className="text-gray-500 text-sm">
                    Game Performance Analysis
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold text-lg">
                    {gameData.opponent ? gameData.opponent.display_name.charAt(0) : 'G'}
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-800">Game Analysis</h2>
                    <p className="text-gray-600">
                      {gameData.problem ? gameData.problem.title : 'Coding Challenge'} • {gameData.date}
                    </p>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="flex gap-2 mb-2">
                  <button
                    onClick={() => navigate('/profile')}
                    className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center cursor-pointer hover:bg-gray-400 transition-colors"
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M19 12H5M12 19l-7-7 7-7"/>
                    </svg>
                  </button>
                </div>
                <p className="text-sm text-gray-500">Analysis ID: GA-{new Date().getTime()}</p>
              </div>
            </div>
          </div>

          {/* AI Analysis Summary */}
          <div className="p-6">
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
              <h3 className="text-lg font-semibold text-blue-800 mb-2">Game Performance Summary</h3>
              <p className="text-gray-700 text-sm leading-relaxed">
                Based on your performance in this {gameData.result.toLowerCase()} against {gameData.opponent ? gameData.opponent.display_name : 'other players'}, 
                we've analyzed your coding approach and problem-solving strategies. Here's a detailed breakdown of your strengths and areas for improvement.
              </p>
            </div>

            {/* Strengths and Knowledge Gaps */}
            <div className="grid md:grid-cols-2 gap-8 mb-8">
              {/* Your Strengths */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Your Strengths</h3>
                {analysis.strengths.map((strength, index) => (
                  <ProgressBar
                    key={index}
                    label={strength.label}
                    percentage={strength.percentage}
                    color="blue"
                    description={strength.description}
                  />
                ))}
              </div>

              {/* Knowledge Gaps */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Areas for Improvement</h3>
                {analysis.gaps.map((gap, index) => (
                  <ProgressBar
                    key={index}
                    label={gap.label}
                    percentage={gap.percentage}
                    color="red"
                    description={gap.description}
                  />
                ))}
              </div>
            </div>

            {/* Personalized Learning Recommendations */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Recommended Next Steps</h3>
              <div className="space-y-4">
                {courseRecommendations.map((course, index) => (
                  <CourseCard
                    key={index}
                    title={course.title}
                    description={course.description}
                    weeks={course.weeks}
                    modules={course.modules}
                    completionRate={course.completionRate}
                  />
                ))}
              </div>
            </div>

            {/* Footer */}
            <div className="flex flex-col sm:flex-row justify-between items-center pt-6 border-t border-gray-200 gap-4">
              <div className="text-sm text-gray-500">
                Game Result: <span className={`font-medium ${
                  gameData.result === 'WIN' ? 'text-green-600' : 'text-red-600'
                }`}>{gameData.result}</span>
              </div>
              <div className="flex gap-3">
                <button 
                  onClick={handleDownloadReport}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors font-medium"
                >
                  Download Report
                </button>
                <button 
                  onClick={handleCreateLearningPlan}
                  className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2 font-medium"
                >
                  Create Learning Plan
                  <span className="text-lg">→</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIKnowledgeAnalysis;