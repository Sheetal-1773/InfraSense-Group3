import { Header } from './Header'

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-[#F7F7F7]">
      <Header />
      <main>
        {children}
      </main>
    </div>
  )
}