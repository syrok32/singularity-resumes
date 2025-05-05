import React from "react";
import { students } from "../data/students"
import StudentCard from "../components/StusentCard";

function Home() {
    return (
        <div>
            <h1 className="title">Список студентов:</h1>
            {students.map((student) => (
                <StudentCard student={student} />
            ))}
        </div>
    );
}

export default Home;

