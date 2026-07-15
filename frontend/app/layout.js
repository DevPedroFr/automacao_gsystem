import './globals.css';
import Sidebar from '@/components/ui/Sidebar';

export const metadata = {
  title: 'CONSULTINGS APD Automation',
  description: 'Plataforma de prospecção consultiva e inteligência comercial',
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body className="flex min-h-screen bg-surface-100">
        <Sidebar />
        <main className="flex-1 overflow-y-auto p-8">{children}</main>
      </body>
    </html>
  );
}
