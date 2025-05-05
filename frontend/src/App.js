import React from "react";
import Home from "./pages/Home"
// import StudentPage from "./pages/StudentPage"
import {BrowserRouter as Router, Routes, Route} from "react-router-dom"


function App() {
    return (
    <Router>
        <Routes>
            <Route path="/" element={<Home />} />
            {/* <Route path="/student/:name" element={<StudentPage />} /> */}
        </Routes>
    </Router>);
}

export default App;