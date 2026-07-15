const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const userDataDir = 'C:\\Users\\55119\\AppData\\Local\\Google\\Chrome\\User Data';
  const executablePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';

  console.log('Iniciando navegador com perfil local...');
  
  // Lança o Chrome do usuário (visível para que ele veja o que está acontecendo)
  const context = await chromium.launchPersistentContext(userDataDir, {
    executablePath,
    headless: false, // para o usuário poder interagir se o Google Password Manager pedir
    viewport: null,
    args: ['--start-maximized']
  });

  const page = await context.newPage();
  console.log('Navegando para o Supabase...');
  await page.goto('https://supabase.com/dashboard/sign-in', { waitUntil: 'domcontentloaded' });

  // Tenta clicar no botão do GitHub caso esteja logado pelo GitHub, 
  // caso contrário, se tiver auto-fill de senha, tenta submeter
  try {
     await page.waitForTimeout(3000);
     if (page.url().includes('sign-in')) {
         console.log('Tentando auto-login se a senha estiver salva...');
         const passwordInput = await page.$('input[type="password"]');
         if (passwordInput) {
             const val = await passwordInput.inputValue();
             if (val) {
                 await page.click('button[type="submit"]');
             }
         } else {
             // Pode ser GitHub
             const githubBtn = await page.$('button:has-text("GitHub")');
             if (githubBtn) await githubBtn.click();
         }
     }
  } catch(e) {}

  console.log('Aguardando login completo (redirecionamento para dashboard)...');
  await page.waitForURL('**/dashboard/projects', { timeout: 60000 }); // Dá 60s para o usuário logar se precisar

  console.log('Logado com sucesso! Iniciando criação do projeto...');
  
  // Estamos na página de projetos. Criar novo projeto.
  // Pode ser que tenha uma organização padrão
  await page.goto('https://supabase.com/dashboard/new/project', { waitUntil: 'networkidle' });
  
  // Seleciona a primeira organização (geralmente obrigatória)
  try {
     await page.click('button:has-text("Choose organization")');
     await page.click('[role="menuitem"]:first-child');
  } catch(e) {}

  console.log('Preenchendo detalhes do projeto...');
  await page.fill('input[name="name"]', 'Consultings APD');
  
  // Senha do banco de dados gerada aleatoriamente
  const dbPassword = 'Consultings' + Math.random().toString(36).substring(2, 10) + 'Apd#2026';
  await page.fill('input[type="password"]', dbPassword);
  
  await page.click('button:has-text("Create new project")');
  
  console.log('Projeto criado! Aguardando o provisionamento (isso pode levar 2-3 minutos)...');
  
  // O Supabase redireciona para a página do projeto
  await page.waitForURL('**/dashboard/project/**', { timeout: 30000 });
  const currentUrl = page.url();
  const projectRef = currentUrl.match(/project\/([a-z0-9]+)/)[1];
  
  console.log(`Reference do projeto: ${projectRef}`);
  console.log('Aguardando API do projeto ficar pronta...');
  
  // Acessa a página de configurações de banco de dados para pegar a Connection String
  await page.goto(`https://supabase.com/dashboard/project/${projectRef}/settings/database`, { waitUntil: 'networkidle' });
  
  // Espera até a string de conexão aparecer (provisionamento concluído)
  // Como pode demorar, vamos dar um timeout longo e tentar recarregar se necessário
  let connectionString = null;
  for (let i = 0; i < 20; i++) {
     try {
       await page.waitForSelector('text=Connection string', { timeout: 10000 });
       // No UI do Supabase, o input URI Fica com postgresql://...
       const uriInput = await page.$('input[value^="postgresql://"]');
       if (uriInput) {
           connectionString = await uriInput.inputValue();
           break;
       }
     } catch(e) {
       console.log('Ainda provisionando... verificando novamente.');
       await page.reload();
     }
  }

  if (connectionString) {
      // Substitui o placeholder [YOUR-PASSWORD] pela senha gerada
      connectionString = connectionString.replace('[YOUR-PASSWORD]', dbPassword);
      console.log('Connection String obtida com sucesso!');
      
      const envPath = path.join(__dirname, '..', '.env');
      let envContent = fs.existsSync(envPath) ? fs.readFileSync(envPath, 'utf8') : '';
      envContent += `\nDATABASE_URL=${connectionString}\n`;
      fs.writeFileSync(envPath, envContent);
      console.log('✅ DATABASE_URL salva no .env local!');
      
      // Salva num txt pra mostrar
      fs.writeFileSync(path.join(__dirname, '..', 'supabase_result.txt'), 'SUCESSO');
  } else {
      console.log('Não foi possível capturar a Connection String.');
  }

  await context.close();
})();
