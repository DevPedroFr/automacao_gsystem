import './globals.css';
import Sidebar from '@/components/ui/Sidebar';

export const metadata = {
  title: 'CONSULTINGS APD Automation',
  description: 'Plataforma de prospecção consultiva e inteligência comercial',
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR" className="dark">
      <body className="flex min-h-screen bg-background text-gray-100 antialiased selection:bg-cyan-500/30">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-8 relative z-10">{children}</main>
      </body>
    </html>
  );
}
