from __future__ import annotations

from dataclasses import dataclass, asdict
from core.ml.models.type_model import TypeModel
from pathlib import Path
from typing import Any
import json

import torch


@dataclass
class ModelArtifactMetadata:
    model_name: TypeModel
    input_dim: int
    hidden_dim: int
    output_dim: int


@dataclass
class LoadedModelArtifact:
    metadata: ModelArtifactMetadata
    state_dict: dict[str, Any]


class ModelArtifact:
    MODEL_FILE_NAME = "model.pt"
    METADATA_FILE_NAME = "metadata.json"

    @classmethod
    def save(
        cls,
        artifact_dir: str | Path,
        model: torch.nn.Module,
        metadata: ModelArtifactMetadata,
    ) -> None:
        artifact_path = Path(artifact_dir)
        artifact_path.mkdir(parents=True, exist_ok=True)

        torch.save(model.state_dict(), artifact_path / cls.MODEL_FILE_NAME)

        with open(artifact_path / cls.METADATA_FILE_NAME, "w", encoding="utf-8") as f:
            json.dump(asdict(metadata), f, indent=2)

    @classmethod
    def load(cls, artifact_dir: str | Path, map_location: str = "cpu") -> LoadedModelArtifact:
        artifact_path = Path(artifact_dir)

        if artifact_path.exists():
            with open(artifact_path / cls.METADATA_FILE_NAME, "r", encoding="utf-8") as f:
                metadata_raw = json.load(f)

            metadata = ModelArtifactMetadata(**metadata_raw)
            state_dict = torch.load(artifact_path / cls.MODEL_FILE_NAME, map_location=map_location)
        else:
            raise FileNotFoundError(f"Model artifact not found in {artifact_path}.")

        return LoadedModelArtifact(
            metadata=metadata,
            state_dict=state_dict,
        )