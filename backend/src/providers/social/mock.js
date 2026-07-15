async function analyzeSocialPresence(businessName, website) {
  const hasWebsiteBonus = website ? 0.15 : 0;

  const has_instagram = Math.random() < (0.60 + hasWebsiteBonus) ? 1 : 0;
  const has_facebook = Math.random() < (0.50 + hasWebsiteBonus) ? 1 : 0;

  let social_last_post_days = null;
  if (has_instagram || has_facebook) {
    const activeBonus = (has_instagram && has_facebook) ? 0 : 30;
    const base = Math.floor(Math.random() * 150) + 1;
    social_last_post_days = Math.min(180, base + activeBonus);

    if (Math.random() < 0.30) {
      social_last_post_days = Math.floor(Math.random() * 15) + 1;
    }
  }

  const has_linkedin = Math.random() < (0.35 + hasWebsiteBonus) ? 1 : 0;

  return {
    has_instagram,
    has_facebook,
    has_linkedin,
    social_last_post_days,
  };
}

module.exports = { analyzeSocialPresence };
