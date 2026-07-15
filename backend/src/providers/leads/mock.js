// Pools de nomes por nicho para gerar variações realistas
const nicheNamePools = {
  'clínicas odontológicas': {
    prefixes: ['Clínica', 'Centro Odontológico', 'Consultório', 'Espaço', 'Studio'],
    names: ['Sorria', 'Dental Premium', 'OdontoVida', 'Sorriso & Saúde', 'OdontoPlan', 'OdontoCenter', 'Oral Excellence'],
    suffixes: ['Odontologia', 'Implantes', 'Ortodontia', 'Estética Dental', 'Odontologia Integrada'],
    doctors: ['Dr. Santos', 'Dra. Oliveira', 'Dr. Mendes', 'Dra. Lima', 'Dr. Ferreira', 'Dra. Costa', 'Dr. Almeida'],
  },
  'imobiliárias': {
    prefixes: ['Imobiliária', 'Grupo', 'Portal', 'Rede'],
    names: ['Nova Casa', 'Morada', 'Horizonte', 'Viva Imóveis', 'Real Estate', 'Prime', 'Casa & Cia', 'Lares'],
    suffixes: ['Imóveis', 'Negócios Imobiliários', 'Empreendimentos', 'Consultoria Imobiliária'],
    doctors: [],
  },
  'restaurantes': {
    prefixes: ['Restaurante', 'Bistrô', 'Cantina', 'Empório', 'Casa'],
    names: ['Sabor & Arte', 'Tempero da Terra', 'Villa Gourmet', 'Alma Cozinha', 'Paladar', 'Aroeira', 'Manjericão'],
    suffixes: ['Gastronomia', 'Cozinha Artesanal', 'Culinária', 'Bar & Restaurante', 'Grill'],
    doctors: [],
  },
  'advogados': {
    prefixes: ['Escritório', 'Advocacia', 'Sociedade de Advogados'],
    names: ['Silva & Associados', 'Mendes Advocacia', 'Barros & Cunha', 'Peixoto Legal', 'Juris Consultoria'],
    suffixes: ['Advogados', 'Assessoria Jurídica', 'Consultoria Legal'],
    doctors: [],
  },
  'academias': {
    prefixes: ['Academia', 'Studio', 'Centro Fitness', 'Espaço'],
    names: ['Iron Body', 'Viva Fit', 'Power Gym', 'Evolution', 'Corpo & Mente', 'MaxForce', 'Elite Fitness'],
    suffixes: ['Fitness', 'Training', 'Saúde & Bem-Estar', 'Personal Studio'],
    doctors: [],
  },
};

const genericPool = {
  prefixes: ['Empresa', 'Centro', 'Espaço', 'Studio', 'Grupo'],
  names: ['Premium', 'Excellence', 'Mais', 'Top', 'Master', 'Pro', 'Prime', 'Quality'],
  suffixes: ['Serviços', 'Soluções', 'Consultoria', 'Profissional'],
  doctors: [],
};

const streets = [
  'Rua XV de Novembro', 'Av. Brasil', 'Rua Marechal Deodoro', 'Av. Sete de Setembro',
  'Rua das Flores', 'Av. República Argentina', 'Rua Padre Anchieta', 'Rua Comendador Araújo',
  'Av. Visconde de Guarapuava', 'Rua Voluntários da Pátria', 'Rua Emiliano Perneta',
  'Av. Presidente Getúlio Vargas', 'Rua Santos Dumont', 'Av. Paulista', 'Rua Augusta',
];

function randomBetween(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function randomFloat(min, max, decimals = 1) {
  const val = Math.random() * (max - min) + min;
  return parseFloat(val.toFixed(decimals));
}

function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function generatePhone() {
  const ddd = pickRandom(['11', '21', '41', '48', '51', '31', '27', '47', '43', '42']);
  const num = `9${randomBetween(1000, 9999)}-${randomBetween(1000, 9999)}`;
  return `(${ddd}) ${num}`;
}

function generateBusinessName(pool, index) {
  const strategy = index % 4;
  switch (strategy) {
    case 0:
      return `${pickRandom(pool.prefixes)} ${pickRandom(pool.names)}`;
    case 1:
      if (pool.doctors.length > 0) {
        return `${pickRandom(pool.doctors)} ${pickRandom(pool.suffixes)}`;
      }
      return `${pickRandom(pool.names)} ${pickRandom(pool.suffixes)}`;
    case 2:
      return `${pickRandom(pool.prefixes)} ${pickRandom(pool.names)} ${pickRandom(pool.suffixes)}`;
    case 3:
      return pickRandom(pool.names);
    default:
      return `${pickRandom(pool.prefixes)} ${pickRandom(pool.names)}`;
  }
}

function generateWebsite(businessName) {
  if (Math.random() < 0.35) return null;

  const slug = businessName
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, '')
    .slice(0, 20);

  const domains = ['.com.br', '.com.br', '.com.br', '.com', '.net.br'];
  return `https://www.${slug}${pickRandom(domains)}`;
}

async function searchBusinesses(niche, location, minRating, searchStatus, negativeKeywords) {
  const nicheKey = niche.toLowerCase();
  const pool = nicheNamePools[nicheKey] || genericPool;
  const count = randomBetween(12, 15);
  const businesses = [];
  const usedNames = new Set();

  for (let i = 0; i < count; i++) {
    let name;
    let attempts = 0;
    do {
      name = generateBusinessName(pool, i + attempts);
      attempts++;
    } while (usedNames.has(name) && attempts < 20);
    usedNames.add(name);

    const address = `${pickRandom(streets)}, ${randomBetween(10, 3500)}`;

    businesses.push({
      name,
      category: niche,
      phone: generatePhone(),
      website: generateWebsite(name),
      address,
      city: location,
      google_rating: randomFloat(2.0, 5.0, 1),
      google_reviews_count: randomBetween(0, 500),
    });
  }

  let filteredBusinesses = businesses;

  if (minRating) {
    filteredBusinesses = filteredBusinesses.filter(b => b.google_rating >= minRating);
  }

  if (negativeKeywords && negativeKeywords.length > 0) {
    filteredBusinesses = filteredBusinesses.filter(b => {
      const titleLower = b.name.toLowerCase();
      return !negativeKeywords.some(word => titleLower.includes(word.toLowerCase()));
    });
  }

  return filteredBusinesses;
}

module.exports = { searchBusinesses };
