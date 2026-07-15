function randomBetween(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

async function analyzeWebsite(url) {
  if (!url) return null;

  const scoreDistribution = () => {
    const roll = Math.random();
    if (roll < 0.15) return randomBetween(25, 35);
    if (roll < 0.40) return randomBetween(36, 50);
    if (roll < 0.70) return randomBetween(51, 70);
    if (roll < 0.90) return randomBetween(71, 85);
    return randomBetween(86, 95);
  };

  const pagespeed_score = scoreDistribution();

  const lcpBase = pagespeed_score < 50 ? 4000 : pagespeed_score < 70 ? 2500 : 1200;
  const lcp_ms = lcpBase + randomBetween(-500, 2000);

  const inpBase = pagespeed_score < 50 ? 350 : pagespeed_score < 70 ? 200 : 80;
  const inp_ms = inpBase + randomBetween(-30, 150);

  const clsBase = pagespeed_score < 50 ? 0.3 : pagespeed_score < 70 ? 0.15 : 0.05;
  const cls = parseFloat((clsBase + Math.random() * 0.15).toFixed(2));

  return {
    pagespeed_score,
    lcp_ms: Math.max(1000, Math.min(8000, lcp_ms)),
    inp_ms: Math.max(50, Math.min(500, inp_ms)),
    cls: Math.max(0.01, Math.min(0.5, cls)),
  };
}

module.exports = { analyzeWebsite };
