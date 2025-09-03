
from dataclasses import dataclass
from typing import Optional
from enums import EventType

@dataclass
class Event:
    """이벤트의 기본 클래스"""
    pass

@dataclass
class CardEvent(Event):
    """카드와 관련된 이벤트의 기본 클래스"""
    card_id: str

@dataclass
class PlayerEvent(Event):
    """플레이어와 관련된 이벤트의 기본 클래스"""
    player_id: str

@dataclass
class CardPlayerEvent(CardEvent, PlayerEvent):
    pass

# 구체적인 이벤트 클래스
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
class AmuletActivatedEvent(CardEvent):
    event_type: EventType = EventType.AMULET_ACTIVATED

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
