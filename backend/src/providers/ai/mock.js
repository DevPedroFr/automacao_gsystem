async function generateDiagnostic(lead) {
  const observed_facts = buildObservedFacts(lead);
  const inferences = buildInferences(lead);
  const recommendations = buildRecommendations(lead);
  const email_draft = buildEmailDraft(lead);

  return {
    observed_facts,
    inferences,
    recommendations,
    email_draft,
  };
}

function buildObservedFacts(lead) {
  const facts = [];

  facts.push(`• Avaliação Google: ${lead.google_rating?.toFixed(1) || 'N/A'} estrelas (${lead.google_reviews_count || 0} avaliações)`);

  if (lead.has_website && lead.website) {
    facts.push(`• Site: ${lead.website} — PageSpeed Score: ${lead.pagespeed_score || 'N/A'}/100 (LCP: ${lead.lcp_ms || 'N/A'}ms, INP: ${lead.inp_ms || 'N/A'}ms, CLS: ${lead.cls || 'N/A'})`);
  } else {
    facts.push(`• Site: Não possui website próprio`);
  }

  const instagram = lead.has_instagram ? 'Presente' : 'Ausente';
  const facebook = lead.has_facebook ? 'Presente' : 'Ausente';
  facts.push(`• Instagram: ${instagram} | Facebook: ${facebook}`);

  if (lead.social_last_post_days != null) {
    facts.push(`• Última postagem em redes sociais: há ${lead.social_last_post_days} dias`);
  }

  facts.push(`• DMS (Maturidade Digital): ${lead.dms}/100`);
  facts.push(`• COS (Oportunidade Comercial): ${lead.cos}/100`);
  facts.push(`• Prioridade de prospecção: ${lead.priority}`);

  return facts.join('\n');
}

function buildInferences(lead) {
  const paragraphs = [];

  if (!lead.has_website) {
    paragraphs.push(
      'A empresa não possui presença web própria, o que representa uma limitação significativa na captação de clientes digitais. ' +
      'Potenciais clientes que buscam serviços no Google não encontram um canal direto para conhecer a empresa, seus serviços e diferenciais. ' +
      'Isso provavelmente resulta em perda de oportunidades para concorrentes que possuem sites otimizados.'
    );
  } else if (lead.pagespeed_score != null && lead.pagespeed_score < 50) {
    paragraphs.push(
      `O site apresenta performance crítica no mobile (PageSpeed Score: ${lead.pagespeed_score}/100). ` +
      `Com um LCP de ${lead.lcp_ms}ms, a página demora significativamente para carregar o conteúdo principal, ` +
      'o que segundo dados do Google pode resultar em até 53% de abandono por usuários mobile. ' +
      'Isso impacta diretamente o posicionamento nos resultados de busca e a taxa de conversão de visitantes.'
    );
  } else if (lead.pagespeed_score != null && lead.pagespeed_score < 70) {
    paragraphs.push(
      `O site apresenta performance moderada (PageSpeed Score: ${lead.pagespeed_score}/100). ` +
      'Embora funcional, há espaço considerável para otimização, especialmente em Core Web Vitals. ' +
      'Melhorias nessas métricas podem impactar positivamente tanto o SEO quanto a experiência do usuário.'
    );
  } else if (lead.pagespeed_score != null) {
    paragraphs.push(
      `O site apresenta boa performance técnica (PageSpeed Score: ${lead.pagespeed_score}/100). ` +
      'As métricas de Core Web Vitals estão dentro dos padrões recomendados pelo Google, ' +
      'o que contribui positivamente para o posicionamento orgânico.'
    );
  }

  if (lead.google_rating >= 4.0 && lead.dms < 40) {
    paragraphs.push(
      'Existe uma desconexão significativa entre a qualidade do serviço presencial (evidenciada pela alta avaliação no Google) ' +
      'e a presença digital da empresa. Clientes satisfeitos não estão sendo convertidos em defensores digitais da marca. ' +
      'Há uma oportunidade clara de alavancar a reputação offline para construir autoridade online.'
    );
  }

  if (!lead.has_instagram && !lead.has_facebook) {
    paragraphs.push(
      'A ausência completa de perfis em redes sociais limita drasticamente a capacidade de engajamento e relacionamento ' +
      'com o público-alvo. Em um mercado onde 78% dos consumidores pesquisam empresas nas redes sociais antes de comprar, ' +
      'essa lacuna representa uma desvantagem competitiva relevante.'
    );
  } else if (lead.social_last_post_days != null && lead.social_last_post_days > 60) {
    paragraphs.push(
      `As redes sociais da empresa estão desatualizadas (último post há ${lead.social_last_post_days} dias). ` +
      'Perfis inativos podem transmitir a impressão de empresa desatualizada ou até mesmo fechada, ' +
      'prejudicando a confiança de potenciais clientes.'
    );
  }

  return paragraphs.join('\n\n');
}

