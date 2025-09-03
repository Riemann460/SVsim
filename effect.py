from typing import Any, Dict, Optional
from enum import Enum


class Effect:
    """카드 별 효과 개별 인스턴스"""
    def __init__(self, **kwargs):
        """Effect 클래스의 생성자입니다."""
        self.attributes = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        """Effect 객체를 대표하는 문자열을 반환합니다."""
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
        """효과의 속성을 업데이트합니다."""
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
        """키를 사용하여 효과의 속성 값을 가져옵니다."""
        return getattr(self, key, default)