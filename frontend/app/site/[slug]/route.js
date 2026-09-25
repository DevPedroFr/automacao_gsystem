import fs from 'fs';
import path from 'path';

export const dynamic = 'force-dynamic';

export async function GET(request, { params }) {
  const { slug } = params;
  const normalizedSlug = slug.replace(/\.html$/, '');
  const filePath = path.join(process.cwd(), 'public', `${normalizedSlug}.html`);

  if (fs.existsSync(filePath)) {
    const html = fs.readFileSync(filePath, 'utf-8');
    return new Response(html, {
      status: 200,
      headers: {
        'Content-Type': 'text/html; charset=utf-8',
        'Cache-Control': 'public, max-age=3600, s-maxage=3600',
      },
    });
  }

  return new Response(
    `<!DOCTYPE html>
    <html lang="pt-BR">
    <head><meta charset="utf-8"/><title>Site não encontrado</title></head>
    <body style="font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; background: #0b0f19; color: #fff;">
      <div style="text-align: center;">
        <h1 style="font-size: 2rem; margin-bottom: 1rem;">Site não encontrado</h1>
        <p style="color: #94a3b8;">A Landing Page solicitada ainda não foi publicada.</p>
      </div>
    </body>
    </html>`,
    {
      status: 404,
      headers: { 'Content-Type': 'text/html; charset=utf-8' },
    }
  );
}
