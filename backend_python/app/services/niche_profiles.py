"""
Módulo de Inteligência de Nichos e Arquitetura de Prompts para Criação de Sites.
Contém perfis de design, paletas cromáticas (HEX), psicologia de cores,
serviços específicos e engenharia de prompts de alta conversão para o Google Stitch / AI Site Builders.
"""
from typing import Optional, Dict, Any, List
import urllib.parse
from app.models.lead import LeadResult
from app.models.diagnosis import DiagnosisResult


NICHE_PROFILES: Dict[str, Dict[str, Any]] = {
    "odonto": {
        "niche_id": "odonto",
        "niche_pt": "Clínica Odontológica & Estética Dental",
        "industry_en": "High-End Modern Dental Clinic & Aesthetic Dentistry",
        "target_audience": "Pacientes que buscam alinhadores invisíveis, implantes dentários, estética do sorriso e atendimento sem dor com hora marcada.",
        "color_palette": {
            "primary": "#0D9488",       # Teal / Verde Água Sofisticado
            "secondary": "#0F172A",     # Slate / Grafite Profundo
            "accent": "#0284C7",        # Cyan Confiável (Botão CTA)
            "background": "#FFFFFF",    # Branco Puro Clean
            "surface": "#F0FDFA",       # Menta Suave
            "text": "#0F172A",
        },
        "typography": {
            "headings": "Plus Jakarta Sans, sans-serif",
            "body": "Inter, sans-serif",
            "style_notes": "Clean, ultra-crisp, reassuring medical aesthetic with generous white space and soft rounded corners (rounded-2xl)."
        },
        "core_services": [
            {"name": "Implantes Dentários Guiados e Próteses Fixas", "benefit": "Recupere 100% da segurança para mastigar e sorrir em poucas sessões com planejamento digital 3D."},
            {"name": "Alinhadores Invisíveis e Ortodontia Digital", "benefit": "Dentes alinhados com tecnologia invisível, sem bráquetes de metal e com visitas rápidas."},
            {"name": "Facetas e Lentes de Contato em Porcelana", "benefit": "Transformação estética com acabamento ultra natural, desenhada sob medida para seu rosto."},
            {"name": "Clareamento a Laser Avançado", "benefit": "Dentes notavelmente mais brancos com protocolo seguro que preserva a sensibilidade dental."},
            {"name": "Harmonização Orofacial e Estética", "benefit": "Equilíbrio e rejuvenescimento facial sutil realizado por cirurgiões-dentistas certificados."},
            {"name": "Odontopediatria e Prevenção Familiar", "benefit": "Atendimento lúdico e sem traumas para crianças, garantindo saúde bucal desde os primeiros anos."},
        ],
        "pain_points": [
            "Medo ou fobia de dor durante anestesia e procedimentos",
            "Insegurança para sorrir ou mastigar em público",
            "Orçamentos confusos e tratamentos que parecem não ter fim",
        ],
        "value_triggers": [
            "Scanner 3D Intraoral sem moldagens desconfortáveis",
            "Atendimento humanizado e rigorosamente pontual",
            "Corpo clínico multidisciplinar com pós-graduação e mestrado",
            "Condições facilitadas de parcelamento em até 12x",
        ],
        "sample_headline": "O Sorriso que Você Sempre Sonhou, com a Tecnologia e o Cuidado que Você Merece.",
        "sample_subheadline": "Tratamentos modernos com planejamento digital 3D e atendimento sem dor em consultório humanizado.",
    },

    "medicina": {
        "niche_id": "medicina",
        "niche_pt": "Clínica Médica & Centro de Especialidades de Saúde",
        "industry_en": "Specialized Medical Clinic & Healthcare Center",
        "target_audience": "Pacientes que buscam atendimento médico humanizado, diagnósticos precisos, corpo clínico renomado e agilidade.",
        "color_palette": {
            "primary": "#0F2744",       # Navy Corporativo / Médico
            "secondary": "#0284C7",     # Azul Céu Tecnológico
            "accent": "#10B981",        # Esmeralda Vitalidade (CTA)
            "background": "#FFFFFF",    # Branco Puro
            "surface": "#F8FAFC",       # Slate 50 Suave
            "text": "#1E293B",
        },
        "typography": {
            "headings": "Plus Jakarta Sans, sans-serif",
            "body": "Inter, sans-serif",
            "style_notes": "Authoritative, serene, clinical excellence with high contrast and readable typography for all age demographics."
        },
        "core_services": [
            {"name": "Consultas Especializadas e Check-up Preventivo", "benefit": "Avaliação detalhada com médicos especialistas focados na raiz do seu bem-estar."},
            {"name": "Exames Diagnósticos com Resultados Ágeis", "benefit": "Equipamentos de última geração para laudos precisos e rápidos sem filas."},
            {"name": "Acompanhamento Contínuo e Medicina Integrada", "benefit": "Planos terapêuticos personalizados unindo diferentes especialidades em um só lugar."},
            {"name": "Telemedicina e Atendimento com Hora Marcada", "benefit": "Conveniência de consultas online seguras ou presenciais sem espera na recepção."},
        ],
        "pain_points": [
            "Atrasos constantes em salas de espera lotadas",
            "Consultas impessoais de 5 minutos sem escuta atenta",
            "Dificuldade de encontrar múltiplos especialistas em um mesmo local",
        ],
        "value_triggers": [
            "Médicos com RQE e títulos de especialista reconhecidos",
            "Estrutura moderna com acessibilidade total e estacionamento",
            "Pontualidade rigorosa e agendamento digital descomplicado",
            "Atendimento humanizado do pré ao pós-consulta",
        ],
        "sample_headline": "Sua Saúde em Boas Mãos: Medicina de Precisão com Atendimento Genuinamente Humano.",
        "sample_subheadline": "Especialistas qualificados, diagnósticos rápidos e infraestrutura de ponta focada no seu bem-estar integral.",
    },

    "advocacia": {
        "niche_id": "advocacia",
        "niche_pt": "Escritório de Advocacia & Consultoria Jurídica",
        "industry_en": "Premier Legal Practice & Strategic Law Firm",
        "target_audience": "Pessoas físicas e empresas buscando defesa combativa, blindagem jurídica, sigilo e soluções ágeis para conflitos legais.",
        "color_palette": {
            "primary": "#0A1128",       # Midnight Navy Solene
            "secondary": "#C5A880",     # Ouro Champagne / Bronze Nobre
            "accent": "#1E3A8A",        # Azul Real Profundo
            "background": "#FDFBF7",    # Marfim Warm Premium
            "surface": "#FFFFFF",       # Branco Puro
            "text": "#1E293B",
        },
        "typography": {
            "headings": "Cinzel / Playfair Display, serif",
            "body": "Plus Jakarta Sans, sans-serif",
            "style_notes": "Prestige, trust, sober elegance with strict OAB compliance, bespoke micro-interactions and gold accents."
        },
        "core_services": [
            {"name": "Direito Trabalhista e Rescisões Complexas", "benefit": "Garantia combativa de todos os direitos e indenizações com análise minuciosa."},
            {"name": "Direito Previdenciário e Aposentadorias", "benefit": "Planejamento previdenciário estratégico para concessão do melhor benefício possível no INSS."},
            {"name": "Direito Civil, Contratos e Família", "benefit": "Soluções ágeis e discretas para inventários, divórcios, partilhas e disputas contratuais."},
            {"name": "Assessoria Jurídica Empresarial e Tributária", "benefit": "Blindagem patrimonial, redução legal de riscos e compliance para seu negócio."},
        ],
        "pain_points": [
            "Medo de perder prazos e ser prejudicado financeiramente",
            "Falta de transparência e comunicação confusa cheia de juridiquês",
            "Sensação de que o advogado não dá retorno sobre o andamento do processo",
        ],
        "value_triggers": [
            "Atendimento transparente com atualizações diretas no WhatsApp",
            "Total sigilo e estrita observância ao Código de Ética da OAB",
            "Análise preliminar de viabilidade ágil e sem rodeios",
            "Atuação nacional online ou presencial com hora marcada",
        ],
        "sample_headline": "Defesa Estratégica dos Seus Direitos com Rigor Técnico e Transparência Total.",
        "sample_subheadline": "Assessoria jurídica especializada para proteger seu patrimônio, sua família e seu futuro sem burocracia.",
    },

    "gastronomia": {
        "niche_id": "gastronomia",
        "niche_pt": "Restaurante, Gastronomia & Delivery",
        "industry_en": "Artisanal Restaurant, Gourmet Dining & Fast Delivery",
        "target_audience": "Clientes buscando experiências gastronômicas memoráveis, ingredientes selecionados, ambiente agradável e delivery rápido.",
        "color_palette": {
            "primary": "#18181B",       # Grafite Carvão Noturno
            "secondary": "#EA580C",     # Laranja Chama / Terracota Apetite
            "accent": "#F59E0B",        # Âmbar Dourado
            "background": "#09090B",    # Dark Mode Premium Acolhedor
            "surface": "#27272A",       # Zinco 800
            "text": "#FAFAFA",
        },
        "typography": {
            "headings": "Cabinet Grotesk / Syne, sans-serif",
            "body": "Plus Jakarta Sans, sans-serif",
            "style_notes": "Appetizing, sensory-rich, high-contrast imagery, responsive interactive menu tabs, and instant WhatsApp/Delivery ordering."
        },
        "core_services": [
            {"name": "Cardápio Artesanal com Ingredientes Frescos", "benefit": "Receitas autorais e preparo diário com ingredientes de produtores selecionados."},
            {"name": "Delivery Expresso com Embalagem Térmica", "benefit": "Sua refeição entregue crocante, quente e perfeita no conforto da sua casa."},
            {"name": "Reserva de Mesas e Eventos Especiais", "benefit": "Garanta seu lugar sem filas para comemorações, aniversários e jantares românticos."},
            {"name": "Carta de Bebidas, Drinks e Sobremesas", "benefit": "Harmonização completa para transformar sua refeição em uma experiência inesquecível."},
        ],
        "pain_points": [
            "Comida que chega fria ou revirada em entregas demoradas",
            "Filas intermináveis de espera na porta aos finais de semana",
            "Cardápios desatualizados sem fotos ou preços claros",
        ],
        "value_triggers": [
            "Entrega rápida e rastreável pelo WhatsApp direto",
            "Ingredientes frescos sem conservantes ou ultraprocessados",
            "Ambiente instagramável com espaço climatizado e Wi-Fi",
            "Programa de fidelidade e benefícios para clientes frequentes",
        ],
        "sample_headline": "Sabores Inesquecíveis, Preparados com Paixão e Ingredientes de Verdade.",
        "sample_subheadline": "Venha viver uma experiência gastronômica autêntica ou peça nosso delivery expresso com entrega quente e rápida.",
    },

    "estetica": {
        "niche_id": "estetica",
        "niche_pt": "Clínica de Estética Avançada & Spa de Beleza",
        "industry_en": "Advanced Medical Aesthetics, Dermatology & Beauty Lounge",
        "target_audience": "Pessoas buscando autocuidado, rejuvenescimento sutil, tratamentos corporais e faciais de alta tecnologia com segurança.",
        "color_palette": {
            "primary": "#1C1917",       # Charcoal Aveludado
            "secondary": "#FDA4AF",     # Blush / Rose Gold Suave
            "accent": "#BE185D",        # Magenta Elegante
            "background": "#FFF1F2",    # Rose 50 Ultra Suave
            "surface": "#FFFFFF",       # Branco Puro
            "text": "#292524",
        },
        "typography": {
            "headings": "Playfair Display / Plus Jakarta Sans",
            "body": "Inter, sans-serif",
            "style_notes": "Sophisticated, glowing, relaxing luxury boutique aesthetic with subtle glassmorphism and before/after showcases."
        },
        "core_services": [
            {"name": "Harmonização Facial e Toxina Botulínica (Botox)", "benefit": "Rejuvenescimento natural que suaviza linhas de expressão sem perder sua identidade."},
            {"name": "Bioestimuladores de Colágeno e Firmeza da Pele", "benefit": "Estímulo biológico profundo para devolver o viço, elasticidade e contorno facial."},
            {"name": "Tratamentos Corporais e Redução de Medidas", "benefit": "Tecnologias avançadas contra flacidez, celulite e gordura localizada resistente."},
            {"name": "Depilação a Laser Indolor de Alta Potência", "benefit": "Pele lisa, sem pelos e sem foliculite desde as primeiras sessões."},
        ],
        "pain_points": [
            "Medo de resultados artificiais ou exagerados",
            "Profissionais sem qualificação técnica ou produtos de procedência duvidosa",
            "Falta de acompanhamento individualizado pós-procedimento",
        ],
        "value_triggers": [
            "Profissionais certificados da área da saúde estética",
            "Produtos originais liberados pela Anvisa com rastreabilidade",
            "Avaliação facial e corporal personalizada com câmera de alta definição",
            "Espaço privativo, relaxante e com máximo conforto",
        ],
        "sample_headline": "Realce Sua Melhor Versão com Resultados Naturais e Tecnologia de Ponta.",
        "sample_subheadline": "Protocolos de estética facial e corporal personalizados para elevar sua autoestima com máxima segurança.",
    },

    "barbearia": {
        "niche_id": "barbearia",
        "niche_pt": "Barbearia Clássica & Grooming Masculino",
        "industry_en": "Premium Gentleman's Barber Club & Grooming Lounge",
        "target_audience": "Homens modernos que valorizam visual impecável, barba alinhada, corte preciso e um ambiente exclusivo para relaxar.",
        "color_palette": {
            "primary": "#121212",       # Preto Fosco Nobre
            "secondary": "#78350F",     # Couro Vintage / Marrom Tabaco
            "accent": "#D97706",        # Âmbar Metálico (CTA)
            "background": "#0A0A0A",    # Dark Mode Premium
            "surface": "#1F1F1F",       # Superfície Grafite
            "text": "#E5E5E5",
        },
        "typography": {
            "headings": "Bebas Neue / Montserrat, sans-serif",
            "body": "Inter, sans-serif",
            "style_notes": "Vintage gentleman industrial club aesthetic with dark leather accents, clean pricing tables and 1-tap booking."
        },
        "core_services": [
            {"name": "Corte de Cabelo Personalizado & Fade Preciso", "benefit": "Visagismo e navalha para encontrar o corte perfeito que combina com o seu rosto."},
            {"name": "Barba Terapia com Toalha Quente e Ozônio", "benefit": "Alinhamento milimétrico com massagem facial e hidratação com óleos nobres."},
            {"name": "Tratamentos Capilares e Camuflagem de Grisalhos", "benefit": "Disfarce natural de fios brancos e fortalecimento dos fios sem parecer artificial."},
            {"name": "Combo Corte + Barba + Cerveja Artesanal", "benefit": "Experiência completa para relaxar enquanto cuida do seu estilo."},
        ],
        "pain_points": [
            "Barbeiro que erra o corte ou faz correndo para atender o próximo",
            "Esperas demoradas sem agendamento eficiente",
            "Ambientes barulhentos sem conforto ou produtos de qualidade",
        ],
        "value_triggers": [
            "Agendamento prático sem fila de espera via WhatsApp",
            "Cerveja gelada, café especial e mesa de sinuca/Wi-Fi",
            "Barbeiros experientes especialistas em visagismo masculino",
            "Produtos de alta performance específicos para cabelo e barba",
        ],
        "sample_headline": "Muito Mais que um Corte: Tradição, Estilo e Respeito ao Seu Tempo.",
        "sample_subheadline": "Barbearia premium com profissionais especializados, toalha quente e atendimento com hora marcada.",
    },

    "automotivo": {
        "niche_id": "automotivo",
        "niche_pt": "Centro Automotivo & Oficina Mecânica Especializada",
        "industry_en": "Precision Auto Center, Diagnostics & Mechanical Service",
        "target_audience": "Proprietários de veículos que exigem manutenção preventiva segura, honestidade de orçamento e peças de primeira linha.",
        "color_palette": {
            "primary": "#0F172A",       # Grafite Asfalto
            "secondary": "#DC2626",     # Vermelho Performance / Aceleração
            "accent": "#F59E0B",        # Âmbar Alerta / CTA
            "background": "#FFFFFF",    # Branco Industrial Limpo
            "surface": "#F1F5F9",       # Cinza Técnico
            "text": "#0F172A",
        },
        "typography": {
            "headings": "Chakra Petch / Plus Jakarta Sans, sans-serif",
            "body": "Inter, sans-serif",
            "style_notes": "Dynamic, high-trust, mechanical precision aesthetic, with transparent pricing badges and WhatsApp quote triggers."
        },
        "core_services": [
            {"name": "Diagnóstico Eletrônico Computadorizado com Scanner", "benefit": "Identificação precisa de falhas na injeção e eletrônica sem achismos."},
            {"name": "Revisão Preventiva Geral e Troca de Óleo e Filtros", "benefit": "Garantia de segurança na estrada e economia de combustível a longo prazo."},
            {"name": "Freios, Suspensão e Amortecedores", "benefit": "Componentes originais com testes rigorosos para máxima estabilidade e frenagem."},
            {"name": "Alinhamento 3D, Balanceamento e Pneus", "benefit": "Direção firme, sem vibrações no volante e desgaste uniforme dos pneus."},
        ],
        "pain_points": [
            "Medo constante de ser enganado com peças desnecessárias ou orçamentos inflados",
            "Demora excessiva para entrega do veículo deixando o cliente a pé",
            "Oficinas sujas sem garantias formais por escrito",
        ],
        "value_triggers": [
            "Orçamento 100% transparente com fotos e vídeos das peças via WhatsApp",
            "Garantia formal de peças e mão de obra por escrito",
            "Scanner de diagnóstico compatível com carros nacionais e importados",
            "Leva e traz / Sala de espera climatizada com café e Wi-Fi",
        ],
        "sample_headline": "Seu Carro em Boas Mãos: Mecânica de Precisão com Honestidade Comprovada.",
        "sample_subheadline": "Diagnóstico computadorizado, peças originais com garantia e orçamento transparente sem surpresas.",
    },

    "imobiliaria": {
        "niche_id": "imobiliaria",
        "niche_pt": "Imobiliária, Corretora & Negócios Imobiliários",
        "industry_en": "Boutique Real Estate Agency, Prime Properties & Advisory",
        "target_audience": "Compradores, investidores e famílias buscando comprar, vender ou alugar imóveis com segurança jurídica e consultoria dedicada.",
        "color_palette": {
            "primary": "#064E3B",       # Verde Floresta / Solidez
            "secondary": "#0F172A",     # Grafite Escuro
            "accent": "#D97706",        # Dourado Imobiliário
            "background": "#FFFFFF",    # Branco Puro
            "surface": "#F4F7F4",       # Menta Acinzentado
            "text": "#1E293B",
        },
        "typography": {
            "headings": "Playfair Display / Plus Jakarta Sans",
            "body": "Inter, sans-serif",
            "style_notes": "Prestigious architectural layout, high-res property image cards, interactive filter pills and direct broker WhatsApp CTAs."
        },
        "core_services": [
            {"name": "Venda e Compra de Imóveis Residenciais e Comerciais", "benefit": "Curadoria exclusiva com as melhores opções da região prontas para morar ou investir."},
            {"name": "Lançamentos e Imóveis na Planta com Condições Especiais", "benefit": "Acesso antecipado a empreendimentos com alto potencial de valorização."},
            {"name": "Consultoria e Assessoria Jurídica Imobiliária Completa", "benefit": "Análise minuciosa de certidões e contratos para transação 100% segura sem dores de cabeça."},
            {"name": "Avaliação Mercadológica Precisa do seu Imóvel", "benefit": "Descubra o valor real de mercado para vender mais rápido sem perder dinheiro."},
        ],
        "pain_points": [
            "Burocracia infernal e contratos com cláusulas dúbias",
            "Imóveis com documentação irregular que travam o financiamento",
            "Corretores insistentes que mostram opções que não têm nada a ver com o cliente",
        ],
        "value_triggers": [
            "Corretores credenciados pelo CRECI com consultoria personalizada",
            "Parceria direta com os principais bancos para aprovação rápida de crédito",
            "Tour virtual 360° e fotos profissionais de cada imóvel",
            "Mais de 95% de clientes satisfeitos com atendimento rápido",
        ],
        "sample_headline": "Encontre o Imóvel Perfeito para Sua Família ou Seu Próximo Grande Investimento.",
        "sample_subheadline": "Curadoria exclusiva de imóveis com segurança jurídica completa e assessoria do início à entrega das chaves.",
    },

    "fitness": {
        "niche_id": "fitness",
        "niche_pt": "Academia, Studio Fitness & Treinamento",
        "industry_en": "High-Performance Fitness Club, Training Studio & Wellness",
        "target_audience": "Pessoas querendo transformar a saúde física, emagrecer, ganhar massa muscular ou aliviar o estresse com acompanhamento motivador.",
        "color_palette": {
            "primary": "#09090B",       # Ônix Profundo
            "secondary": "#84CC16",     # Verde Volt Elétrico / Energia
            "accent": "#06B6D4",        # Ciano Vibrante
            "background": "#09090B",    # Dark Mode Energético
            "surface": "#18181B",       # Zinco Escuro
            "text": "#F4F4F5",
        },
        "typography": {
            "headings": "Syne / Montserrat Black, sans-serif",
            "body": "Plus Jakarta Sans, sans-serif",
            "style_notes": "Dynamic, high-voltage fitness club energy, bold typography, schedule tab filters and 1-tap Free Trial Class CTA."
        },
        "core_services": [
            {"name": "Musculação com Equipamentos Biomecânicos Modernos", "benefit": "Treinos seguros que maximizam resultados sem sobrecarregar as articulações."},
            {"name": "Aulas Coletivas Dinâmicas (Spinning, Funcional, Dança)", "benefit": "Queima calórica intensa em ambiente contagiante com professores motivadores."},
            {"name": "Treinamento Personalizado e Avaliação Física 3D", "benefit": "Metas claras e fichas de treino adaptadas à sua rotina e evolução real."},
            {"name": "Área de Recuperação, Alongamento e Convivência", "benefit": "Espaço completo para desaquecer, hidratar e recarregar as energias."},
        ],
        "pain_points": [
            "Ambientes cheios onde se perde tempo revezando aparelhos",
            "Instrutores que ignoram alunos iniciantes deixando-os com vergonha",
            "Planos com taxas de cancelamento abusivas e contratos de longo prazo",
        ],
        "value_triggers": [
            "Aparelhos modernos e manutenção periódica impecável",
            "Acompanhamento atencioso desde o primeiro dia de treino",
            "Horário estendido de segunda a domingo para sua comodidade",
            "Ganhe 1 Aula Experimental 100% Gratuita para conhecer a estrutura",
        ],
        "sample_headline": "Treine em um Ambiente que Inspira Sua Melhor Versão Todos os Dias.",
        "sample_subheadline": "Equipamentos de última geração, professores que te acompanham de verdade e planos sem pegadinhas.",
    },

    "pet": {
        "niche_id": "pet",
        "niche_pt": "Clínica Veterinária, Pet Shop & Banho e Tosa",
        "industry_en": "Compassionate Veterinary Clinic, Pet Care & Grooming Spa",
        "target_audience": "Tutores de cães e gatos que consideram seus pets como filhos e não abrem mão de carinho, higiene e medicina preventiva.",
        "color_palette": {
            "primary": "#059669",       # Verde Esmeralda Natural
            "secondary": "#0284C7",     # Azul Confiável
            "accent": "#F59E0B",        # Âmbar Quente
            "background": "#FFFFFF",    # Branco Puro
            "surface": "#F0FDF4",       # Menta Acolhedor
            "text": "#1E293B",
        },
        "typography": {
            "headings": "Plus Jakarta Sans, sans-serif",
            "body": "Inter, sans-serif",
            "style_notes": "Warm, loving, friendly medical and grooming aesthetic with rounded edges, pet photo cards and WhatsApp emergency quick button."
        },
        "core_services": [
            {"name": "Consultas Veterinárias, Vacinação e Prevenção", "benefit": "Atendimento carinhoso e minucioso para manter seu pet protegido e saudável."},
            {"name": "Banho e Tosa com Câmeras e Vidro Panorâmico", "benefit": "Higiene profissional com toalhas esterilizadas e produtos hipoalergênicos sem estresse."},
            {"name": "Cirurgias Gerais e Exames Laboratoriais Rápidos", "benefit": "Estrutura cirúrgica equipada com anestesia inalatória e monitoramento contínuo."},
            {"name": "Farmácia Veterinária Completa e Rações Super Premium", "benefit": "Medicamentos e nutrição de ponta recomendados por quem cuida do seu pet."},
        ],
        "pain_points": [
            "Medo de que o pet seja maltratado ou fique traumatizado no banho",
            "Clínicas frias com veterinários impacientes que cobram exames desnecessários",
            "Falta de socorro veterinário rápido quando o animal adoece de repente",
        ],
        "value_triggers": [
            "Vidro panorâmico no banho e tosa para você acompanhar tudo",
            "Veterinários apaixonados por animais e com pós-graduação",
            "Ambiente com salas separadas para cães e gatos (reduz estresse)",
            "Atendimento de urgência e contato direto no WhatsApp",
        ],
        "sample_headline": "O Amor e Cuidado que o Seu Melhor Amigo Merece, em Cada Detalhe.",
        "sample_subheadline": "Medicina veterinária dedicada, banho e tosa com carinho e tudo o que seu pet precisa para uma vida longa e feliz.",
    },

    "geral": {
        "niche_id": "geral",
        "niche_pt": "Negócio Local & Prestação de Serviços",
        "industry_en": "Professional Local Business & Premium Services",
        "target_audience": "Clientes locais buscando confiança, rapidez de resposta, trabalho de qualidade e facilidade de contato via WhatsApp.",
        "color_palette": {
            "primary": "#0F172A",       # Grafite / Azul Marinho
            "secondary": "#2563EB",     # Azul Royal Confiável
            "accent": "#10B981",        # Esmeralda CTA
            "background": "#FFFFFF",    # Branco Puro
            "surface": "#F8FAFC",       # Cinza 50 Suave
            "text": "#0F172A",
        },
        "typography": {
            "headings": "Plus Jakarta Sans, sans-serif",
            "body": "Inter, sans-serif",
            "style_notes": "Modern, crisp, high-conversion commercial landing page layout with prominent reviews, map and WhatsApp floating trigger."
        },
        "core_services": [
            {"name": "Atendimento Especializado com Hora Marcada", "benefit": "Soluções sob medida para sua necessidade com pontualidade e agilidade."},
            {"name": "Garantia de Qualidade e Suporte Dedicado", "benefit": "Trabalho executado por profissionais capacitados com materiais de primeira linha."},
            {"name": "Orçamento Rápido e Sem Burocracia via WhatsApp", "benefit": "Tire suas dúvidas e receba propostas claras em poucos minutos no celular."},
            {"name": "Facilidade de Pagamento e Condições Especiais", "benefit": "Parcelamento transparente pensado para viabilizar seu projeto."},
        ],
        "pain_points": [
            "Falta de pontualidade e demora para responder mensagens",
            "Serviços mal feitos sem garantia de qualidade",
            "Orçamentos sem transparência com custos surpresa no final",
        ],
        "value_triggers": [
            "Atendimento ágil direto com especialistas pelo WhatsApp",
            "Garantia formal de qualidade em todos os serviços",
            "Empresa consolidada com excelentes avaliações no Google",
            "Localização de fácil acesso e estacionamento",
        ],
        "sample_headline": "Excelência e Compromisso: A Escolha de Confiança na Nossa Região.",
        "sample_subheadline": "Soluções profissionais realizadas com dedicação, agilidade e o melhor custo-benefício para você.",
    },
}


