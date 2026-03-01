export default function AuthLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <div className="flex min-h-screen flex-col items-center justify-center p-4 bg-white relative overflow-hidden">
            {/* Background Grid Pattern (Untitled UI style) */}
            <div
                className="absolute inset-0 z-0 opacity-[0.03] pointer-events-none"
                style={{ backgroundImage: 'linear-gradient(#000 1px, transparent 1px), linear-gradient(90deg, #000 1px, transparent 1px)', backgroundSize: '40px 40px' }}
            ></div>

            <div className="z-10 w-full max-w-md bg-white">
                {children}
            </div>
        </div>
    )
}