function buildRecommendations(lead) {
  const recs = [];

  if (!lead.has_website) {
    recs.push('🔴 PRIORITÁRIO: Desenvolvimento de Landing Page otimizada para conversão, com design responsivo e foco em captação de leads');
  }

  if (lead.has_website && lead.pagespeed_score != null && lead.pagespeed_score < 50) {
    recs.push('🔴 PRIORITÁRIO: Otimização de performance e Core Web Vitals — reescrever o site com foco em velocidade mobile');
  } else if (lead.has_website && lead.pagespeed_score != null && lead.pagespeed_score < 70) {
    recs.push('🟡 RECOMENDADO: Otimização de Core Web Vitals (LCP, INP, CLS) para melhorar posicionamento no Google');
  }

  if (!lead.has_instagram || !lead.has_facebook) {
    recs.push('🟡 RECOMENDADO: Criação e gestão de perfis em redes sociais com estratégia de conteúdo');
  }

  if (lead.social_last_post_days != null && lead.social_last_post_days > 30) {
    recs.push('🟡 RECOMENDADO: Plano de conteúdo mensal para redes sociais com calendário editorial');
  }

  if (lead.google_reviews_count < 20) {
    recs.push('🟢 SUGESTÃO: Implementação de estratégia de coleta de avaliações no Google (QR Code, follow-up pós-atendimento)');
  }

  if (lead.has_website && (!lead.has_instagram && !lead.has_facebook)) {
    recs.push('🟢 SUGESTÃO: Integração do site com redes sociais e implementação de pixel de remarketing');
  }

  if (recs.length === 0) {
    recs.push('🟢 SUGESTÃO: Manutenção e evolução contínua da presença digital — SEO avançado, marketing de conteúdo');
  }

  return recs.join('\n');
}

function buildEmailDraft(lead) {
  const firstName = lead.name.split(' ')[0];
  const isClinic = /clínica|odonto|dental|dr\.|dra\./i.test(lead.name);
  const treatment = isClinic ? 'Prezado(a) Dr(a).' : 'Prezado(a)';

  let mainGap = '';
  if (!lead.has_website) {
    mainGap = 'a ausência de um site profissional, o que pode estar limitando a captação de novos pacientes e clientes pelo digital';
  } else if (lead.pagespeed_score != null && lead.pagespeed_score < 50) {
    mainGap = 'que o site atual pode estar com performance abaixo do ideal no mobile, o que impacta diretamente no posicionamento do Google';
  } else if (!lead.has_instagram && !lead.has_facebook) {
    mainGap = 'uma oportunidade de ampliar o alcance da marca através das redes sociais, canal essencial para engajamento com o público';
  } else {
    mainGap = 'oportunidades concretas de fortalecimento da presença digital que podem trazer mais visibilidade e clientes';
  }

  return `Assunto: ${lead.name} — Oportunidade de crescimento digital

${treatment},

Meu nome é [Seu Nome], da Consultings APD. Somos uma consultoria especializada em presença digital para empresas do segmento de ${lead.category?.toLowerCase() || 'serviços'}.

Realizamos recentemente um estudo sobre o cenário digital de empresas em ${lead.city || 'sua região'}, e durante nossa análise identificamos ${mainGap}.

Com base nos dados que levantamos, acreditamos que com adjustments estratégicos pontuais, a ${lead.name} pode ampliar significativamente sua captação de clientes pelo digital. Preparamos um diagnóstico gratuito e personalizado que gostaríamos de compartilhar com você — sem compromisso.

Teria disponibilidade para uma conversa rápida de 15 minutos esta semana? Posso apresentar os dados e algumas recomendações práticas.

Fico à disposição.

Atenciosamente,
[Seu Nome]
Consultings APD
[Telefone] | [E-mail]`;
}

module.exports = { generateDiagnostic };
