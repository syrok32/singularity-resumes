import { studentDetails } from "../data/students"

function StudentCard({ student }) {
    const studentDetail = studentDetails.find(detail => detail.student_id === student.id);

    return (
        <article className="st-card">

            <a href={student.profile_url} target="_blank" rel="noopener noreferrer">
                <img
                    src={student.photo_url}
                    alt={`${student.full_name}'s photo`}
                    className="st-card_photo"
                />

                <div className="skills">
                    {student.top_skills && student.top_skills.map((skill, index) => (
                        <span key={index} className="skill-tag">{skill}</span>
                    ))}
                </div>

                <h1 className="st-card_name">{student.full_name}</h1>
                <h2 className="st-card_role">{student.role}</h2>
            </a>
        </article>
    );
}

export default StudentCard;
