import { Scale, FileText, Briefcase, Clock, ShieldAlert, Building2 } from 'lucide-react';

const services = [
  {
    title: 'Direito Trabalhista',
    description: 'Orientação completa e estratégica sobre direitos e deveres na relação de emprego.',
    icon: Scale,
  },
  {
    title: 'Reclamações trabalhistas',
    description: 'Atuação responsável na defesa de seus direitos ou na representação de sua empresa.',
    icon: FileText,
  },
  {
    title: 'Rescisões e verbas trabalhistas',
    description: 'Análise detalhada de cálculos e orientações sobre os valores devidos na demissão.',
    icon: Briefcase,
  },
  {
    title: 'Horas extras',
    description: 'Acompanhamento e reivindicação de jornada de trabalho excedente não remunerada.',
    icon: Clock,
  },
  {
    title: 'Assédio moral',
    description: 'Apoio jurídico e orientação clara em situações de abuso no ambiente de trabalho.',
    icon: ShieldAlert,
  },
  {
    title: 'Consultoria preventiva',
    description: 'Orientação focada para empresas que buscam adequação à legislação trabalhista.',
    icon: Building2,
  },
];

export default function Services() {
  return (
    <section id="atuacao" className="py-24 bg-[var(--color-gray-light)]">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-serif text-[var(--color-navy)] mb-6">
            Áreas de atuação
          </h2>
          <p className="text-lg text-gray-600 font-sans">
            Conheça nossas frentes de atuação para defender seus direitos com responsabilidade.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {services.map((service, index) => (
            <div 
              key={index}
              className="group rounded-2xl bg-white border border-gray-100 p-8 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300"
            >
              <div className="h-14 w-14 rounded-2xl bg-[var(--color-navy)]/5 text-[var(--color-navy)] flex items-center justify-center mb-6 group-hover:bg-[var(--color-navy)] group-hover:text-[var(--color-gold)] transition-colors duration-300">
                <service.icon className="h-7 w-7" />
              </div>
              <h3 className="text-xl font-serif text-[var(--color-navy)] mb-3">
                {service.title}
              </h3>
              <p className="text-gray-600 leading-relaxed font-sans">
                {service.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
