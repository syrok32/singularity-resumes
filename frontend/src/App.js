import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import Home from './pages/Home';
import StudentPage from './pages/StudentPage';

function App() {
  return (
    <Router>
      <nav className="bg-gray-800 p-4">
        <Link to="/" className="text-white mx-4">Home</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/student/:id" element={<StudentPage />} />
      </Routes>
    </Router>  // Исправлено: закрываем <Router>, а не <div>
  );
}

export default App;