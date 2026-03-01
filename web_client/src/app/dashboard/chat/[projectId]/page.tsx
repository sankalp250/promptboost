'use client'

import { useState, useRef, useEffect } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { useParams } from 'next/navigation'
import { Send01, MessageChatCircle, RefreshCcw02 } from '@untitledui/icons'
import { createClient } from '@/utils/supabase/client'

interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
    isReroll?: boolean
}

export default function ChatPage() {
    const params = useParams()
    const projectId = params.projectId as string
    const [messages, setMessages] = useState<Message[]>([])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [sessionId] = useState(() => uuidv4())
    const [userId, setUserId] = useState<string | null>(null)
    const messagesEndRef = useRef<HTMLDivElement>(null)

    useEffect(() => {
        const fetchUser = async () => {
            const supabase = createClient()
            const { data } = await supabase.auth.getUser()
            if (data.user) {
                setUserId(data.user.id)
            } else {
                // Fallback for missing anon keys
                setUserId(uuidv4())
            }
        }
        fetchUser()
    }, [])

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages, loading])

    const handleSend = async (content: string, isReroll = false) => {
        if (!content.trim() || !userId) return

        const newMessage: Message = { id: uuidv4(), role: 'user', content, isReroll }

        // Don't show reroll commands in the UI to keep it clean, only show the initial prompt
        if (!isReroll) {
            setMessages((prev) => [...prev, newMessage])
        }

        setInput('')
        setLoading(true)

        try {
            const apiBaseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

            const payload = {
                original_prompt: content,
                user_id: userId,
                session_id: sessionId,
                project_id: projectId,
                is_reroll: isReroll,
            }

            const response = await fetch(`${apiBaseURL}/enhance`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            })

            if (!response.ok) {
                throw new Error('Failed to enhance prompt')
            }

            const data = await response.json()

            const assistantMessage: Message = {
                id: uuidv4(),
                role: 'assistant',
                content: data.enhanced_prompt
            }

            setMessages((prev) => [...prev, assistantMessage])
        } catch (error: any) {
            setMessages((prev) => [...prev, { id: uuidv4(), role: 'assistant', content: `❌ Error: ${error.message}` }])
        } finally {
            setLoading(false)
        }
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend(input)
        }
    }

    const handleReroll = () => {
        // Find the last user message
        const lastUserMsg = [...messages].reverse().find(m => m.role === 'user')
        if (lastUserMsg) {
            handleSend(`Reroll this response to be better: ${lastUserMsg.content}`, true)
        }
    }

    return (
        <div className="flex flex-col h-[calc(100vh-4rem)] md:h-[calc(100vh-4rem)] lg:h-screen w-full bg-white relative">
            {/* Chat Header */}
            <div className="h-14 border-b border-gray-200 flex items-center px-6 shrink-0 bg-white/80 backdrop-blur-sm z-10 sticky top-0">
                <div className="flex items-center gap-3">
                    <div className="h-8 w-8 rounded bg-[#F4EBFF] flex items-center justify-center">
                        <MessageChatCircle className="w-4 h-4 text-[#7f56d9]" />
                    </div>
                    <div>
                        <h2 className="text-sm font-semibold text-gray-900">Project Workspace</h2>
                        <p className="text-xs text-gray-500">ID: {projectId} • Vector RAG Active</p>
                    </div>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
                {messages.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto">
                        <div className="h-16 w-16 mb-4 rounded-2xl bg-gradient-to-br from-[#7f56d9] to-[#9e77ed] flex items-center justify-center shadow-lg shadow-[#7f56d9]/20">
                            <MessageChatCircle className="w-8 h-8 text-white" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">How can I help you build?</h3>
                        <p className="text-gray-500 text-sm">
                            I have full access to your codebase via Vector DB RAG. Ask me to write a feature, refactor code, or explain how a specific component works.
                        </p>
                        <div className="mt-8 flex flex-wrap justify-center gap-2">
                            {['Explain the auth flow', 'Refactor the database models', 'Write a new Next.js component'].map((suggestion) => (
                                <button
                                    key={suggestion}
                                    onClick={() => setInput(suggestion)}
                                    className="text-xs font-medium px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-full text-gray-600 hover:bg-gray-100 transition-colors"
                                >
                                    {suggestion}
                                </button>
                            ))}
                        </div>
                    </div>
                ) : (
                    <div className="max-w-4xl mx-auto space-y-6 pb-4">
                        {messages.map((message) => (
                            <div key={message.id} className={`flex gap-4 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                {message.role === 'assistant' && (
                                    <div className="h-8 w-8 rounded bg-gradient-to-br from-[#7f56d9] to-[#9e77ed] shrink-0 flex items-center justify-center mt-1 shadow-sm">
                                        <div className="h-2 w-2 rounded-full bg-white shadow-inner"></div>
                                    </div>
                                )}
                                <div className={`flex flex-col gap-1 max-w-[85%] ${message.role === 'user' ? 'items-end' : 'items-start'}`}>
                                    <div className={`px-4 py-2.5 rounded-2xl text-[15px] leading-relaxed shadow-sm ${message.role === 'user'
                                            ? 'bg-[#7f56d9] text-white rounded-tr-sm'
                                            : 'bg-white border border-gray-200 text-gray-800 rounded-tl-sm'
                                        }`}>
                                        <div className="whitespace-pre-wrap">{message.content}</div>
                                    </div>
                                    {message.role === 'assistant' && (
                                        <button onClick={handleReroll} className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-[#7f56d9] transition-colors mt-1 ml-1 font-medium pb-4">
                                            <RefreshCcw02 className="w-3.5 h-3.5" />
                                            Reroll Response
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                        {loading && (
                            <div className="flex gap-4 justify-start">
                                <div className="h-8 w-8 rounded bg-gradient-to-br from-[#7f56d9] to-[#9e77ed] shrink-0 flex items-center justify-center mt-1 shadow-sm">
                                    <div className="h-2 w-2 rounded-full bg-white shadow-inner animate-pulse"></div>
                                </div>
                                <div className="px-4 py-3 bg-white border border-gray-200 rounded-2xl rounded-tl-sm shadow-sm flex items-center gap-1.5">
                                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></div>
                                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                    <div className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white border-t border-gray-200 shrink-0">
                <div className="max-w-4xl mx-auto relative flex items-end shadow-sm rounded-xl border border-gray-300 bg-white focus-within:ring-2 focus-within:ring-[#7f56d9]/20 focus-within:border-[#7f56d9] transition-all">
                    <textarea
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Message PromptBoost AI..."
                        className="w-full max-h-[200px] min-h-[52px] py-3.5 pl-4 pr-12 bg-transparent resize-none outline-none text-[15px] text-gray-900 placeholder:text-gray-400 my-auto"
                        rows={1}
                    />
                    <div className="absolute right-2 bottom-2">
                        <button
                            onClick={() => handleSend(input)}
                            disabled={loading || !input.trim()}
                            className={`h-9 w-9 rounded-lg flex items-center justify-center transition-colors ${input.trim() && !loading
                                    ? 'bg-[#7f56d9] hover:bg-[#6941c6] text-white shadow-sm'
                                    : 'bg-gray-100 text-gray-400'
                                }`}
                        >
                            <Send01 className="w-4 h-4" />
                        </button>
                    </div>
                </div>
                <p className="text-center text-[11px] text-gray-400 mt-2 font-medium">PromptBoost AI can make mistakes. Consider verifying important information.</p>
            </div>
        </div>
    )
}
