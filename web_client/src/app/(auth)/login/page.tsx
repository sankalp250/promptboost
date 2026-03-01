'use client'

import { useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { login, signup } from './actions'

export default function LoginPage() {
    const searchParams = useSearchParams()
    const error = searchParams.get('error')
    const initialView = searchParams.get('view') === 'signup' ? 'signup' : 'login'

    const [view, setView] = useState<'login' | 'signup'>(initialView)

    return (
        <div className="w-full flex justify-center items-center p-4">
            <div className="w-full max-w-[400px] flex flex-col items-center">

                {/* Mock Logo / Avatar */}
                <div className="mb-6 h-12 w-12 rounded-xl bg-gradient-to-br from-[#7f56d9] to-[#9e77ed] flex items-center justify-center shadow-lg shadow-[#7f56d9]/20 border border-white border-2">
                    <div className="h-4 w-4 rounded-full bg-white opacity-90 shadow-inner"></div>
                </div>

                {/* Headings */}
                <h1 className="text-3xl font-semibold text-gray-900 mb-2">
                    {view === 'login' ? 'Log in to your account' : 'Create an account'}
                </h1>
                <p className="text-gray-500 mb-8 text-center text-sm">
                    {view === 'login'
                        ? 'Welcome back! Please enter your details.'
                        : 'Start your 30-day free trial.'}
                </p>

                {/* Toggle Switch */}
                <div className="w-full flex bg-[#F9FAFB] p-1 rounded-lg border border-gray-200 mb-8">
                    <button
                        type="button"
                        onClick={() => setView('signup')}
                        className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${view === 'signup'
                                ? 'bg-white text-gray-900 shadow-sm border border-gray-200'
                                : 'text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        Sign up
                    </button>
                    <button
                        type="button"
                        onClick={() => setView('login')}
                        className={`flex-1 py-2 text-sm font-medium rounded-md transition-all ${view === 'login'
                                ? 'bg-white text-gray-900 shadow-sm border border-gray-200'
                                : 'text-gray-500 hover:text-gray-700'
                            }`}
                    >
                        Log in
                    </button>
                </div>

                {/* Form Error */}
                {error && (
                    <div className="w-full mb-4 p-3 bg-red-50 text-red-600 border border-red-200 rounded-lg text-sm">
                        {error}
                    </div>
                )}

                {/* Auth Form */}
                <form className="w-full flex flex-col gap-4">

                    {view === 'signup' && (
                        <div className="flex flex-col gap-1.5">
                            <label className="text-sm font-medium text-gray-700" htmlFor="name">Name</label>
                            <input
                                id="name"
                                name="name"
                                type="text"
                                placeholder="Enter your name"
                                className="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#7f56d9]/50 focus:border-[#7f56d9] placeholder:text-gray-400 placeholder:font-light"
                            />
                        </div>
                    )}

                    <div className="flex flex-col gap-1.5">
                        <label className="text-sm font-medium text-gray-700" htmlFor="email">Email</label>
                        <input
                            id="email"
                            name="email"
                            type="email"
                            required
                            placeholder="Enter your email"
                            className="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#7f56d9]/50 focus:border-[#7f56d9] placeholder:text-gray-400 placeholder:font-light"
                        />
                    </div>

                    <div className="flex flex-col gap-1.5">
                        <label className="text-sm font-medium text-gray-700" htmlFor="password">Password</label>
                        <input
                            id="password"
                            name="password"
                            type="password"
                            required
                            placeholder={view === 'login' ? '••••••••' : 'Create a password'}
                            className="w-full px-3.5 py-2.5 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-[#7f56d9]/50 focus:border-[#7f56d9] placeholder:text-gray-400 placeholder:font-light"
                        />
                    </div>

                    {view === 'login' && (
                        <div className="flex justify-between items-center mt-1">
                            <label className="flex items-center gap-2 cursor-pointer">
                                <input type="checkbox" className="w-4 h-4 rounded border-gray-300 text-[#7f56d9] focus:ring-[#7f56d9]" />
                                <span className="text-sm text-gray-700">Remember for 30 days</span>
                            </label>
                            <a href="#" className="text-sm font-medium text-[#7f56d9] hover:text-[#6941c6]">Forgot password</a>
                        </div>
                    )}

                    {view === 'signup' && (
                        <div className="flex flex-col gap-2 mt-1">
                            <label className="flex items-center gap-2">
                                <div className="w-4 h-4 rounded-full bg-[#E9D7FE] flex items-center justify-center">
                                    <svg width="10" height="10" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M10 3L4.5 8.5L2 6" stroke="#7F56D9" strokeWidth="1.6666" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                </div>
                                <span className="text-sm text-gray-600">Must be at least 8 characters</span>
                            </label>
                            <label className="flex items-center gap-2">
                                <div className="w-4 h-4 rounded-full bg-[#E9D7FE] flex items-center justify-center">
                                    <svg width="10" height="10" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <path d="M10 3L4.5 8.5L2 6" stroke="#7F56D9" strokeWidth="1.6666" strokeLinecap="round" strokeLinejoin="round" />
                                    </svg>
                                </div>
                                <span className="text-sm text-gray-600">Must contain one special character</span>
                            </label>
                        </div>
                    )}

                    <button
                        formAction={view === 'login' ? login : signup}
                        className="w-full mt-4 py-2.5 px-4 bg-[#7f56d9] hover:bg-[#6941c6] text-white font-medium rounded-lg shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#7f56d9]"
                    >
                        {view === 'login' ? 'Sign in' : 'Get started'}
                    </button>

                    <button
                        type="button"
                        className="w-full py-2.5 px-4 bg-white border border-gray-300 text-gray-700 font-medium rounded-lg shadow-sm hover:bg-gray-50 transition-colors flex justify-center items-center gap-3 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-200"
                    >
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M23.745 12.27c0-.79-.07-1.54-.19-2.27h-11.3v4.51h6.47c-.29 1.48-1.14 2.73-2.4 3.58v3h3.86c2.26-2.09 3.56-5.17 3.56-8.82Z" fill="#4285F4" />
                            <path d="M12.255 24c3.24 0 5.95-1.08 7.93-2.91l-3.86-3c-1.08.72-2.45 1.16-4.07 1.16-3.13 0-5.78-2.11-6.73-4.96h-3.98v3.09C3.515 21.3 7.565 24 12.255 24Z" fill="#34A853" />
                            <path d="M5.525 14.29c-.25-.72-.38-1.49-.38-2.29s.14-1.57.38-2.29V6.62h-3.98a11.86 11.86 0 0 0 0 10.76l3.98-3.09Z" fill="#FBBC05" />
                            <path d="M12.255 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C18.205 1.19 15.495 0 12.255 0 7.565 0 3.515 2.7 1.545 6.62l3.98 3.09c.95-2.85 3.6-4.96 6.73-4.96Z" fill="#EA4335" />
                        </svg>
                        Sign in with Google
                    </button>
                </form>

                {/* Footer text */}
                <p className="mt-8 text-sm text-gray-500 text-center">
                    {view === 'login' ? "Don't have an account? " : "Already have an account? "}
                    <button
                        type="button"
                        onClick={() => setView(view === 'login' ? 'signup' : 'login')}
                        className="font-semibold text-[#7f56d9] hover:text-[#6941c6]"
                    >
                        {view === 'login' ? 'Sign up' : 'Log in'}
                    </button>
                </p>
            </div>
        </div>
    )
}
