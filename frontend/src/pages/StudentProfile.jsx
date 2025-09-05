"use client"

import { useState, useEffect } from "react"
import { useParams, Link } from "react-router-dom"
import Header from "../components/Header"

const StudentProfile = () => {
  const { id } = useParams()
  const [student, setStudent] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [relatedStudents, setRelatedStudents] = useState([])

  useEffect(() => {
    const fetchStudent = async () => {
      try {
        setLoading(true)
        const response = await fetch(`http://127.0.0.1:8000/api/v1/profiles/${id}/`)
        if (!response.ok) {
          throw new Error("Студент не найден")
        }
        const data = await response.json()
        setStudent(data)

        const relatedResponse = await fetch(`http://127.0.0.1:8000/api/v1/profiles/?page_size=4`)
        if (relatedResponse.ok) {
          const relatedData = await relatedResponse.json()
          setRelatedStudents(relatedData.results.filter((s) => s.id !== Number.parseInt(id)).slice(0, 4))
        }
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    if (id) {
      fetchStudent()
    }
  }, [id])

  const getAvatarUrl = (avatarUrl) => {
    if (!avatarUrl) return "/professional-student-portrait.png"
    if (avatarUrl.startsWith("http")) return avatarUrl
    return `http://127.0.0.1:8000${avatarUrl}`
  }

  const getCourseColor = (course) => {
    const colors = {
      1: "from-blue-500 to-blue-600",
      2: "from-green-500 to-green-600",
      3: "from-purple-500 to-purple-600",
      4: "from-orange-500 to-orange-600",
      5: "from-red-500 to-red-600",
    }
    return colors[course] || "from-gray-500 to-gray-600"
  }

  const getSkillColor = (index) => {
    const colors = [
      "from-purple-500 to-pink-500",
      "from-blue-500 to-cyan-500",
      "from-green-500 to-emerald-500",
      "from-orange-500 to-yellow-500",
      "from-red-500 to-rose-500",
      "from-indigo-500 to-purple-500",
    ]
    return colors[index % colors.length]
  }

  const formatDate = (dateString) => {
    if (!dateString) return ""
    const date = new Date(dateString)
    return date.toLocaleDateString("ru-RU")
  }

  const calculateAge = (birthDate) => {
    if (!birthDate) return null
    const today = new Date()
    const birth = new Date(birthDate)
    let age = today.getFullYear() - birth.getFullYear()
    const monthDiff = today.getMonth() - birth.getMonth()
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--
    }
    return age
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Загрузка...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-red-400 text-xl">{error}</div>
      </div>
    )
  }

  if (!student) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Студент не найден</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <Header />

      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 mb-8 shadow-2xl">
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Avatar Section */}
            <div className="flex-shrink-0">
              <div className="relative">
                <div className="w-32 h-32 rounded-2xl overflow-hidden bg-gradient-to-br from-purple-500/20 to-pink-500/20 p-1">
                  <img
                    src={getAvatarUrl(student.avatar_url) || "/placeholder.svg"}
                    alt={student.full_name}
                    className="w-full h-full object-cover rounded-xl"
                  />
                </div>
                <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-2 border-slate-900"></div>
              </div>
            </div>

            {/* Main Info */}
            <div className="flex-1">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-4">
                  <h2 className="text-3xl font-bold text-white">{student.full_name}</h2>
                  <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-xs">✓</span>
                  </div>
                  {student.course && (
                    <span
                      className={`inline-flex items-center justify-center w-8 h-8 text-sm font-bold text-white rounded-full bg-gradient-to-r ${getCourseColor(student.course)}`}
                    >
                      {student.course}
                    </span>
                  )}
                </div>
              </div>

              <p className="text-xl text-slate-300 mb-2">{student.specialty}</p>

              <div className="flex items-center gap-4 text-slate-400 mb-4">
                {student.birth_date && <span>{calculateAge(student.birth_date)} лет</span>}
                {student.city && <span>г. {student.city}</span>}
              </div>

              {student.bio && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-white mb-2">Обо мне</h3>
                  <p className="text-slate-300 leading-relaxed">{student.bio}</p>
                </div>
              )}

              {student.skills && student.skills.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-white mb-3">Hard-скиллы (навыки)</h3>
                  <div className="flex flex-wrap gap-2">
                    {student.skills.map((skill, index) => (
                      <span
                        key={index}
                        className={`px-4 py-2 bg-gradient-to-r ${getSkillColor(index)} text-white text-sm rounded-full font-medium shadow-lg`}
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {student.portfolios && student.portfolios.length > 0 && (
          <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 mb-8 shadow-2xl">
            <h3 className="text-xl font-semibold text-white mb-6">Портфолио</h3>
            <div className="grid md:grid-cols-3 gap-4">
              {student.portfolios.map((portfolio, index) => {
                const gradients = [
                  "from-purple-600 to-blue-600",
                  "from-yellow-500 to-orange-500",
                  "from-green-500 to-teal-500",
                ]
                return (
                  <div
                    key={portfolio.id}
                    className={`bg-gradient-to-br ${gradients[index % gradients.length]} rounded-2xl p-6 text-white relative overflow-hidden`}
                  >
                    <div className="relative z-10">
                      <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center mb-4">
                        <span className="text-2xl">{index === 0 ? "🐙" : index === 1 ? "📊" : "🎨"}</span>
                      </div>
                      <h4 className="font-bold text-lg mb-2">{portfolio.title}</h4>
                      {portfolio.description && <p className="text-white/80 text-sm mb-4">{portfolio.description}</p>}
                      {portfolio.link && (
                        <a
                          href={portfolio.link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg text-sm transition-all"
                        >
                          Открыть проект →
                        </a>
                      )}
                    </div>
                    <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
                  </div>
                )
              })}
            </div>
          </div>
        )}

        {student.work_experiences && student.work_experiences.length > 0 && (
          <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 mb-8 shadow-2xl">
            <h3 className="text-xl font-semibold text-white mb-6">Опыт работы</h3>
            <div className="space-y-4">
              {student.work_experiences.map((work) => (
                <div key={work.id} className="bg-slate-700/30 rounded-2xl p-6 border border-slate-600/30">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h4 className="font-bold text-white text-lg">{work.position}</h4>
                      <p className="text-slate-300">{work.company}</p>
                      <p className="text-slate-400 text-sm">
                        {formatDate(work.start_date)} - {work.end_date ? formatDate(work.end_date) : "настоящее время"}
                      </p>
                    </div>
                    <div className="w-3 h-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"></div>
                  </div>
                  {work.description && <p className="text-slate-300 leading-relaxed">{work.description}</p>}
                </div>
              ))}
            </div>
          </div>
        )}

        {student.educations && student.educations.length > 0 && (
          <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 mb-8 shadow-2xl">
            <h3 className="text-xl font-semibold text-white mb-6">Образование</h3>
            <div className="space-y-4">
              {student.educations.map((education) => (
                <div key={education.id} className="bg-slate-700/30 rounded-2xl p-6 border border-slate-600/30">
                  <div className="flex items-start gap-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl flex items-center justify-center flex-shrink-0">
                      <span className="text-white text-xl">🎓</span>
                    </div>
                    <div>
                      <h4 className="font-bold text-white text-lg">{education.institution}</h4>
                      <p className="text-slate-300">{education.specialty?.name || education.specialty}</p>
                      <p className="text-slate-400 text-sm">
                        {education.start_year} - {education.end_year}
                      </p>
                      {education.additional_info && (
                        <p className="text-slate-400 text-sm mt-2">{education.additional_info}</p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 mb-8 shadow-2xl">
          <h3 className="text-xl font-semibold text-white mb-6">Связаться со студентом</h3>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="space-y-4">
              {student.phone_number && (
                <div className="flex items-center gap-4 p-4 bg-slate-700/30 rounded-xl">
                  <div className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center">
                    <span className="text-white">📞</span>
                  </div>
                  <span className="text-white">{student.phone_number}</span>
                </div>
              )}
              {student.email && (
                <div className="flex items-center gap-4 p-4 bg-slate-700/30 rounded-xl">
                  <div className="w-10 h-10 bg-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-white">✉️</span>
                  </div>
                  <span className="text-white">{student.email}</span>
                </div>
              )}
              {student.hh_link && (
                <a
                  href={student.hh_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-4 p-4 bg-slate-700/30 rounded-xl hover:bg-slate-700/50 transition-colors"
                >
                  <div className="w-10 h-10 bg-red-500 rounded-full flex items-center justify-center">
                    <span className="text-white">🔗</span>
                  </div>
                  <span className="text-white">HeadHunter профиль</span>
                </a>
              )}
            </div>

            <div className="bg-gradient-to-br from-purple-600/20 to-pink-600/20 rounded-2xl p-6">
              <h4 className="text-white font-semibold mb-4">Быстрое сообщение</h4>
              <div className="space-y-3">
                <button className="w-full text-left p-3 bg-white/10 hover:bg-white/20 rounded-lg text-white transition-colors">
                  Хочу пригласить на собеседование
                </button>
                <button className="w-full text-left p-3 bg-white/10 hover:bg-white/20 rounded-lg text-white transition-colors">
                  Расскажи о своих проектах
                </button>
                <button className="w-full text-left p-3 bg-white/10 hover:bg-white/20 rounded-lg text-white transition-colors">
                  Готов к стажировке?
                </button>
              </div>
              <button className="w-full mt-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white py-3 rounded-lg font-semibold hover:from-purple-600 hover:to-pink-600 transition-all">
                Связаться 💬
              </button>
            </div>
          </div>
        </div>

        {relatedStudents.length > 0 && (
          <div className="bg-gradient-to-br from-slate-800/80 to-slate-900/80 backdrop-blur-xl border border-slate-700/50 rounded-3xl p-8 shadow-2xl">
            <h3 className="text-xl font-semibold text-white mb-6">Студенты с похожими навыками</h3>
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {relatedStudents.map((relatedStudent) => (
                <Link
                  key={relatedStudent.id}
                  to={`/profile/${relatedStudent.id}`}
                  className="bg-slate-700/30 rounded-2xl p-4 border border-slate-600/30 hover:bg-slate-700/50 transition-all group"
                >
                  <div className="relative mb-4">
                    <div className="w-16 h-16 rounded-xl overflow-hidden bg-gradient-to-br from-purple-500/20 to-pink-500/20 mx-auto">
                      <img
                        src={getAvatarUrl(relatedStudent.avatar_url) || "/placeholder.svg"}
                        alt={relatedStudent.full_name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    {relatedStudent.course && (
                      <span
                        className={`absolute -top-1 -right-1 w-6 h-6 text-xs font-bold text-white rounded-full bg-gradient-to-r ${getCourseColor(relatedStudent.course)} flex items-center justify-center`}
                      >
                        {relatedStudent.course}
                      </span>
                    )}
                  </div>
                  <h4 className="font-semibold text-white text-center mb-1 group-hover:text-purple-300 transition-colors">
                    {relatedStudent.full_name}
                  </h4>
                  <p className="text-slate-400 text-sm text-center">{relatedStudent.specialty}</p>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default StudentProfile
