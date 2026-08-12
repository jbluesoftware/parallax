from dataclasses import dataclass


@dataclass
class ModelInfo:
    name: str
    description: str = ""
