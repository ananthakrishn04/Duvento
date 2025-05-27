import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import './App.css';
import CodeEditorPage from './components/CodeEditorPage';
import { Login } from './screens/Login';
import { AuthProvider } from './context/AuthContext';
import { SessionProvider } from './context/SessionContext';
import ProtectedRoute from './components/ProtectedRoute';
import LandingPage from './components/LandingPage';
import CreateProblem from './components/CreateProblem';
import ProfilePage from './components/ProfilePage';
import AIKnowledgeAnalysis from './components/Ai_Analysis';

function App() {
  return (
    <AuthProvider>
      <SessionProvider>
        <Router>
          <div className="App">
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              
              {/* Protected routes */}
              <Route
                path="/landing"
                element={
                  <ProtectedRoute>
                    <LandingPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/editor"
                element={
                  <ProtectedRoute>
                    <CodeEditorPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/problems/create"
                element={
                  <ProtectedRoute>
                    <CreateProblem />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile"
                element={
                  <ProtectedRoute>
                    <ProfilePage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/analysis"
                element={
                  <ProtectedRoute>
                    <AIKnowledgeAnalysis />
                  </ProtectedRoute>
                }
              />
              
              {/* Redirect root to landing page */}
              <Route path="/" element={<Navigate to="/landing" replace />} />
              
              {/* Catch all route - redirect to login */}
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </div>
        </Router>
      </SessionProvider>
    </AuthProvider>
  );
}

export default App;
