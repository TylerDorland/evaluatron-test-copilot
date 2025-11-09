import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Queries from './pages/Queries';
import Analytics from './pages/Analytics';
import ScheduledTests from './pages/ScheduledTests';
import './index.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <Router>
      <div>
        <header className="header">
          <div className="container">
            <h1>Evaluatron</h1>
            <nav className="nav">
              <Link to="/">Dashboard</Link>
              <Link to="/queries">Queries</Link>
              <Link to="/analytics">Analytics</Link>
              <Link to="/scheduled-tests">Scheduled Tests</Link>
              <button
                onClick={handleLogout}
                style={{
                  background: 'transparent',
                  border: '1px solid white',
                  color: 'white',
                  cursor: 'pointer',
                  padding: '5px 15px',
                  borderRadius: '4px',
                }}
              >
                Logout
              </button>
            </nav>
          </div>
        </header>

        <div className="container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/queries" element={<Queries />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/scheduled-tests" element={<ScheduledTests />} />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
