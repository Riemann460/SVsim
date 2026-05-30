# 역할 정의. 카드 효과의 속성 데이터를 담고 딕셔너리와의 상호 변환을 지원하는 클래스입니다.

from typing import Any, Dict, List, Optional
from enum import Enum


def wrap_dict(val: Any) -> Any:
    """딕셔너리를 적절한 Process 또는 Effect 객체로 래핑합니다."""
    if isinstance(val, dict):
        wrapped_kwargs = {k: wrap_dict(v) for k, v in val.items()}
        if 'process' in wrapped_kwargs and isinstance(wrapped_kwargs['process'], str):
            from src.common.enums import ProcessType
            try:
                wrapped_kwargs['process'] = ProcessType[wrapped_kwargs['process']]
            except KeyError:
                pass
        if 'target' in wrapped_kwargs and isinstance(wrapped_kwargs['target'], str):
            from src.common.enums import TargetType
            try:
                wrapped_kwargs['target'] = TargetType[wrapped_kwargs['target']]
            except KeyError:
                pass
        if 'type' in wrapped_kwargs and isinstance(wrapped_kwargs['type'], str):
            from src.common.enums import EffectType
            try:
                wrapped_kwargs['type'] = EffectType[wrapped_kwargs['type']]
            except KeyError:
                pass

        if 'processes' in wrapped_kwargs or 'type' in wrapped_kwargs:
            return Effect(**wrapped_kwargs)
        elif 'process' in wrapped_kwargs:
            return Process(**wrapped_kwargs)
        else:
            return wrapped_kwargs
    elif isinstance(val, list):
        return [wrap_dict(item) for item in val]
    return val


