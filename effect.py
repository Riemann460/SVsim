from typing import Any, Dict, Optional
from enum import Enum


class Effect:
    """카드 별 효과 개별 인스턴스"""
    def __init__(self, **kwargs):
        """Effect 클래스의 생성자입니다."""
        self.attributes = kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

        # 'CHOOSE' 타입에 대한 유효성 검사 추가
        if self.get('type') and self.get('type').name == 'CHOOSE':
            if 'choices' not in self.attributes or not isinstance(self.attributes['choices'], list):
                raise ValueError("CHOOSE effect must have a 'choices' list.")
            for choice in self.attributes['choices']:
                if not isinstance(choice, Effect):
                    raise TypeError("All items in 'choices' must be Effect objects.")

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
        """효과를 딕셔너리 형태로 재귀적으로 변환합니다."""
        data = {}
        for key, value in self.attributes.items():
            if isinstance(value, Enum):
                data[key] = value.name
            elif isinstance(value, Effect):
                data[key] = value.to_dict()  # 재귀 호출
            elif isinstance(value, list):
                # 리스트 내의 Effect 객체들도 변환
                data[key] = [
                    item.to_dict() if isinstance(item, Effect) else item
                    for item in value
                ]
            else:
                data[key] = value
        return data

    def get(self, key: str, default: Any = None) -> Any:
        """키를 사용하여 효과의 속성 값을 가져옵니다."""
        return getattr(self, key, default)