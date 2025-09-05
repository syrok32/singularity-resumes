import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import StudentPage from "./pages/StudentPage.jsx"
import StudentProfile from "./pages/StudentProfile.jsx"
import StatsPage from "./pages/StatsPage.jsx"
import Header from "./components/Header.jsx"
import "./App.css"

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <Routes>
          <Route path="/" element={<StudentPage />} />
          <Route path="/student/:id" element={<StudentProfile />} />
          <Route path="/stats" element={<StatsPage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
