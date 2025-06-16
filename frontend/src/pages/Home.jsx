import React, { useState, useEffect } from 'react';
import axios from 'axios';
import StudentCard from '../components/StudentCard';

function Home() {
  const [students, setStudents] = useState([]);
  const [nextUrl, setNextUrl] = useState(null);
  const [prevUrl, setPrevUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStudents = async (url = 'http://127.0.0.1:8000/api/students/') => {
    setLoading(true);
    try {
      const response = await axios.get(url);
      setStudents(response.data.results);
      setNextUrl(response.data.next);
      setPrevUrl(response.data.previous);
      setError(null);
    } catch (err) {
      setError('Failed to fetch students');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudents();
  }, []);

  if (loading) return <div className="text-center py-4">Loading...</div>;
  if (error) return <div className="text-red-500 text-center py-4">{error}</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Students</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {students.map(student => (
          <StudentCard key={student.id} student={student} />
        ))}
      </div>
      <div className="mt-4 flex justify-between">
        <button
          onClick={() => fetchStudents(prevUrl)}
          disabled={!prevUrl}
          className="px-4 py-2 bg-gray-300 rounded disabled:opacity-50"
        >
          Previous
        </button>
        <button
          onClick={() => fetchStudents(nextUrl)}
          disabled={!nextUrl}
          className="px-4 py-2 bg-gray-300 rounded disabled:opacity-50"
        >
          Next
        </button>
      </div>
    </div>
  );
}

export default Home;