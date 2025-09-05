"use client"

import { useState, useEffect } from "react"
import StudentCard from "../components/StudentCard"
import Header from "../components/Header"

const StudentPage = () => {
  const [students, setStudents] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filterOptions, setFilterOptions] = useState({
    specialties: [],
    skills_by_category: {},
    courses: [],
    cities: [],
  })
  const [filters, setFilters] = useState({
    course: [],
    specialty: [],
    specialty_name: [],
    skills: [],
    skills_name: [],
    cities: [],
    over_18: null,
    search: "",
    has_experience: null,
    has_portfolio: null,
    is_active: null,
  })
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 5,
    total: 0,
  })
  const [showFilters, setShowFilters] = useState(false)
  const [viewMode, setViewMode] = useState("grid") // 'grid' or 'list'
  const [availableSkills, setAvailableSkills] = useState({})

  useEffect(() => {
    const fetchFilterOptions = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/v1/filter-options/")
        if (response.ok) {
          const data = await response.json()
          setFilterOptions(data)
          setAvailableSkills(data.skills_by_category)
        }
      } catch (err) {
        console.error("Error fetching filter options:", err)
      }
    }
    fetchFilterOptions()
  }, [])

  useEffect(() => {
    if (filters.specialty.length > 0) {
      const filteredSkills = {}
      Object.entries(filterOptions.skills_by_category).forEach(([category, skills]) => {
        const relevantSkills = skills.filter((skill) =>
          filters.specialty.some(
            (specialtyId) => skill.specialties && skill.specialties.includes(Number.parseInt(specialtyId)),
          ),
        )
        if (relevantSkills.length > 0) {
          filteredSkills[category] = relevantSkills
        }
      })
      setAvailableSkills(filteredSkills)
    } else {
      setAvailableSkills(filterOptions.skills_by_category)
    }
  }, [filters.specialty, filterOptions.skills_by_category])

  const fetchStudents = async (page = 1, pageSize = 5) => {
    try {
      setLoading(true)
      const params = new URLSearchParams()

      if (filters.course.length) params.append("course", filters.course.join(","))
      if (filters.specialty.length) params.append("specialty", filters.specialty.join(","))
      if (filters.skills.length) params.append("skills", filters.skills.join(","))
      if (filters.cities.length) params.append("cities", filters.cities.join(","))
      if (filters.search) params.append("search", filters.search)
      if (filters.has_experience !== null) params.append("has_experience", filters.has_experience.toString())
      if (filters.has_portfolio !== null) params.append("has_portfolio", filters.has_portfolio.toString())
      if (filters.is_active !== null) params.append("is_active", filters.is_active.toString())
      if (filters.over_18 !== null) params.append("over_18", filters.over_18.toString())
      params.append("page", page)
      params.append("page_size", pageSize)

      const response = await fetch(`http://127.0.0.1:8000/api/v1/profiles/?${params.toString()}`)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setStudents(data.results || [])
      setPagination((prev) => ({
        ...prev,
        current: page,
        pageSize: pageSize,
        total: data.count || 0,
      }))
    } catch (err) {
      console.error("Error fetching students:", err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStudents(pagination.current, pagination.pageSize)
  }, [filters])

  const applyFilters = () => {
    setPagination((prev) => ({ ...prev, current: 1 }))
    fetchStudents(1, pagination.pageSize)
  }

  const resetFilters = () => {
    setFilters({
      course: [],
      specialty: [],
      specialty_name: [],
      skills: [],
      skills_name: [],
      cities: [],
      over_18: null,
      search: "",
      has_experience: null,
      has_portfolio: null,
      is_active: null,
    })
  }

  const handlePageChange = (page) => {
    fetchStudents(page, pagination.pageSize)
  }

  const handlePageSizeChange = (pageSize) => {
    fetchStudents(1, pageSize)
  }

  const handleSpecialtyChange = (e) => {
    const selectedIds = Array.from(e.target.selectedOptions, (option) => option.value)
    const selectedNames = Array.from(e.target.selectedOptions, (option) => option.text)

    setFilters((prev) => ({
      ...prev,
      specialty: selectedIds,
      specialty_name: selectedNames,
      skills: [],
      skills_name: [],
    }))
  }

  const handleSkillChange = (skillId, skillName, checked) => {
    if (checked) {
      setFilters((prev) => ({
        ...prev,
        skills: [...prev.skills, skillId],
        skills_name: [...prev.skills_name, skillName],
      }))
    } else {
      setFilters((prev) => ({
        ...prev,
        skills: prev.skills.filter((s) => s !== skillId),
        skills_name: prev.skills_name.filter((s) => s !== skillName),
      }))
    }
  }

  if (loading && students.length === 0) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-lg">Загрузка студентов...</div>
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
      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-slate-800/30 backdrop-blur-sm border border-slate-700/50 rounded-3xl p-8">
          {/* Page Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setViewMode("list")}
                  className={`p-2 rounded-lg border border-slate-600/30 ${viewMode === "list" ? "bg-purple-500" : "bg-slate-700/50"}`}
                >
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 6h16M4 10h16M4 14h16M4 18h16"
                    />
                  </svg>
                </button>
                <button
                  onClick={() => setViewMode("grid")}
                  className={`p-2 rounded-lg ${viewMode === "grid" ? "bg-purple-500" : "bg-slate-700/50 border border-slate-600/30"}`}
                >
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"
                    />
                  </svg>
                </button>
              </div>
              <h1 className="text-2xl font-bold text-white">Студенты</h1>
              <span className="text-slate-400 text-sm">({pagination.total} найдено)</span>
            </div>

            <button
              onClick={() => setShowFilters(!showFilters)}
              className="px-6 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full font-medium hover:from-purple-600 hover:to-pink-600 transition-all duration-200 flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
                />
              </svg>
              Фильтр
            </button>
          </div>

          {showFilters && (
            <div className="bg-slate-800/50 rounded-2xl p-6 mb-8 border border-slate-700/30">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Курс</label>
                  <select
                    multiple
                    value={filters.course}
                    onChange={(e) =>
                      setFilters((prev) => ({
                        ...prev,
                        course: Array.from(e.target.selectedOptions, (option) => option.value),
                      }))
                    }
                    className="w-full bg-slate-700 text-white rounded-lg border border-slate-600 p-2 focus:border-purple-500 focus:outline-none"
                  >
                    {filterOptions.courses.map((course) => (
                      <option key={course.value} value={course.value}>
                        {course.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Специальность</label>
                  <select
                    multiple
                    value={filters.specialty}
                    onChange={handleSpecialtyChange}
                    className="w-full bg-slate-700 text-white rounded-lg border border-slate-600 p-2 focus:border-purple-500 focus:outline-none"
                  >
                    {filterOptions.specialties.map((specialty) => (
                      <option key={specialty.id} value={specialty.id}>
                        {specialty.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">Город</label>
                  <select
                    multiple
                    value={filters.cities}
                    onChange={(e) =>
                      setFilters((prev) => ({
                        ...prev,
                        cities: Array.from(e.target.selectedOptions, (option) => option.value),
                      }))
                    }
                    className="w-full bg-slate-700 text-white rounded-lg border border-slate-600 p-2 focus:border-purple-500 focus:outline-none"
                  >
                    {filterOptions.cities.map((city) => (
                      <option key={city.value} value={city.value}>
                        {city.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-300 mb-2">Навыки</label>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
                  {Object.entries(availableSkills).map(([category, skills]) => (
                    <div key={category}>
                      <div className="text-xs text-slate-400 mb-1">{category}</div>
                      {skills.map((skill) => (
                        <label key={skill.id} className="flex items-center text-sm text-slate-300 mb-1">
                          <input
                            type="checkbox"
                            checked={filters.skills.includes(skill.id)}
                            onChange={(e) => handleSkillChange(skill.id, skill.name, e.target.checked)}
                            className="mr-2 rounded border-slate-600 bg-slate-700 text-purple-500 focus:ring-purple-500"
                          />
                          {skill.name}
                        </label>
                      ))}
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex flex-wrap gap-4 mb-4">
                <label className="flex items-center text-slate-300">
                  <input
                    type="checkbox"
                    checked={filters.over_18 === true}
                    onChange={(e) =>
                      setFilters((prev) => ({
                        ...prev,
                        over_18: e.target.checked ? true : null,
                      }))
                    }
                    className="mr-2 rounded border-slate-600 bg-slate-700 text-purple-500 focus:ring-purple-500"
                  />
                  Старше 18 лет
                </label>
                <label className="flex items-center text-slate-300">
                  <input
                    type="checkbox"
                    checked={filters.has_experience === true}
                    onChange={(e) =>
                      setFilters((prev) => ({
                        ...prev,
                        has_experience: e.target.checked ? true : null,
                      }))
                    }
                    className="mr-2 rounded border-slate-600 bg-slate-700 text-purple-500 focus:ring-purple-500"
                  />
                  С опытом работы
                </label>
                <label className="flex items-center text-slate-300">
                  <input
                    type="checkbox"
                    checked={filters.has_portfolio === true}
                    onChange={(e) =>
                      setFilters((prev) => ({
                        ...prev,
                        has_portfolio: e.target.checked ? true : null,
                      }))
                    }
                    className="mr-2 rounded border-slate-600 bg-slate-700 text-purple-500 focus:ring-purple-500"
                  />
                  С портфолио
                </label>
                <label className="flex items-center text-slate-300">
                  <input
                    type="checkbox"
                    checked={filters.is_active === true}
                    onChange={(e) =>
                      setFilters((prev) => ({
                        ...prev,
                        is_active: e.target.checked ? true : null,
                      }))
                    }
                    className="mr-2 rounded border-slate-600 bg-slate-700 text-purple-500 focus:ring-purple-500"
                  />
                  Активный
                </label>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={applyFilters}
                  className="px-4 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors"
                >
                  Применить
                </button>
                <button
                  onClick={resetFilters}
                  className="px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-500 transition-colors"
                >
                  Сбросить
                </button>
              </div>
            </div>
          )}

          <div className="space-y-6">
            {loading && <div className="text-center text-slate-400 py-8">Загрузка...</div>}
            {!loading && students.length === 0 && (
              <div className="text-center text-slate-400 py-8">Студенты не найдены</div>
            )}
            {students.map((student) => (
              <StudentCard key={student.id} student={student} />
            ))}
          </div>

          {pagination.total > pagination.pageSize && (
            <div className="flex items-center justify-between mt-8 pt-6 border-t border-slate-700/50">
              <div className="text-slate-400 text-sm">
                Показано {(pagination.current - 1) * pagination.pageSize + 1}-
                {Math.min(pagination.current * pagination.pageSize, pagination.total)} из {pagination.total}
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => handlePageChange(pagination.current - 1)}
                  disabled={pagination.current === 1}
                  className="px-3 py-1 bg-slate-700 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-600"
                >
                  Назад
                </button>

                <div className="flex gap-1">
                  {Array.from({ length: Math.ceil(pagination.total / pagination.pageSize) }, (_, i) => i + 1)
                    .filter(
                      (page) =>
                        page === 1 ||
                        page === Math.ceil(pagination.total / pagination.pageSize) ||
                        Math.abs(page - pagination.current) <= 2,
                    )
                    .map((page, index, array) => (
                      <div key={page}>
                        {index > 0 && array[index - 1] !== page - 1 && <span className="px-2 text-slate-400">...</span>}
                        <button
                          onClick={() => handlePageChange(page)}
                          className={`px-3 py-1 rounded ${
                            page === pagination.current
                              ? "bg-purple-500 text-white"
                              : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                          }`}
                        >
                          {page}
                        </button>
                      </div>
                    ))}
                </div>

                <button
                  onClick={() => handlePageChange(pagination.current + 1)}
                  disabled={pagination.current === Math.ceil(pagination.total / pagination.pageSize)}
                  className="px-3 py-1 bg-slate-700 text-white rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-600"
                >
                  Далее
                </button>
              </div>

              <select
                value={pagination.pageSize}
                onChange={(e) => handlePageSizeChange(Number(e.target.value))}
                className="bg-slate-700 text-white rounded border border-slate-600 px-2 py-1"
              >
                <option value={5}>5 на странице</option>
                <option value={10}>10 на странице</option>
                <option value={20}>20 на странице</option>
              </select>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/50 bg-slate-900/80 backdrop-blur-sm mt-16">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-slate-400 text-sm mb-2">Телефон</div>
              <div className="text-white font-medium">+7 (996) 644-39-38</div>
            </div>

            <div className="text-center">
              <div className="text-slate-400 text-sm mb-2">Главная</div>
              <div className="text-slate-400 text-sm">О нас</div>
            </div>

            <div className="flex flex-col items-end gap-4">
              <div className="text-white font-bold text-xl">
                <span className="bg-white text-slate-900 px-2 py-1 text-sm font-bold">resume</span>
              </div>
              <div className="text-slate-400 font-medium">Singularity</div>
              <div className="text-slate-400 font-medium">skyeng</div>
            </div>
          </div>

          <div className="flex items-center gap-4 mt-6">
            <div className="text-slate-400 text-sm">Контакты</div>
            <div className="flex gap-2">
              <button className="p-2 bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors">
                <svg className="w-5 h-5 text-slate-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.024-.105-.949-.199-2.403.041-3.439.219-.937 1.404-5.965 1.404-5.965s-.359-.72-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.097.118.112.221.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.402.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.357-.629-2.748-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24.009 12.017 24.009c6.624 0 11.99-5.367 11.99-12.014C24.007 5.36 18.641.001 12.017.001z" />
                </svg>
              </button>
              <button className="p-2 bg-slate-800 rounded-lg hover:bg-slate-700 transition-colors">
                <svg className="w-5 h-5 text-slate-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.890-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.488" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default StudentPage
