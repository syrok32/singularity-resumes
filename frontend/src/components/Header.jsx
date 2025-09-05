"use client"

import { Link, useLocation } from "react-router-dom"
import { useState } from "react"

const Header = () => {
  const location = useLocation()
  const [searchQuery, setSearchQuery] = useState("")

  return (
    <header className="border-b border-slate-800/50 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <nav className="flex items-center space-x-8">
            <Link
              to="/"
              className={`transition-colors font-medium ${
                location.pathname === "/" ? "text-white" : "text-slate-300 hover:text-white"
              }`}
            >
              ГЛАВНАЯ
            </Link>
            <Link
              to="/"
              className={`transition-colors font-medium ${
                location.pathname === "/" ? "text-white" : "text-slate-300 hover:text-white"
              }`}
            >
              О СТУДЕНТАХ
            </Link>
            <Link
              to="/stats"
              className={`transition-colors font-medium ${
                location.pathname === "/stats" ? "text-white" : "text-slate-300 hover:text-white"
              }`}
            >
              СТАТИСТИКА
            </Link>
          </nav>

          <div className="flex items-center">
            <div className="text-white font-bold text-xl">
              <span className="text-purple-400">singularity</span>
              <span className="bg-white text-slate-900 px-2 py-1 ml-2 text-sm font-bold">resume</span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <Link to="/" className="text-slate-300 hover:text-white transition-colors font-medium">
              НАЙТИ СТАЖЕРА
            </Link>
            <div className="relative">
              <input
                type="text"
                placeholder="Поиск студентов..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="bg-slate-800 text-white px-4 py-2 pl-10 rounded-lg border border-slate-600 focus:border-purple-500 focus:outline-none"
              />
              <svg
                className="w-5 h-5 text-slate-400 absolute left-3 top-2.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
