import { createClient } from '@/utils/supabase/server'
import { redirect } from 'next/navigation'
import { LogOut01, Settings01, HomeLine } from '@untitledui/icons'

export default async function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const supabase = await createClient()
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
        redirect('/login')
    }

    return (
        <div className="flex h-screen bg-gray-50 flex-col md:flex-row">
            {/* Sidebar Desktop */}
            <aside className="hidden md:flex flex-col w-64 bg-white border-r border-gray-200 h-full">
                <div className="h-16 flex items-center px-6 border-b border-gray-100">
                    <div className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-[#7f56d9] to-[#9e77ed] flex items-center justify-center shadow-sm">
                            <div className="h-2.5 w-2.5 rounded-full bg-white shadow-inner"></div>
                        </div>
                        <span className="font-semibold text-gray-900 text-lg">PromptBoost</span>
                    </div>
                </div>

                <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
                    <a href="/dashboard" className="flex items-center gap-3 px-3 py-2 bg-gray-50 text-gray-900 rounded-md font-medium text-sm">
                        <HomeLine className="w-5 h-5 text-gray-500" />
                        Projects
                    </a>
                    <a href="/dashboard/settings" className="flex items-center gap-3 px-3 py-2 text-gray-700 hover:bg-gray-50 rounded-md font-medium text-sm transition-colors">
                        <Settings01 className="w-5 h-5 text-gray-500" />
                        Settings
                    </a>
                </nav>

                <div className="p-4 border-t border-gray-200">
                    <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold border border-indigo-200">
                            {user.email?.charAt(0).toUpperCase()}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-gray-900 truncate">User</p>
                            <p className="text-sm text-gray-500 truncate">{user.email}</p>
                        </div>
                    </div>
                    <form action="/auth/signout" method="post">
                        <button className="mt-4 w-full flex items-center justify-center gap-2 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50">
                            <LogOut01 className="w-4 h-4" />
                            Sign out
                        </button>
                    </form>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-y-auto">
                {/* Mobile Header */}
                <div className="md:hidden h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4">
                    <div className="flex items-center gap-2">
                        <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-[#7f56d9] to-[#9e77ed] flex items-center justify-center shadow-sm">
                            <div className="h-2.5 w-2.5 rounded-full bg-white shadow-inner"></div>
                        </div>
                        <span className="font-semibold text-gray-900">PromptBoost</span>
                    </div>
                    <div className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 font-bold border border-indigo-200">
                        {user.email?.charAt(0).toUpperCase()}
                    </div>
                </div>

                <div className="h-full">
                    {children}
                </div>
            </main>
        </div>
    )
}
