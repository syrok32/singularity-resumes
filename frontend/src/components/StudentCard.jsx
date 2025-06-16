import React from 'react';

function StudentCard({ student }) {
  return (
    <div className="border rounded-lg p-4 shadow hover:shadow-lg transition">
      {student.photo_url && (
        <img src={student.photo_url} alt={student.full_name} className="w-20 h-20 object-cover rounded-full mx-auto mb-2" />
      )}
      <h3 className="text-lg font-semibold">{student.full_name}</h3>
      <p className="text-gray-600">Role: {student.role}</p>
      <p className="text-gray-500">Skills: {student.top_skills.join(', ') || 'None'}</p>
    </div>
  );
}

export default StudentCard;