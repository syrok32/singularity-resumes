// API integration for student data
const API_BASE_URL = "http://127.0.0.1:8000/api/v1"

export const fetchStudents = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/profiles/`)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data.results || []
  } catch (error) {
    console.error("Error fetching students:", error)
    throw error
  }
}

export const fetchStudentById = async (id) => {
  try {
    const response = await fetch(`${API_BASE_URL}/profiles/${id}/`)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error("Error fetching student:", error)
    throw error
  }
}

// Utility functions
export const getAvatarUrl = (avatarUrl) => {
  if (!avatarUrl) return "/professional-student-portrait.png"
  if (avatarUrl.startsWith("http")) return avatarUrl
  return `http://127.0.0.1:8000${avatarUrl}`
}

export const getCourseColor = (course) => {
  const colors = {
    1: "bg-blue-500",
    2: "bg-green-500",
    3: "bg-purple-500",
    4: "bg-orange-500",
    5: "bg-red-500",
  }
  return colors[course] || "bg-gray-500"
}
