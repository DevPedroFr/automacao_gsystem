// Provider real para a Outscraper API (ESQUELETO MOCKADO)
const mockProvider = require('./mock');

async function searchBusinesses(niche, location) {
  console.log(`[Outscraper Provider] Simulação de chamada real iniciada para "${niche}" em "${location}"`);
  // TODO: Implementar chamada à Outscraper API real futuramente
  return mockProvider.searchBusinesses(niche, location);
}

module.exports = { searchBusinesses };
