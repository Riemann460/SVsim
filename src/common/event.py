# 역할 정의. 게임의 상태 전이 및 카드 능력의 격리된 구독 처리를 돕는 개별 이벤트 데이터 구조를 정의합니다.

from dataclasses import dataclass
from typing import Optional
from src.common.enums import EventType

@dataclass
class Event:
    """이벤트의 기본 클래스입니다."""
    pass

@dataclass
class CardEvent(Event):
    """카드와 관련된 이벤트의 기본 클래스입니다."""
    card_id: str

@dataclass
class PlayerEvent(Event):
    """플레이어와 관련된 이벤트의 기본 클래스입니다."""
    player_id: str

@dataclass
class CardPlayerEvent(CardEvent, PlayerEvent):
    pass

# 구체적인 이벤트 클래스들입니다.
@dataclass
class TurnStartEvent(PlayerEvent):
    turn_number: int
    event_type: EventType = EventType.TURN_START

@dataclass
class TurnEndEvent(PlayerEvent):
    event_type: EventType = EventType.TURN_END

@dataclass
class SpellCastEvent(PlayerEvent):
    event_type: EventType = EventType.SPELL_CAST

@dataclass
class FollowerEnterFieldEvent(CardPlayerEvent):
    event_type: EventType = EventType.FOLLOWER_ENTER_FIELD

@dataclass
class CardPlayedEvent(CardEvent):
    enhanced_cost: int
    event_type: EventType = EventType.CARD_PLAYED

@dataclass
class FollowerEvolvedEvent(CardEvent):
    spend_ep: bool
    event_type: EventType = EventType.FOLLOWER_EVOLVED

@dataclass
class FollowerSuperEvolvedEvent(CardEvent):
    spend_sep: bool
    event_type: EventType = EventType.FOLLOWER_SUPER_EVOLVED

@dataclass
class CardEngagedEvent(CardEvent):
    event_type: EventType = EventType.CARD_ENGAGED

@dataclass
class DestroyedOnFieldEvent(CardEvent):
    event_type: EventType = EventType.DESTROYED_ON_FIELD

@dataclass
class AttackDeclaredEvent(CardEvent):
    target_id: str
    event_type: EventType = EventType.ATTACK_DECLARED

@dataclass
class CombatInitiatedEvent(CardEvent):
    target_id: str
    event_type: EventType = EventType.COMBAT_INITIATED

@dataclass
class DamageDealtByCombatEvent(CardEvent):
    damage: int
    event_type: EventType = EventType.DAMAGE_DEALT_BY_COMBAT

@dataclass
class CardDiscardedEvent(CardPlayerEvent):
    """카드가 버려졌을 때 발생하는 이벤트입니다."""
    event_type: EventType = EventType.CARD_DISCARDED

@dataclass
class FuseDeclaredEvent(CardPlayerEvent):
    """융합을 선언했을 때 발생하는 이벤트입니다."""
    material_card_ids: list
    event_type: EventType = EventType.FUSE_DECLARED

@dataclass
class LeaveFieldEvent(CardPlayerEvent):
    """카드가 필드를 벗어날 때 발생하는 이벤트입니다."""
    event_type: EventType = EventType.LEAVE_FIELD
