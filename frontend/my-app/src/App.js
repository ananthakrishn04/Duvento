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

function App() {
  return (
    <AuthProvider>
      <SessionProvider>
        <Router>
          <div className="App">
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/landing" element={<LandingPage />} />
              <Route
                path="/editor"
                element={
                  <ProtectedRoute>
                    <CodeEditorPage />
                  </ProtectedRoute>
                }
              />
              <Route path="/problems/create" element={<CreateProblem />} />
              <Route path="/" element={<Navigate to="/landing" replace />} />
            </Routes>
          </div>
        </Router>
      </SessionProvider>
    </AuthProvider>
  );
}

export default App;
