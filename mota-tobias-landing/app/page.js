import Header from './components/Header';
import Hero from './components/Hero';
import Reputation from './components/Reputation';
import Services from './components/Services';
import About from './components/About';
import FAQ from './components/FAQ';
import CTA from './components/CTA';
import Footer from './components/Footer';

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-light text-text-dark selection:bg-gold/30">
      <Header />
      <Hero />
      <Reputation />
      <Services />
      <About />
      <FAQ />
      <CTA />
      <Footer />
    </main>
  );
}
