import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from app.services.lp_prompt_engine import LPPromptEngine
from app.services.site_generator_service import SiteGeneratorService
from app.integrations.google_places import GooglePlacesIntegration


class PhotoPlacementEngineTests(unittest.TestCase):
    def setUp(self):
        self.sample_photos = [
            f"https://lh3.googleusercontent.com/place-photos/SAMPLE_HASH_{i}=s4800-w640-h480"
            for i in range(1, 9)
        ]

    def test_allocate_photos_distribution(self):
        plan = LPPromptEngine.allocate_photos(self.sample_photos)
        self.assertEqual(plan["count"], 8)
        self.assertEqual(plan["hero"], self.sample_photos[0])
        self.assertEqual(len(plan["services"]), 3)
        self.assertEqual(plan["services"], self.sample_photos[1:4])
        self.assertEqual(len(plan["structure_gallery"]), 6)
        self.assertEqual(plan["structure_gallery"], self.sample_photos[1:7])
        self.assertEqual(plan["facade"], self.sample_photos[4])

    def test_allocate_photos_single_photo(self):
        single = ["https://lh3.googleusercontent.com/place-photos/SINGLE=s4800-w640-h480"]
        plan = LPPromptEngine.allocate_photos(single)
        self.assertEqual(plan["count"], 1)
        self.assertEqual(plan["hero"], single[0])
        self.assertEqual(plan["facade"], single[0])
        self.assertEqual(plan["services"], [])
        self.assertEqual(plan["structure_gallery"], [])

    def test_get_photo_token_map(self):
        token_map = LPPromptEngine.get_photo_token_map(self.sample_photos)
        self.assertIn("__PHOTO_HERO__", token_map)
        self.assertIn("__PHOTO_FACADE__", token_map)
        self.assertIn("__PHOTO_SERVICE_1__", token_map)
        self.assertIn("__PHOTO_GALLERY_1__", token_map)
        self.assertEqual(token_map["__PHOTO_HERO__"], self.sample_photos[0])

    def test_hydrate_photo_tokens_and_protect_header(self):
        raw_html = f"""
        <!DOCTYPE html><html>
        <header><div class="logo"><img src="{self.sample_photos[0]}" alt="Leaked" /></div></header>
        <section id="hero"><img src="__PHOTO_HERO__" alt="Hero" /></section>
        <section id="solucoes"><img src="__PHOTO_SERVICE_1__" alt="S1" /></section>
        <section id="localizacao"><img src="__PHOTO_FACADE__" alt="Loc" /></section>
        </html>
        """
        hydrated = SiteGeneratorService.hydrate_photo_tokens(raw_html, self.sample_photos)

        # 1. Tokens substituídos corretamente
        self.assertIn(self.sample_photos[0], hydrated)
        self.assertIn(self.sample_photos[1], hydrated)
        self.assertIn(self.sample_photos[4], hydrated)

        # 2. Logotipo protegido (foto vazada no header deve ser removida)
        header_part = hydrated.split("</header>")[0]
        self.assertNotIn("src=\"" + self.sample_photos[0] + "\"", header_part)

    def test_semantic_landing_page_renders_all_photo_sections(self):
        lead_data = {
            "name": "Depósito de Materiais Teste",
            "category": "Materiais para Construção",
            "phone": "(11) 99999-8888",
            "address": "Rua das Obras, 100, Mogi das Cruzes - SP",
            "google_rating": 4.9,
            "google_reviews_count": 95,
        }

        html = SiteGeneratorService._build_semantic_landing_page(
            lead_data=lead_data,
            brand_colors={},
            owners=[],
            logo_url=None,
            gallery_urls=self.sample_photos,
        )

        # Hero com foto de destaque
        self.assertIn(self.sample_photos[0], html)
        self.assertIn("Unidade Oficial • Atendimento Aberto", html)

        # Serviços com foto nos cards
        self.assertIn(self.sample_photos[1], html)

        # Galeria dedicada de estrutura
        self.assertIn('id="estrutura"', html)
        self.assertIn("Conheça Nosso Espaço", html)

        # Localização com foto da fachada
        self.assertIn(self.sample_photos[4], html)
        self.assertIn("Fachada & Entrada Principal", html)

        # Navbar protegida
        header_part = html.split("</header>")[0]
        self.assertNotIn("lh3.googleusercontent.com", header_part)

    def test_niche_detection_estetica_vs_medicina(self):
        # Virtuosa Clínica de Estética DEVE ser detectada como estetica, NÃO medicina
        niche = LPPromptEngine.detect_niche("Virtuosa Clínica de Estética", "Clínica de Estética")
        self.assertEqual(niche, "estetica")

        # Clínica Médica deve ser detectada como medicina
        niche_med = LPPromptEngine.detect_niche("Clínica Médica Integrada Santa Clara", "Saúde e Medicina")
        self.assertEqual(niche_med, "medicina")

        # Odonto deve ser odontologia
        niche_odonto = LPPromptEngine.detect_niche("Clínica Odontológica Sorriso Perfeito", "Dentista")
        self.assertEqual(niche_odonto, "odontologia")

    def test_contrast_text_color_calculations(self):
        # Cores claras exigem texto escuro (#090D16)
        self.assertEqual(LPPromptEngine.get_contrast_text_color("#38BDF8"), "#090D16")  # Azul céu claro
        self.assertEqual(LPPromptEngine.get_contrast_text_color("#F59E0B"), "#090D16")  # Âmbar/Dourado claro
        self.assertEqual(LPPromptEngine.get_contrast_text_color("#FFFFFF"), "#090D16")  # Branco

        # Cores escuras ou saturadas exigem texto claro (#FFFFFF)
        self.assertEqual(LPPromptEngine.get_contrast_text_color("#EF4444"), "#FFFFFF")  # Vermelho
        self.assertEqual(LPPromptEngine.get_contrast_text_color("#1E3A8A"), "#FFFFFF")  # Azul marinho escuro
        self.assertEqual(LPPromptEngine.get_contrast_text_color("#0F172A"), "#FFFFFF")  # Slate escuro

    def test_street_photo_rejection_in_brand_colors(self):
        from app.services.enrichment_service import EnrichmentService
        # Fotos do Google Places (rua/fachada) NUNCA devem ter cores extraídas pelo Pillow
        street_url = "https://lh3.googleusercontent.com/places/AAkxkeL123=s1600"
        colors = EnrichmentService.extract_brand_colors(street_url)
        self.assertIsNone(colors)

    def test_landing_page_wcag_color_contrast_and_badges(self):
        lead_data = {
            "name": "Virtuosa Clínica de Estética",
            "category": "Clínica de Estética",
            "phone": "(11) 98581-9552",
            "address": "R. Dr. Ricardo Vilela, 1380 - Centro, Mogi das Cruzes - SP",
            "google_rating": 4.8,
            "google_reviews_count": 344,
        }

        html = SiteGeneratorService._build_semantic_landing_page(
            lead_data=lead_data,
            brand_colors={},
            owners=[],
            logo_url=None,
            gallery_urls=self.sample_photos,
        )

        # 1. Nicho correto: Estética (não medicina)
        self.assertIn("Estética Avançada & Bem-Estar", html)
        self.assertNotIn("Medicina Integrada & Consultas Especializadas", html)

        # 2. Tailwind Config deve conter on-primary
        self.assertIn('"on-primary":', html)

        # 3. Botões primários NUNCA devem ter classe 'text-background'
        self.assertNotIn("bg-primary text-background", html)
        self.assertIn("bg-primary text-on-primary", html)

        # 4. Hero Badge deve usar bg-primary/10 e text-primary (nunca bg-surface-container)
        self.assertIn("bg-primary/10 border border-primary/30", html)
        self.assertIn("text-primary", html)

    def test_download_lead_images_zip_generation(self):
        import json
        import zipfile
        import io
        from app.api.diagnostics import download_lead_images
        from unittest.mock import MagicMock, AsyncMock, patch

        mock_db = MagicMock()
        mock_lead = MagicMock()
        mock_lead.id = "lead-test-123"
        mock_lead.name = "Clínica Teste"
        mock_lead.category = "Estética"
        mock_lead.phone = "(11) 99999-9999"
        mock_lead.address = "Rua Teste, 100"
        mock_lead.city = "São Paulo"
        mock_lead.google_rating = 4.9
        mock_lead.google_reviews_count = 120
        mock_lead.gallery_urls = json.dumps(["https://fake.url/img1.jpg", "https://fake.url/img2.jpg"])
        mock_lead.image_url = "https://fake.url/img1.jpg"
        mock_lead.logo_url = None

        mock_diag = MagicMock()
        mock_diag.stitch_prompt = "PROMPT DE TESTE ELITE CRO"

        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_lead, mock_diag]

        fake_resp = MagicMock()
        fake_resp.status_code = 200
        fake_resp.headers = {"content-type": "image/jpeg"}
        fake_resp.content = b"FAKE_JPEG_BYTES"

        async def run_test():
            with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
                mock_get.return_value = fake_resp
                response = await download_lead_images(lead_id="lead-test-123", db=mock_db)
                self.assertEqual(response.media_type, "application/zip")
                self.assertIn("attachment; filename=", response.headers.get("Content-Disposition", ""))

                # Verificar conteúdo do ZIP em memória
                body = response.body
                with zipfile.ZipFile(io.BytesIO(body)) as zf:
                    namelist = zf.namelist()
                    self.assertIn("LEIA-ME_COMO_USAR.txt", namelist)
                    self.assertIn("prompt_para_desenvolvimento.txt", namelist)
                    self.assertTrue(any(name.startswith("imagens/") for name in namelist))

                    readme = zf.read("LEIA-ME_COMO_USAR.txt").decode("utf-8")
                    self.assertIn("CLÍNICA TESTE", readme.upper())

                    prompt = zf.read("prompt_para_desenvolvimento.txt").decode("utf-8")
                    self.assertEqual(prompt, "PROMPT DE TESTE ELITE CRO")

        asyncio.run(run_test())


if __name__ == "__main__":
    unittest.main()
