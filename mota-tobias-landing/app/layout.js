import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

const playfair = Playfair_Display({
  variable: "--font-playfair",
  subsets: ["latin"],
});

export const metadata = {
  title: "Mota Tobias Advocacia Trabalhista em Mogi das Cruzes",
  description: "Atendimento claro, estratégico e responsável para orientar trabalhadores e empresas em demandas trabalhistas. Advocacia com forte reputação local e avaliação 5.0 no Google.",
};

export default function RootLayout({ children }) {
  return (
    <html
      lang="pt-BR"
      className={`${inter.variable} ${playfair.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
