import './globals.css';
import Sidebar from '@/components/ui/Sidebar';

export const metadata = {
  title: 'Automação de Leads',
  description: 'Plataforma de prospecção consultiva e inteligência comercial',
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR" className="dark">
      <body className="flex min-h-screen bg-background text-gray-100 antialiased selection:bg-cyan-500/30">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-4 pb-24 md:p-8 print:p-0 print:pb-0 relative z-10 w-full">{children}</main>
      </body>
    </html>
  );
}
