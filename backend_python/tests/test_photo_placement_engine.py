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


if __name__ == "__main__":
    unittest.main()
