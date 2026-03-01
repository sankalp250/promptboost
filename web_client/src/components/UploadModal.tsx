'use client'

import { useState } from 'react'
import { UploadCloud02 } from '@untitledui/icons'
import { useRouter } from 'next/navigation'

interface UploadModalProps {
    onClose: () => void
}

export default function UploadModal({ onClose }: UploadModalProps) {
    const router = useRouter()
    const [file, setFile] = useState<File | null>(null)
    const [uploading, setUploading] = useState(false)
    const [projectId, setProjectId] = useState('')
    const [message, setMessage] = useState('')

    const handleUpload = async () => {
        if (!file || !projectId) {
            setMessage("Please provide a Project ID and a ZIP file.")
            return
        }

        setUploading(true)
        setMessage("Uploading... this may take a moment.")

        try {
            const formData = new FormData()
            formData.append("project_id", projectId)
            formData.append("file", file)

            const apiBaseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'
            const response = await fetch(`${apiBaseURL}/project/upload`, {
                method: "POST",
                body: formData,
            })

            if (response.ok) {
                setMessage("✅ Upload successful! Redirecting to chat...")
                setTimeout(() => {
                    onClose()
                    router.push(`/dashboard/chat/${projectId}`)
                }, 1500)
            } else {
                const errorData = await response.json()
                setMessage(`❌ Upload failed: ${errorData.detail || 'Server logic error'}`)
            }
        } catch (err: any) {
            setMessage(`❌ Network error: ${err.message}`)
        } finally {
            setUploading(false)
        }
    }

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-xl shadow-xl w-full max-w-md p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-2">Upload Codebase</h2>
                <p className="text-sm text-gray-500 mb-6">Compress your project folder into a .zip file and upload it here.</p>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Project ID</label>
                        <input
                            type="text"
                            value={projectId}
                            onChange={(e) => setProjectId(e.target.value)}
                            placeholder="e.g. promptboost-v1"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#7f56d9] focus:border-[#7f56d9] outline-none"
                        />
                    </div>

                    <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 flex flex-col items-center justify-center bg-gray-50 hover:bg-gray-100 transition-colors">
                        <div className="h-10 w-10 rounded-full bg-gray-200 flex items-center justify-center mb-3">
                            <UploadCloud02 className="w-5 h-5 text-gray-600" />
                        </div>
                        <p className="text-sm font-medium text-gray-700">Click to upload or drag and drop</p>
                        <p className="text-xs text-gray-500 mt-1">ZIP folder containing your code (Max 50MB)</p>
                        <input
                            type="file"
                            accept=".zip"
                            onChange={(e) => setFile(e.target.files?.[0] || null)}
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                            title="Upload ZIP"
                        />
                    </div>

                    {file && (
                        <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg flex items-center">
                            <span className="text-sm text-gray-700 font-medium truncate">{file.name}</span>
                        </div>
                    )}

                    {message && (
                        <p className={`text-sm font-medium ${message.includes('❌') ? 'text-red-600' : 'text-green-600'}`}>{message}</p>
                    )}

                </div>

                <div className="mt-6 flex gap-3">
                    <button
                        onClick={onClose}
                        disabled={uploading}
                        className="flex-1 py-2 px-4 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleUpload}
                        disabled={uploading || !file || !projectId}
                        className="flex-1 py-2 px-4 bg-[#7f56d9] disabled:bg-indigo-300 hover:bg-[#6941c6] text-white rounded-lg font-medium transition"
                    >
                        {uploading ? 'Uploading...' : 'Confirm Upload'}
                    </button>
                </div>
            </div>
        </div>
    )
}
