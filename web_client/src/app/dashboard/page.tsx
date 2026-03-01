'use client'

import { useState } from 'react'
import { Plus } from 'lucide-react'
import { FolderCode } from '@untitledui/icons'
import UploadModal from '@/components/UploadModal'

export default function DashboardPage() {
    const [isUploadModalOpen, setIsUploadModalOpen] = useState(false)

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 h-full flex flex-col">
            <div className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Your Projects</h1>
                    <p className="text-sm text-gray-500 mt-1">Manage your connected codebases and RAG contexts.</p>
                </div>
                <button
                    onClick={() => setIsUploadModalOpen(true)}
                    className="flex items-center gap-2 bg-[#7f56d9] hover:bg-[#6941c6] text-white px-4 py-2.5 rounded-lg text-sm font-medium shadow-sm transition-colors"
                >
                    <Plus className="w-4 h-4" />
                    New Project
                </button>
            </div>

            <div className="flex-1 bg-white border border-gray-200 rounded-xl shadow-sm text-center py-16 flex flex-col items-center justify-center">
                <div className="h-12 w-12 rounded-full bg-[#F4EBFF] flex items-center justify-center mb-4 ring-8 ring-[#F9F5FF]">
                    <FolderCode className="w-6 h-6 text-[#7F56D9]" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-1">No projects yet</h3>
                <p className="text-gray-500 text-sm max-w-sm mx-auto mb-6">
                    Upload your codebase folder or connect a GitHub repository to get started with an AI-enhanced workspace.
                </p>
                <button
                    onClick={() => setIsUploadModalOpen(true)}
                    className="flex items-center gap-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 px-4 py-2.5 rounded-lg text-sm font-medium shadow-sm transition-colors"
                >
                    <Plus className="w-4 h-4" />
                    Upload Project
                </button>
            </div>

            {isUploadModalOpen && (
                <UploadModal onClose={() => setIsUploadModalOpen(false)} />
            )}
        </div>
    )
}
