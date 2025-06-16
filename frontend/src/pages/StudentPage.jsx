import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

function StudentPage() {
  const { id } = useParams();
  const [student, setStudent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    axios.get(`http://127.0.0.1:8000/api/student/${id}`)
      .then(response => {
        setStudent(response.data.student); // Предполагая, что структура включает student
        setError(null);
      })
      .catch(err => {
        setError('Failed to fetch student profile');
        console.error(err);
      })
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <div className="text-center py-4">Loading...</div>;
  if (error) return <div className="text-red-500 text-center py-4">{error}</div>;
  if (!student) return <div className="text-center py-4">Student not found</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">{student.full_name}</h1>
      {student.photo_url && (
        <img src={student.photo_url} alt={student.full_name} className="w-40 h-40 object-cover rounded-full mx-auto mb-4" />
      )}
      <p className="text-lg"><strong>Role:</strong> {student.role}</p>
      <p className="text-lg"><strong>Skills:</strong> {student.top_skills.join(', ') || 'None'}</p>
      <p className="text-gray-700 mt-2">{student.short_description}</p>
      <a href={student.profile_url} target="_blank" rel="noopener noreferrer" className="text-blue-500 mt-4 inline-block">
        View Profile
      </a>
    </div>
  );
}

export default StudentPage;