"use client"

import { useState, useEffect } from "react"
import Header from "../components/Header"

const StatsPage = () => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        const response = await fetch("http://127.0.0.1:8000/api/v1/stats/")

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }

        const data = await response.json()
        setStats(data)
      } catch (err) {
        console.error("Error fetching stats:", err)
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-lg">Загрузка статистики...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-red-400 text-lg">Ошибка: {error}</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <Header />

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="bg-slate-800/30 backdrop-blur-sm border border-slate-700/50 rounded-3xl p-8">
          <h1 className="text-3xl font-bold text-white mb-8">Статистика студентов</h1>

          {/* Overview Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700/30">
              <div className="text-2xl font-bold text-white mb-2">{stats?.total_students || 0}</div>
              <div className="text-slate-400">Всего студентов</div>
            </div>
            <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700/30">
              <div className="text-2xl font-bold text-purple-400 mb-2">{stats?.students_with_experience || 0}</div>
              <div className="text-slate-400">С опытом работы</div>
            </div>
            <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700/30">
              <div className="text-2xl font-bold text-pink-400 mb-2">{stats?.students_with_portfolio || 0}</div>
              <div className="text-slate-400">С портфолио</div>
            </div>
            <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700/30">
              <div className="text-2xl font-bold text-blue-400 mb-2">
                {Object.keys(stats?.by_specialty || {}).length}
              </div>
              <div className="text-slate-400">Специальностей</div>
            </div>
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* By Course */}
            <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700/30">
              <h3 className="text-xl font-semibold text-white mb-4">По курсам</h3>
              <div className="space-y-3">
                {Object.entries(stats?.by_course || {}).map(([course, count]) => (
                  <div key={course} className="flex items-center justify-between">
                    <span className="text-slate-300">{course} курс</span>
                    <div className="flex items-center gap-3">
                      <div className="w-32 bg-slate-700 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full"
                          style={{ width: `${(count / stats?.total_students) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-white font-medium w-8">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* By Specialty */}
            <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700/30">
              <h3 className="text-xl font-semibold text-white mb-4">По специальностям</h3>
              <div className="space-y-3">
                {Object.entries(stats?.by_specialty || {})
                  .slice(0, 6)
                  .map(([specialty, count]) => (
                    <div key={specialty} className="flex items-center justify-between">
                      <span className="text-slate-300 text-sm">{specialty}</span>
                      <div className="flex items-center gap-3">
                        <div className="w-24 bg-slate-700 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full"
                            style={{ width: `${(count / stats?.total_students) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-white font-medium w-8">{count}</span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>

            {/* By City */}
            <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700/30">
              <h3 className="text-xl font-semibold text-white mb-4">По городам</h3>
              <div className="space-y-3">
                {Object.entries(stats?.by_city || {})
                  .slice(0, 6)
                  .map(([city, count]) => (
                    <div key={city} className="flex items-center justify-between">
                      <span className="text-slate-300">{city}</span>
                      <div className="flex items-center gap-3">
                        <div className="w-24 bg-slate-700 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full"
                            style={{ width: `${(count / stats?.total_students) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-white font-medium w-8">{count}</span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>

            {/* Top Skills */}
            <div className="bg-slate-800/50 rounded-2xl p-6 border border-slate-700/30">
              <h3 className="text-xl font-semibold text-white mb-4">Популярные навыки</h3>
              <div className="space-y-3">
                {Object.entries(stats?.top_skills || {})
                  .slice(0, 8)
                  .map(([skill, count]) => (
                    <div key={skill} className="flex items-center justify-between">
                      <span className="text-slate-300 text-sm">{skill}</span>
                      <div className="flex items-center gap-3">
                        <div className="w-20 bg-slate-700 rounded-full h-2">
                          <div
                            className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full"
                            style={{ width: `${(count / stats?.total_students) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-white font-medium w-8">{count}</span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default StatsPage