class Process:
    """Process 클래스입니다."""
    def __init__(self, **kwargs):
        """Process 클래스의 생성자입니다."""
        wrapped = {k: wrap_dict(v) for k, v in kwargs.items()}
        self.attributes = wrapped
        for key, value in wrapped.items():
            setattr(self, key, value)

    def __getattr__(self, name):
        """부모 Effect 객체의 속성을 조회합니다."""
        if name in ['process', 'target', 'value', 'condition', 'is_split', 'extra_effect', 'processes', 'attributes']:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        if name != 'parent_effect' and hasattr(self, 'parent_effect') and self.parent_effect:
            parent = self.parent_effect
            if name in parent.__dict__:
                return parent.__dict__[name]
            if hasattr(parent, 'attributes') and name in parent.attributes:
                return parent.attributes[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __repr__(self):
        """Process 객체를 대표하는 문자열을 반환합니다."""
        parts = []
        sorted_keys = sorted(self.attributes.keys(), key=lambda k: k != 'process')
        for key in sorted_keys:
            value = self.attributes[key]
            if isinstance(value, Enum):
                formatted_value = f"{type(value).__name__}.{value.name}"
            else:
                formatted_value = repr(value)
            parts.append(f"'{key}': {formatted_value}")
        return "Process{" + f"{', '.join(parts)}" + "}"

    def get(self, key: str, default: Any = None) -> Any:
        """키를 사용하여 프로세스의 속성 값을 가져옵니다."""
        return getattr(self, key, default)

    def update(self, **kwargs):
        """프로세스의 속성을 업데이트합니다."""
        self.attributes.update(kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        """프로세스를 딕셔너리 형태로 재귀적으로 변환합니다."""
        data = {}
        for key, value in self.attributes.items():
            if isinstance(value, Enum):
                data[key] = value.name
            elif isinstance(value, (Effect, Process)):
                data[key] = value.to_dict()
            elif isinstance(value, list):
                data[key] = [
                    item.to_dict() if isinstance(item, (Effect, Process)) else item
                    for item in value
                ]
            else:
                data[key] = value
        return data


class Effect:
    """Effect 클래스입니다."""
    def __init__(self, **kwargs):
        """Effect 클래스의 생성자입니다."""
        self._in_update = False
        wrapped = {k: wrap_dict(v) for k, v in kwargs.items()}
        self.attributes = wrapped

        # processes 필드가 리스트 형태가 아닌 경우 자동 래핑 및 초기화를 먼저 수행합니다.
        if 'processes' not in self.attributes:
            self.processes = []
            if 'process' in self.attributes:
                p_attrs = {
                    "process": self.attributes.get("process"),
                    "target": self.attributes.get("target"),
                    "value": self.attributes.get("value"),
                    "condition": self.attributes.get("condition"),
                    "is_split": self.attributes.get("is_split"),
                    "extra_effect": self.attributes.get("extra_effect")
                }
                p_attrs = {k: v for k, v in p_attrs.items() if v is not None}
                self.processes.append(Process(**p_attrs))
            self.attributes['processes'] = self.processes
        else:
            self.processes = self.attributes['processes']

        # 프로세스 개별 속성을 제외한 메타 필드(type 등)만 __dict__ 속성으로 설정합니다.
        for key, value in wrapped.items():
            if key not in ['process', 'target', 'value', 'condition', 'is_split', 'extra_effect', 'processes']:
                setattr(self, key, value)

        # 하위 프로세스들에 부모 참조를 설정합니다.
        for p in self.processes:
            if isinstance(p, Process):
                p.parent_effect = self

        if isinstance(self.get('type'), Enum) and self.get('type').name == 'MODE':
            # choices 가 존재하지 않는 경우 빈 리스트로 자동 생성합니다.
            if 'choices' not in self.attributes:
                self.choices = []
                self.attributes['choices'] = self.choices
            elif not isinstance(self.attributes['choices'], list):
                raise TypeError("choices must be a list.")
            for choice in self.attributes['choices']:
                if not isinstance(choice, Effect):
                    raise TypeError("All items in 'choices' must be Effect objects.")

    def __getattr__(self, name):
        """기존 단일 프로세스 접근에 대한 위임 처리를 수행합니다."""
        if name in ['process', 'target', 'value', 'condition', 'is_split', 'extra_effect']:
            if hasattr(self, 'processes') and self.processes:
                return getattr(self.processes[0], name, None)
            if name in self.attributes:
                return self.attributes[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        """기존 단일 프로세스 수정 시 첫 번째 프로세스 객체와 값을 동기화합니다."""
        in_update = self.__dict__.get('_in_update', False)
        if not in_update and name in ['process', 'target', 'value', 'condition', 'is_split', 'extra_effect']:
            self.attributes[name] = value
            if hasattr(self, 'processes') and self.processes:
                setattr(self.processes[0], name, value)
                self.processes[0].attributes[name] = value
        else:
            super().__setattr__(name, value)

    def __repr__(self):
        """Effect 객체를 대표하는 문자열을 반환합니다."""
        parts = []
        sorted_keys = sorted(self.attributes.keys(), key=lambda k: k != 'type')

        for key in sorted_keys:
            value = self.attributes[key]

            if isinstance(value, Enum):
                formatted_value = f"{type(value).__name__}.{value.name}"
            elif isinstance(value, list):
                formatted_value = "[" + ", ".join(repr(item) for item in value) + "]"
            else:
                formatted_value = repr(value)

            parts.append(f"'{key}': {formatted_value}")

        return "Effect{" + f"{', '.join(parts)}" + "}"

    def update(self, **kwargs):
        """효과의 속성을 업데이트합니다."""
        self._in_update = True
        try:
            self.attributes.update(kwargs)
            for key, value in kwargs.items():
                setattr(self, key, value)
        finally:
            self._in_update = False

    def to_dict(self) -> Dict[str, Any]:
        """효과를 딕셔너리 형태로 재귀적으로 변환합니다."""
        data = {}
        for key, value in self.attributes.items():
            if isinstance(value, Enum):
                data[key] = value.name
            elif isinstance(value, (Effect, Process)):
                data[key] = value.to_dict()  # 재귀 호출
            elif isinstance(value, list):
                # 리스트 내의 Effect 또는 Process 객체들도 변환합니다.
                data[key] = [
                    item.to_dict() if isinstance(item, (Effect, Process)) else item
                    for item in value
                ]
            else:
                data[key] = value
        return data

    def get(self, key: str, default: Any = None) -> Any:
        """키를 사용하여 효과의 속성 값을 가져옵니다."""
        return getattr(self, key, default)