def detect_niche_profile(name: str, category: Optional[str] = None, address: Optional[str] = None) -> Dict[str, Any]:
    """
    Identifica de forma profunda o perfil de nicho ideal para a empresa com base no nome,
    categoria oficial do Google Places e endereço.
    """
    combined_text = f"{name or ''} {category or ''} {address or ''}".lower()

    # Mapeamento por palavras-chave com pesos semânticos
    rules = [
        ("odonto", ["odonto", "dent", "implant", "sorriso", "orto", "alinhador", "facetas", "dental", "periodont"]),
        ("medicina", ["clinic", "medic", "doutor", "dr.", "dra.", "saude", "oftalm", "dermato", "pediatra", "cardiolog", "ortoped", "psicolog", "fisioter", "nutri", "laborat", "hospital"]),
        ("advocacia", ["advog", "jurid", "direito", "associados", "oab", "tributar", "previdenci", "trabalhist", "advocacia"]),
        ("gastronomia", ["restaurante", "pizz", "burger", "hamburg", "bistr", "cafe", "cafeteria", "culin", "sushi", "churrasc", "padaria", "bar", "pub", "confeit", "gastronom", "lanchonete", "acai", "massa"]),
        ("estetica", ["estetica", "beleza", "salao", "micropigment", "depilac", "spa", "sobrancelh", "massag", "laser", "unhas", "nails", "hair", "cabeleireir", "harmonizacao"]),
        ("barbearia", ["barbearia", "barber", "barba", "navalha"]),
        ("automotivo", ["oficina", "mecanic", "auto center", "autocenter", "pneus", "funilaria", "pintura", "suspens", "freios", "auto eletric", "detail", "lava rapido", "troca de oleo", "car"]),
        ("imobiliaria", ["imobiliaria", "imoveis", "corretor", "arquitet", "engenhar", "construtor", "reforma", "marmoraria", "vidrac", "decorac"]),
        ("fitness", ["academia", "fitness", "crossfit", "treino", "personal", "pilates", "yoga", "luta", "artes marciais", "boxe", "jiu", "musculacao"]),
        ("pet", ["pet", "vet", "veterinar", "bicho", "banho e tosa", "canil", "felin", "racao", "animal"]),
    ]

    for niche_key, keywords in rules:
        if any(kw in combined_text for kw in keywords):
            return NICHE_PROFILES[niche_key]

    # Se não houver match direto em palavras comuns mas temos a categoria do Google Places:
    default_profile = dict(NICHE_PROFILES["geral"])
    if category:
        clean_cat = category.strip().title()
        default_profile["niche_pt"] = clean_cat
        default_profile["industry_en"] = f"Specialized {clean_cat} Provider"
        default_profile["target_audience"] = f"Clientes e famílias em busca de serviços confiáveis de {clean_cat.lower()}."
        default_profile["sample_headline"] = f"A Escolha de Confiança em {clean_cat} na Região."

    return default_profile


