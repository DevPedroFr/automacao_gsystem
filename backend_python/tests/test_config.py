import sys
from pathlib import Path


def test_settings_loads_api_keys_from_env_file():
    backend_dir = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(backend_dir))

    import importlib
    import app.core.config as config_module

    importlib.reload(config_module)

    settings = config_module.settings

    assert settings.GOOGLE_PLACES_API_KEY
    assert settings.GOOGLE_PLACES_API_KEY != "your_google_places_api_key_here"
    assert settings.ANTHROPIC_API_KEY
    assert settings.ANTHROPIC_API_KEY != "your_anthropic_api_key_here"
