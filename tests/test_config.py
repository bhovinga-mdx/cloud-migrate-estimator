"""Tests for configuration loading."""

from pathlib import Path

from estimator.config import (
    load_aws_baselines,
    load_rate_card,
    load_settings,
    validate_config,
)

# Default config directory (project root / config)
CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


class TestLoadRateCard:
    def test_loads_successfully(self):
        rc = load_rate_card(CONFIG_DIR)
        assert len(rc.roles) > 0

    def test_has_expected_roles(self):
        rc = load_rate_card(CONFIG_DIR)
        assert "solutions_architect" in rc.roles
        assert "cloud_engineer" in rc.roles

    def test_rates_are_positive(self):
        rc = load_rate_card(CONFIG_DIR)
        for role_key, role in rc.roles.items():
            assert role.hourly_rate > 0, f"{role_key} has invalid rate"


class TestLoadAWSBaselines:
    def test_loads_successfully(self):
        baselines = load_aws_baselines(CONFIG_DIR)
        assert len(baselines.sizes) > 0

    def test_has_expected_sizes(self):
        baselines = load_aws_baselines(CONFIG_DIR)
        for size in ("S", "M", "L", "XL"):
            assert size in baselines.sizes

    def test_cost_ranges_valid(self):
        baselines = load_aws_baselines(CONFIG_DIR)
        for size_key, size in baselines.sizes.items():
            assert size.monthly_cost_low < size.monthly_cost_high, f"{size_key} has invalid range"


class TestLoadSettings:
    def test_loads_successfully(self):
        settings = load_settings(CONFIG_DIR)
        assert settings.models.extract == "claude-opus-4-6"
        assert settings.pipeline.max_retries >= 0

    def test_defaults_applied(self):
        settings = load_settings(CONFIG_DIR)
        assert settings.output.save_intermediates is True


class TestValidateConfig:
    def test_valid_config(self):
        errors = validate_config(CONFIG_DIR)
        assert errors == []

    def test_missing_directory(self, tmp_path):
        errors = validate_config(tmp_path / "nonexistent")
        assert len(errors) > 0