def build_impeccable_site_prompt(
    lead: LeadResult,
    profile: Dict[str, Any],
    diagnosis: DiagnosisResult,
) -> str:
    """
    Gera um roteiro arquitetural e criativo de UI/UX em INGLÊS com especificações
    cirúrgicas para ferramentas como Google Stitch, v0, Lovable ou geradores de código.
    """
    city_or_address = lead.formatted_address or lead.city or "Brasil"
    city_short = lead.city or (lead.formatted_address.split(",")[-2].strip() if lead.formatted_address and "," in lead.formatted_address else "sua região")

    # Formatação da Reputação
    if lead.rating and lead.rating >= 4.0:
        rating_badge = f"{lead.rating}/5.0 Stars ({lead.user_rating_count or '100+'} verified Google Reviews)"
        rating_proof_text = f"Top-rated {profile['niche_pt']} in {city_short} with an outstanding {lead.rating}★ rating on Google Maps."
    else:
        rating_badge = "Empresa Verificada & Referência em Atendimento Local"
        rating_proof_text = f"Reconhecida pela pontualidade, transparência e satisfação dos clientes em {city_short}."

    # WhatsApp Link
    clean_phone = "".join(c for c in (lead.national_phone_number or "") if c.isdigit())
    greeting_text = urllib.parse.quote(f"Olá! Conheci a {lead.name} pelo site e gostaria de agendar um atendimento.")
    wa_url = f"https://wa.me/55{clean_phone}?text={greeting_text}" if clean_phone else "https://wa.me/?text=Ola"

    # Proposta de valor e dores do diagnóstico
    sales = diagnosis.sales_recommendation
    val_prop = sales.value_proposition if sales and sales.value_proposition else profile["sample_headline"]
    headline_txt = profile.get("sample_headline", f"Excelência em {profile['niche_pt']} para Você.")
    subheadline_txt = profile.get("sample_subheadline", "Atendimento ágil, transparente e focado em superar suas expectativas.")

    # Formatação dos serviços do nicho
    services_md = []
    for idx, s in enumerate(profile["core_services"][:5], 1):
        services_md.append(
            f"  - Card {idx}: **{s['name']}**\n"
            f"    - Benefit Copy: {s['benefit']}\n"
            f"    - Action Trigger: Direct WhatsApp consultation button with pre-filled topic '{s['name']}'"
        )
    services_formatted = "\n".join(services_md)

    # Formatação dos diferenciais
    differentials_md = []
    for idx, d in enumerate(profile["value_triggers"][:4], 1):
        differentials_md.append(f"  - Differential {idx}: {d}")
    differentials_formatted = "\n".join(differentials_md)

    palette = profile["color_palette"]
    typo = profile["typography"]

    # Fotos reais públicas do Google
    photos = getattr(lead, "image_urls", None) or []
    hero_photo = getattr(lead, "image_url", None) or (photos[0] if photos else None)
    if hero_photo or photos:
        photos_lines = []
        for idx, p_url in enumerate(photos[:4], 1):
            photos_lines.append(f"  - Public Gallery Photo {idx}: '{p_url}'")
        gallery_formatted = "\n".join(photos_lines)
        photo_spec_md = f"""- **Real Business Photography (Verified Google Places Public Photos):**
  - Primary Hero Cover: '{hero_photo}' (Use in split hero layout or background banner with dark gradient overlay)
  - Authentic Atmosphere & Facility Photos:
{gallery_formatted}
  - CRITICAL INSTRUCTION: Use these exact authentic CDN image URLs in <img> src attributes for the hero section and facilities showcase. Do NOT replace them with generic stock images."""
    else:
        photo_spec_md = f"- **Imagery Standard:** High-converting commercial photography strictly representing {profile['industry_en']} with modern lighting."

    prompt = f"""# UI/UX GENERATION PROMPT: HIGH-CONVERTING LANDING PAGE FOR {lead.name.upper()}

## 1. PROJECT SPECIFICATION & ART DIRECTION
- **Client/Brand Name:** {lead.name}
- **Specialized Industry:** {profile['industry_en']} ({profile['niche_pt']})
- **Target Market Location:** {city_or_address}
- **Primary Business Goal:** Drive qualified customer inquiries and instant bookings via direct WhatsApp integration.
- **Brand Personality & Tone of Voice:** Authoritative, reassuring, empathetic, transparent, premium yet accessible.
- **Strict Color Architecture (HEX Tokens):**
  - Primary Brand Identity: `{palette['primary']}`
  - Secondary / Supporting: `{palette['secondary']}`
  - High-Contrast Conversion Accent (CTAs): `{palette['accent']}`
  - Background Neutral: `{palette['background']}`
  - Card & Container Surface: `{palette['surface']}`
  - Body & Heading Typography: `{palette['text']}`
- **Typography Standard:**
  - Display & Headings: {typo['headings']}
  - Body & UI Elements: {typo['body']}
  - Aesthetic Notes: {typo['style_notes']}

## 2. HERO SECTION (ABOVE THE FOLD - MAXIMUM PERSUASION)
- **Visual Composition:** Two-column split layout (desktop) / Stacked with instant visual anchor (mobile).
{photo_spec_md}
- **High-Impact Headline:** "{headline_txt}"
- **Persuasive Subheadline:** "{subheadline_txt}"
- **Primary Hero CTA Button:**
  - Label: "Falar com Especialista no WhatsApp ↗"
  - Micro-copy beneath button: "⚡ Resposta rápida e atendimento sem compromisso"
  - Action Target: `{wa_url}`
- **Authority Proof Badges (Immediately Below Hero Buttons):**
  - Badge 1 (Reputation): ⭐ {rating_badge}
  - Badge 2 (Trust Anchor): 🛡️ {profile['value_triggers'][0]}
  - Badge 3 (Local Presence): 📍 Atendimento presencial e online em {city_short}

## 3. SPECIALIZED SERVICES & PROCEDURES MATRIX
- **Section Heading:** "Nossas Soluções Especializadas para Você"
- **Section Subtitle:** "Cuidado individualizado com tecnologia de ponta e foco total nos seus resultados."
- **Interactive Component Grid:**
{services_formatted}
- **UX Requirement:** Each card must include subtle hover elevation (scale-105 transition), modern icons, outcome-driven copy, and an individual inquiry button.

## 4. COMPETITIVE DIFFERENTIALS (WHY CHOOSE {lead.name.upper()})
- **Section Heading:** "Por que Somos a Escolha de Confiança na Região"
- **Section Subtitle:** "Eliminamos a burocracia e as dores de cabeça com um padrão de atendimento diferenciado:"
- **Highlights Grid (4 Pillars):**
{differentials_formatted}

## 5. REAL SOCIAL PROOF & GOOGLE REPUTATION ENGINE
- **Section Heading:** "Aprovado por Quem Já Conhece e Confia"
- **Reputation Bar:** Display verified Google Maps badge: {rating_proof_text}
- **Testimonial Carousel/Grid:** 3 authentic, sector-specific customer testimonials praising punctuality, technical quality, humanized care, and great outcome.

## 6. LOCATION CONVENIENCE & INTERACTIVE LOCAL MAP
- **Section Heading:** "Fácil Localização e Atendimento com Hora Marcada"
- **Left Column:**
  - Physical Address: {lead.formatted_address or 'Consulte nosso endereço completo pelo WhatsApp'}
  - Direct Phone/WhatsApp: {lead.national_phone_number or 'Disponível no botão'}
  - Operating Hours: Segunda a Sexta: 08h às 19h | Sábado: 08h às 13h
  - Route Button: "Como Chegar via Google Maps (GPS)"
- **Right Column:** Embedded interactive Google Maps viewport showing the exact pinpoint.

## 7. HIGH-CONVERSION PERSUASIVE CLOSING & MOBILE ACTION BAR
- **Bottom Closing Banner:** Deep gradient with headline: "Pronto para Transformar sua Experiência com {lead.name}?"
- **Closing Value Proposition:** "{val_prop}"
- **Main Action CTA:** Big high-contrast button pointing to `{wa_url}`.
- **Sticky Bottom Mobile Bar (Crucial):** Persistent fixed bottom bar on mobile screens with:
  - Phone call button (`tel:{clean_phone}`)
  - Pulsing WhatsApp CTA button with direct chat trigger.

## 8. TECHNICAL, SPEED & ACCESSIBILITY REQUIREMENTS
- 100% Mobile-first responsive layout (strictly tested on 375px, 414px, 768px, 1280px, 1920px).
- Core Web Vitals target: PageSpeed 95+, Largest Contentful Paint < 1.1s, Cumulative Layout Shift = 0.
- Semantic HTML5 structure with OpenGraph meta tags optimized for WhatsApp link previews.
- Fully accessible WCAG AA compliant colors, button states and font sizes.
"""
    return prompt.strip()


def build_brand_identity_summary(
    lead: LeadResult,
    profile: Dict[str, Any],
    diagnosis: DiagnosisResult,
) -> str:
    """
    Gera um resumo executivo da identidade visual e tom de voz em português.
    """
    palette = profile["color_palette"]
    typo = profile["typography"]
    sales = diagnosis.sales_recommendation
    value_prop = sales.value_proposition if sales and sales.value_proposition else profile["sample_headline"]

    return (
        f"🎨 IDENTIDADE VISUAL & TOM DE VOZ — {lead.name.upper()}\n"
        f"• Segmento: {profile['niche_pt']} ({profile['industry_en']})\n"
        f"• Proposta de Valor: {value_prop}\n"
        f"• Paleta de Cores: Primária ({palette['primary']}), Apoio ({palette['secondary']}), CTA Destaque ({palette['accent']}), Fundo ({palette['background']})\n"
        f"• Tipografia: Títulos ({typo['headings']}), Texto ({typo['body']})\n"
        f"• Tom de Voz: Empático, consultivo, de alta autoridade e focado em conversão sem rodeios técnicos."
    )
