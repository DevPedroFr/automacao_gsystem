import re
import math
import json
import logging
from typing import Optional, List, Dict, Any
from io import BytesIO
from collections import Counter

import httpx
try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    Image = None
    HAS_PILLOW = False

from app.core.config import settings

logger = logging.getLogger(__name__)


class EnrichmentService:
    """
    Serviço de Enriquecimento Avançado de Leads:
    1. Identidade visual e paleta de cores (Pillow).
    2. Investigação de sócios/fundadores (BrasilAPI / QSA + Instagram Bio + Google Reviews).
    3. Coleta de ativos visuais (Logo e Galeria).
    """

    @staticmethod
    def extract_brand_colors(image_bytes_or_path: Any) -> Optional[Dict[str, Any]]:
        """
        Analisa uma imagem de logotipo e extrai a cor primária de destaque da marca.
        Fotos de estabelecimentos/rua (Google Places) são rejeitadas para evitar paletas incoerentes.
        """
        if not HAS_PILLOW or not image_bytes_or_path:
            return None

        # Rejeitar fotos do Google Places (lh3/googleusercontent) pois são fotos de rua/fachada
        if isinstance(image_bytes_or_path, str) and ("lh3.googleusercontent.com" in image_bytes_or_path or "googleusercontent" in image_bytes_or_path):
            return None

        try:
            if isinstance(image_bytes_or_path, str) and (image_bytes_or_path.startswith("http://") or image_bytes_or_path.startswith("https://")):
                with httpx.Client(timeout=8.0) as client:
                    resp = client.get(image_bytes_or_path)
                    resp.raise_for_status()
                    img = Image.open(BytesIO(resp.content))
            elif isinstance(image_bytes_or_path, bytes):
                img = Image.open(BytesIO(image_bytes_or_path))
            else:
                img = Image.open(image_bytes_or_path)

            img = img.convert("RGBA")
            img = img.resize((100, 100))
            pixels = list(img.getdata())

            # Filtrar pixels transparentes, muito pretos, muito brancos ou cinzas neutros
            colored_pixels = []
            for r, g, b, a in pixels:
                if a < 128:
                    continue  # Transparente
                if (r < 30 and g < 30 and b < 30) or (r > 235 and g > 235 and b > 235):
                    continue  # Preto e branco puro
                max_c = max(r, g, b)
                min_c = min(r, g, b)
                if (max_c - min_c) < 25:
                    continue  # Tons de cinza
                colored_pixels.append((r, g, b))

            def to_hex(c):
                return "#{:02x}{:02x}{:02x}".format(c[0], c[1], c[2])

            if not colored_pixels:
                return None

            counts = Counter(colored_pixels)
            dominant_rgb = counts.most_common(1)[0][0]
            primary_hex = to_hex(dominant_rgb)

            # Luminância relativa para contraste do texto do botão primário
            lum = (dominant_rgb[0] * 0.299 + dominant_rgb[1] * 0.587 + dominant_rgb[2] * 0.114) / 255.0
            on_primary = "#090D16" if lum > 0.40 else "#FFFFFF"

            return {
                "background": "#0B101E",
                "primary": primary_hex,
                "secondary": "#141D30",
                "text": "#FFFFFF",
                "on_primary": on_primary,
                "is_dark_theme": True,
            }
        except Exception as e:
            logger.warning(f"Erro ao extrair paleta de cores via Pillow: {e}")
            return None

    @staticmethod
    def _default_palette() -> Dict[str, Any]:
        return {
            "background": "#0F131C",
            "primary": "#3B82F6",
            "secondary": "#1E293B",
            "text": "#FFFFFF",
            "on_primary": "#FFFFFF",
            "is_dark_theme": True,
        }

    @staticmethod
    async def get_partners_from_cnpj(cnpj: str) -> List[Dict[str, str]]:
        """
        Consulta o Quadro de Sócios e Administradores (QSA) na BrasilAPI.
        Retorna lista de sócios formatada com nome e cargo.
        """
        clean_cnpj = re.sub(r"\D", "", cnpj)
        if len(clean_cnpj) != 14:
            return []

        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                url = f"https://brasilapi.com.br/api/cnpj/v1/{clean_cnpj}"
                res = await client.get(url)
                if res.status_code == 200:
                    data = res.json()
                    qsa = data.get("qsa", [])
                    partners = []
                    for item in qsa:
                        name = item.get("nome_socio")
                        role = item.get("qualificacao_socio", "Sócio")
                        if name:
                            # Capitalizar nome no padrão visual agradável
                            pretty_name = " ".join(part.capitalize() for part in name.split())
                            partners.append({"name": pretty_name, "role": role})
                    return partners
        except Exception as e:
            logger.warning(f"Erro ao consultar sócios na BrasilAPI para CNPJ {cnpj}: {e}")
        return []

    @staticmethod
    def extract_cnpj_from_text(text: str) -> Optional[str]:
        """Procura padrão de CNPJ formatado ou numérico dentro de um texto."""
        if not text:
            return None
        # Padrão com pontuação: XX.XXX.XXX/XXXX-XX
        match = re.search(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b", text)
        if match:
            return match.group(0)
        return None

    @staticmethod
    def detect_owners_from_bio_and_reviews(
        bio: Optional[str] = None,
        reviews_or_answers: Optional[str] = None,
        company_name: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Heurística rápida para extrair nomes de fundadores/doutores citados na bio do Instagram
        ou em respostas a avaliações do Google Maps.
        """
        owners = []
        combined_text = f"{bio or ''} {reviews_or_answers or ''}"
        
        # Padrões comuns no Brasil
        patterns = [
            r"(?:Dra?\.|Doutor(?:a)?)\s+([A-ZÁÉÍÓÚÂÊÔÃÕ][a-záéíóúâêôãõ]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕ][a-záéíóúâêôãõ]+){1,3})",
            r"(?:Fundad[oa]r?(?:a)?\s+por|Idealizad[oa]r?(?:a)?|S[oó]ci[oa]s?|Direç[aã]o(?:\s+cl[ií]nica)?):\s*([A-ZÁÉÍÓÚÂÊÔÃÕ][a-záéíóúâêôãõ]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕ][a-záéíóúâêôãõ]+){1,3})",
            r"(?:Por|Com)\s+@?([A-Za-z0-9_\.]+)\s+e\s+@?([A-Za-z0-9_\.]+)",
        ]

        for pat in patterns:
            matches = re.findall(pat, combined_text, flags=re.IGNORECASE)
            for m in matches:
                if isinstance(m, tuple):
                    for sub in m:
                        if sub and len(sub) > 2 and sub not in [o["name"] for o in owners]:
                            owners.append({"name": sub.strip(), "role": "Fundador / Responsável"})
                elif isinstance(m, str) and len(m) > 2:
                    if m not in [o["name"] for o in owners]:
                        owners.append({"name": m.strip(), "role": "Fundador / Responsável"})

        return owners[:3]

    @staticmethod
    async def enrich_lead_data(
        lead_name: str,
        city: str = "",
        website_url: Optional[str] = None,
        instagram_bio: Optional[str] = None,
        logo_url_or_path: Optional[str] = None,
        reviews_text: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executa a pipeline completa de enriquecimento:
        - Cores da marca
        - Detecção de CNPJ & Sócios
        - Identificação de donos pela bio/reviews
        """
        brand_colors = None
        if logo_url_or_path:
            brand_colors = EnrichmentService.extract_brand_colors(logo_url_or_path)

        partners = []
        found_cnpj = None

        # 1. Se tem website, tenta extrair CNPJ do site
        if website_url:
            try:
                async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
                    resp = await client.get(website_url)
                    if resp.status_code == 200:
                        found_cnpj = EnrichmentService.extract_cnpj_from_text(resp.text)
            except Exception:
                pass

        # 2. Se achou CNPJ, busca o Quadro de Sócios Oficial (QSA)
        if found_cnpj:
            partners = await EnrichmentService.get_partners_from_cnpj(found_cnpj)

        # 3. Se não achou por CNPJ, tenta extrair da bio e reviews
        if not partners:
            partners = EnrichmentService.detect_owners_from_bio_and_reviews(
                bio=instagram_bio,
                reviews_or_answers=reviews_text,
                company_name=lead_name,
            )

        return {
            "cnpj": found_cnpj,
            "brand_colors": brand_colors,
            "owners": partners,
        }
