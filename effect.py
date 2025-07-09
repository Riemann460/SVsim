from typing import Any, Dict, Optional
from enum import Enum


class Effect:
    def __init__(self, **kwargs):
        self.attributes = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        parts = []
        sorted_keys = sorted(self.attributes.keys(), key=lambda k: k != 'type')

        for key in sorted_keys:
            value = self.attributes[key]

            if isinstance(value, Enum):
                formatted_value = f"{type(value).__name__}.{value.name}"
            else:
                formatted_value = repr(value)

            parts.append(f"'{key}': {formatted_value}")

        return "{"+f"{', '.join(parts)}"+"}"

    def update(self, **kwargs):
        self.attributes.update(kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """효과를 딕셔너리 형태로 변환 (필요시 사용)"""
        keys = self.attributes.keys()
        data = {}

        if 'type' in self.attributes.keys():
            data['type'] = self.type.name
            keys = [key for key in self.attributes.keys() if key != 'type']

        for key in keys:
            value = self.attributes[key]
            if isinstance(value, Enum):
                data[key] = value.name
            else:
                data[key] = value

        return data

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)
