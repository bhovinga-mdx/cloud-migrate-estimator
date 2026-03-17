"""Configuration loading from TOML files."""

import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel

# Default config directory relative to package
_PACKAGE_DIR = Path(__file__).resolve().parent
_DEFAULT_CONFIG_DIR = _PACKAGE_DIR.parent.parent / "config"


class RoleConfig(BaseModel):
    title: str
    hourly_rate: int


class RateCardConfig(BaseModel):
    roles: dict[str, RoleConfig]


class TShirtSizeConfig(BaseModel):
    label: str
    description: str
    monthly_cost_low: int
    monthly_cost_high: int
    typical_workload_count: str


class AWSBaselinesConfig(BaseModel):
    sizes: dict[str, TShirtSizeConfig]


class ModelsConfig(BaseModel):
    extract: str = "claude-opus-4-6"
    architect: str = "claude-sonnet-4-6"
    estimate: str = "claude-opus-4-6"
    gaps: str = "claude-sonnet-4-6"


class PipelineConfig(BaseModel):
    max_retries: int = 1
    max_transcript_chars: int = 400_000


class OutputConfig(BaseModel):
    output_dir: str = "estimates"
    save_intermediates: bool = True


class SettingsConfig(BaseModel):
    models: ModelsConfig = ModelsConfig()
    pipeline: PipelineConfig = PipelineConfig()
    output: OutputConfig = OutputConfig()


def _load_toml(path: Path) -> dict[str, Any]:
    with open(path, "rb") as f:
        return tomllib.load(f)


def load_rate_card(config_dir: Path | None = None) -> RateCardConfig:
    config_dir = config_dir or _DEFAULT_CONFIG_DIR
    data = _load_toml(config_dir / "rate_card.toml")
    return RateCardConfig(**data)


def load_aws_baselines(config_dir: Path | None = None) -> AWSBaselinesConfig:
    config_dir = config_dir or _DEFAULT_CONFIG_DIR
    data = _load_toml(config_dir / "aws_baselines.toml")
    return AWSBaselinesConfig(**data)


def load_settings(config_dir: Path | None = None) -> SettingsConfig:
    config_dir = config_dir or _DEFAULT_CONFIG_DIR
    data = _load_toml(config_dir / "settings.toml")
    return SettingsConfig(**data)


def validate_config(config_dir: Path | None = None) -> list[str]:
    """Validate all config files. Returns list of errors (empty = valid)."""
    errors: list[str] = []
    config_dir = config_dir or _DEFAULT_CONFIG_DIR

    for name, loader in [
        ("rate_card.toml", load_rate_card),
        ("aws_baselines.toml", load_aws_baselines),
        ("settings.toml", load_settings),
    ]:
        path = config_dir / name
        if not path.exists():
            errors.append(f"Missing config file: {path}")
            continue
        try:
            loader(config_dir)
        except Exception as e:
            errors.append(f"Invalid {name}: {e}")

    return errors
