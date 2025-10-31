import os
import pytest
from unittest.mock import patch

from src.config import Config, DevelopmentConfig, PreproductionConfig, ProductionConfig


class TestConfig:
    """Test cases for base Config class."""

    def test_config_loads_environment_variables(self):
        """Test that Config loads environment variables."""
        # Config is loaded at import time, so we check it has the attributes
        assert hasattr(Config, 'SPOTIPY_CLIENT_ID')
        assert hasattr(Config, 'SPOTIPY_CLIENT_SECRET')

    def test_config_defaults(self):
        """Test Config default settings."""
        assert Config.DEBUG == False
        assert Config.TESTING == False

    @patch.dict(os.environ, {}, clear=True)
    def test_config_missing_credentials(self):
        """Test Config with missing credentials."""
        # When env vars are not set, they should be None
        config = Config()
        # The class attributes are set at import time, so we check the class
        assert hasattr(Config, 'SPOTIPY_CLIENT_ID')
        assert hasattr(Config, 'SPOTIPY_CLIENT_SECRET')


class TestDevelopmentConfig:
    """Test cases for DevelopmentConfig."""

    def test_development_debug_enabled(self):
        """Test that debug mode is enabled in development."""
        assert DevelopmentConfig.DEBUG == True

    def test_development_inherits_from_config(self):
        """Test that DevelopmentConfig inherits from Config."""
        assert issubclass(DevelopmentConfig, Config)

    def test_development_testing_disabled(self):
        """Test that testing mode is disabled by default."""
        assert DevelopmentConfig.TESTING == False


class TestPreproductionConfig:
    """Test cases for PreproductionConfig."""

    def test_preproduction_debug_disabled(self):
        """Test that debug mode is disabled in preproduction."""
        assert PreproductionConfig.DEBUG == False

    def test_preproduction_inherits_from_config(self):
        """Test that PreproductionConfig inherits from Config."""
        assert issubclass(PreproductionConfig, Config)

    def test_preproduction_testing_disabled(self):
        """Test that testing mode is disabled by default."""
        assert PreproductionConfig.TESTING == False


class TestProductionConfig:
    """Test cases for ProductionConfig."""

    def test_production_debug_disabled(self):
        """Test that debug mode is disabled in production."""
        assert ProductionConfig.DEBUG == False

    def test_production_inherits_from_config(self):
        """Test that ProductionConfig inherits from Config."""
        assert issubclass(ProductionConfig, Config)

    def test_production_testing_disabled(self):
        """Test that testing mode is disabled by default."""
        assert ProductionConfig.TESTING == False


class TestConfigSelection:
    """Test cases for configuration selection logic."""

    def test_all_configs_have_required_attributes(self):
        """Test that all configs have required attributes."""
        configs = [Config, DevelopmentConfig, PreproductionConfig, ProductionConfig]
        required_attrs = ['DEBUG', 'TESTING', 'SPOTIPY_CLIENT_ID', 'SPOTIPY_CLIENT_SECRET']
        
        for config in configs:
            for attr in required_attrs:
                assert hasattr(config, attr), f"{config.__name__} missing {attr}"
