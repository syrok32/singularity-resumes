export const fetchStudents = async () => {
  const response = await fetch('http://127.0.0.1:8000/api/students/');
  if (!response.ok) throw new Error('Failed to fetch students');
  return response.json();
};