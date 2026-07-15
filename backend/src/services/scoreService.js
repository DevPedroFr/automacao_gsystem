/**
 * Score Service — Calcula DMS (Digital Maturity Score) e COS (Commercial Opportunity Score)
 */

/**
 * Calcula o Digital Maturity Score (0-100)
 * Composto por: Google Business Profile (40pts), Performance Web (35pts), Presença Social (25pts)
 * @param {Object} lead - Dados do lead
 * @returns {number} Score de 0 a 100
 */
function calculateDMS(lead) {
  let total = 0;

  // === Google Business Profile (40 pontos max) ===
  // Nota: (google_rating / 5) * 20
  const ratingScore = ((lead.google_rating || 0) / 5) * 20;
  // Volume: min(google_reviews_count, 100) / 100 * 20
  const reviewsScore = (Math.min(lead.google_reviews_count || 0, 100) / 100) * 20;
  total += ratingScore + reviewsScore;

  // === Performance Web (35 pontos max) ===
  if (lead.has_website && lead.pagespeed_score != null) {
    total += (lead.pagespeed_score / 100) * 35;
  }
  // Se não tem website → 0 pontos

  // === Presença Social (25 pontos max) ===
  if (lead.has_instagram) total += 10;
  if (lead.has_facebook) total += 10;
  if (lead.social_last_post_days != null && lead.social_last_post_days < 30) total += 5;

  return Math.round(total);
}

/**
 * Calcula o Commercial Opportunity Score (0-100)
 * Leva em conta a validação do negócio e o gap digital
 * @param {Object} lead - Dados do lead
 * @param {number} dms - Digital Maturity Score calculado
 * @returns {number} Score de 0 a 100
 */
function calculateCOS(lead, dms) {
  // Business Validation (0-100)
  let businessValidation = 20;
  const rating = lead.google_rating || 0;
  const reviews = lead.google_reviews_count || 0;

  if (rating >= 3.5 && reviews >= 50) {
    businessValidation = 100;
  } else if (rating >= 3.5 && reviews >= 10) {
    businessValidation = 75;
  } else if (rating >= 3.0 && reviews >= 5) {
    businessValidation = 50;
  }

  // Digital Gap: quanto pior a presença digital, maior a oportunidade
  const digitalGap = 100 - dms;

  // COS = 40% validação do negócio + 60% gap digital
  const cos = (businessValidation * 0.4) + (digitalGap * 0.6);

  return Math.round(cos);
}

/**
 * Determina a prioridade com base no COS
 * @param {number} cos - Commercial Opportunity Score
 * @returns {'A'|'B'|'C'} Prioridade
 */
function getPriority(cos) {
  if (cos > 80) return 'A';
  if (cos >= 50) return 'B';
  return 'C';
}

module.exports = { calculateDMS, calculateCOS, getPriority };
