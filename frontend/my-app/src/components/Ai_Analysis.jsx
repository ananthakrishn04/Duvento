import React from 'react';

const AIKnowledgeAnalysis = () => {
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

  // Sample data - in a real app, this would come from props or API
  const userData = {
    name: "John Smith",
    role: "Java Developer • Intermediate Level",
    generatedDate: "May 12, 2025",
    analysisId: "AA-2025-05-12-JS"
  };

  const strengths = [
    {
      label: "Algorithm Implementation",
      percentage: 92,
      description: "Excellent ability to implement various algorithms efficiently. You consistently write clean, optimized code."
    },
    {
      label: "Problem Solving", 
      percentage: 88,
      description: "Strong analytical skills and creative approach to solving complex problems."
    },
    {
      label: "Data Structures",
      percentage: 85,
      description: "Good understanding of when and how to use appropriate data structures."
    }
  ];

  const knowledgeGaps = [
    {
      label: "Design Patterns",
      percentage: 45,
      description: "Limited application of common design patterns. This impacts code maintainability and scalability."
    },
    {
      label: "System Architecture",
      percentage: 38,
      description: "Need to improve understanding of designing scalable and maintainable systems."
    },
    {
      label: "Testing Practices",
      percentage: 52,
      description: "Inconsistent test coverage and limited use of testing methodologies."
    }
  ];

  const courseRecommendations = [
    {
      title: "Design Patterns Mastery Course",
      description: "Learn practical applications of common design patterns with real-world examples. This course covers creational, structural, and behavioral patterns.",
      weeks: 4,
      modules: 12,
      completionRate: 94
    },
    {
      title: "System Architecture: From Monolith to Microservices", 
      description: "Comprehensive guide to modern system architecture principles, focusing on scalability, fault tolerance, and maintainable design.",
      weeks: 6,
      modules: 18,
      completionRate: 88
    },
    {
      title: "Test-Driven Development Workshop",
      description: "Practical workshop on implementing TDD in your workflow, covering unit testing, integration testing, and test automation.",
      weeks: 2,
      modules: 8,
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
                    AI Knowledge Analysis
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold text-lg">
                    JS
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-800">{userData.name}</h2>
                    <p className="text-gray-600">{userData.role}</p>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="flex gap-2 mb-2">
                  <div className="w-8 h-8 bg-yellow-400 rounded-full flex items-center justify-center cursor-pointer hover:bg-yellow-500 transition-colors">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                      <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                    </svg>
                  </div>
                  <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center cursor-pointer hover:bg-gray-400 transition-colors">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                      <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                  </div>
                </div>
                <p className="text-sm text-gray-500">Generated: {userData.generatedDate}</p>
              </div>
            </div>
          </div>

          {/* AI Analysis Summary */}
          <div className="p-6">
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6">
              <h3 className="text-lg font-semibold text-blue-800 mb-2">AI Analysis Summary</h3>
              <p className="text-gray-700 text-sm leading-relaxed">
                Based on your performance across 5 coding challenges and 3 knowledge assessments, our AI has identified several areas of strength and some knowledge 
                gaps. Your strong algorithm implementation and problem-solving skills could benefit from improving your knowledge of design patterns and system 
                architecture. Recommendations for targeted learning have been provided below.
              </p>
            </div>

            {/* Strengths and Knowledge Gaps */}
            <div className="grid md:grid-cols-2 gap-8 mb-8">
              {/* Your Strengths */}
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Your Strengths</h3>
                {strengths.map((strength, index) => (
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
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Knowledge Gaps</h3>
                {knowledgeGaps.map((gap, index) => (
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
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Personalized Learning Recommendations</h3>
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
                Analysis ID: {userData.analysisId}
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