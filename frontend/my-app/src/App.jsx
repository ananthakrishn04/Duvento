import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Login } from './screens/Login';
import { Register } from './screens/Register';
import { Landing } from './screens/Landing';
import { AuthProvider } from './context/AuthContext';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/landing" element={<Landing />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App; 