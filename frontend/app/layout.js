import './globals.css';
import Sidebar from '@/components/ui/Sidebar';

export const metadata = {
  title: 'Automação de Leads',
  description: 'Plataforma de prospecção consultiva e inteligência comercial',
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR" className="dark">
      <body className="flex min-h-screen overflow-x-hidden bg-background text-gray-100 antialiased">
        <Sidebar />
        <main className="relative z-10 min-w-0 w-full flex-1 overflow-y-auto p-4 pb-24 sm:p-6 md:p-8 2xl:px-12 print:p-0 print:pb-0">
          {children}
        </main>
      </body>
    </html>
  );
}
