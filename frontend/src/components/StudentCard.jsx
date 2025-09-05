import { Link } from "react-router-dom"

const StudentCard = ({ student }) => {
  const getAvatarUrl = (avatarUrl) => {
    if (!avatarUrl) return "/professional-student-portrait.png"
    if (avatarUrl.startsWith("http")) return avatarUrl
    return `http://127.0.0.1:8000${avatarUrl}`
  }

  const getCourseColor = (course) => {
    const colors = {
      1: "bg-blue-500",
      2: "bg-green-500",
      3: "bg-purple-500",
      4: "bg-orange-500",
      5: "bg-red-500",
    }
    return colors[course] || "bg-gray-500"
  }

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-6 hover:bg-slate-800/70 transition-all duration-300 hover:border-slate-600/50 hover:shadow-lg hover:shadow-purple-500/10">
      <div className="flex gap-6">
        {/* Avatar */}
        <div className="flex-shrink-0">
          <div className="w-32 h-32 rounded-xl overflow-hidden bg-slate-700">
            <img
              src={getAvatarUrl(student.avatar_url) || "/placeholder.svg"}
              alt={student.full_name}
              className="w-full h-full object-cover"
            />
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-3">
              <h3 className="text-xl font-semibold text-white text-balance">{student.full_name}</h3>
              {student.course && (
                <span
                  className={`inline-flex items-center justify-center w-6 h-6 text-xs font-bold text-white rounded-full ${getCourseColor(student.course)}`}
                >
                  {student.course}
                </span>
              )}
            </div>
          </div>

          <p className="text-slate-300 text-sm mb-4 font-medium">{student.specialty}</p>

          {/* Skills */}
          <div className="flex flex-wrap gap-2 mb-4">
            {student.skills &&
              student.skills.slice(0, 6).map((skill, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-slate-700/50 text-slate-200 text-xs rounded-full border border-slate-600/30 font-medium"
                >
                  {skill}
                </span>
              ))}
            {student.skills && student.skills.length > 6 && (
              <span className="px-3 py-1 bg-slate-700/50 text-slate-400 text-xs rounded-full border border-slate-600/30 font-medium">
                +{student.skills.length - 6} еще
              </span>
            )}
          </div>

          {/* Description */}
          <p className="text-slate-400 text-sm leading-relaxed mb-4 line-clamp-3">
            {student.description ||
              "Я начинающий специалист. Программирую более 2-ух лет. Занимаюсь спортивным программированием. Пишу на Java, Python, C++. Дважды финалист ВКОШП..."}
            <button className="text-purple-400 hover:text-purple-300 ml-1 font-medium">Читать дальше</button>
          </p>

          {/* Action Button */}
          <Link
            to={`/student/${student.id}`}
            className="inline-block px-6 py-2 bg-slate-700/50 hover:bg-slate-700 text-slate-200 text-sm rounded-lg border border-slate-600/30 hover:border-slate-500 transition-all duration-200 font-medium"
          >
            Смотреть резюме
          </Link>
        </div>
      </div>
    </div>
  )
}

export default StudentCard
