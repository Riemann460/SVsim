# 역할 정의. GUI를 우회하여 게임 엔진의 자동 랜덤 플레이 시뮬레이션을 수행하고 예외를 감지 및 분석하여 리포트를 생성하는 퍼징 러너 스크립트입니다.

import os
import sys
import json
import random
import traceback
from typing import Dict, Any, List, Tuple, Optional

# 절대 경로 설정을 위해 작업 디렉토리를 참조합니다.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.models.card import Card
from src.common.enums import Zone, CardType, EffectType


class MockGUI:
    """Tkinter GUI 팝업을 차단하고 콘솔 상에서 무작위 선택을 자동으로 처리하는 모의 GUI 클래스입니다."""

    def __init__(self, game_state_manager: Any = None):
        """MockGUI 인스턴스를 생성하고 게임 상태 매니저를 참조합니다."""
        self.game_state_manager = game_state_manager

    def update(self):
        """GUI 화면 갱신 요청을 시뮬레이션하며 실제로는 아무 동작도 수행하지 않습니다."""
        pass

    def get_user_choice(self, prompt: str, choices: Dict[str, Any]) -> Any:
        """제시된 무작위 효과나 행동 선택지 중 하나를 무작위로 결정하여 반환합니다."""
        if not choices:
            return None
        selected_key = random.choice(list(choices.keys()))
        return choices[selected_key]

    def get_mulligan_choices(self, player_id: str, hand_cards: List[Card]) -> List[str]:
        """멀리건 단계에서 교체할 손패 카드를 0장부터 최대 전체 손패 수 범위 내에서 무작위로 선택합니다."""
        if not hand_cards:
            return []
        num_to_replace = random.randint(0, len(hand_cards))
        selected_cards = random.sample(hand_cards, num_to_replace)
        return [c.card_id for c in selected_cards]

    def get_discard_choices(self, player_id: str, hand_cards: List[Card], count: int) -> List[str]:
        """버려야 할 손패 카드를 요구 수량에 맞춰 무작위로 선택하여 반환합니다."""
        card_ids = [c.card_id for c in hand_cards]
        num_to_discard = min(count, len(card_ids))
        return random.sample(card_ids, num_to_discard)


# GUI 창이 생성 단계에서부터 팝업되는 것을 막기 위해 GameGUI 클래스를 MockGUI로 원숭이 패치(Monkey Patch)합니다.
import ui.gui
ui.gui.GameGUI = MockGUI

import src.engine.main_game_logic as main_game_logic
main_game_logic.GameGUI = MockGUI

from src.engine.main_game_logic import Game
import src.common.card_data as card_data


def get_all_possible_actions(game: Game, current_player: str) -> List[Dict[str, Any]]:
    """현재 활성화된 플레이어가 수행 가능한 모든 유효한 액션을 수집하여 리스트로 반환합니다."""
    possible_actions = []
    opponent_id = game.opponent_id[current_player]

    # 1 패에서 카드를 내는 액션을 수집합니다.
    use_extra_pp_options = [False]
    if game.has_extra_pp(current_player):
        use_extra_pp_options.append(True)

    for use_extra_pp in use_extra_pp_options:
        hand_cards_id, is_validate = game.get_playable_cards_id(current_player, use_extra_pp)
        if hand_cards_id:
            for i, card_id in enumerate(hand_cards_id):
                if is_validate[i]:
                    current_pp, _ = game.game_state_manager.get_pp_info(current_player)
                    enhance_effects = [effect for effect in game.game_state_manager.get_card_effects(card_id, EffectType.ENHANCE)]
                    enhance_costs_for_card = [effect.enhance_cost for effect in enhance_effects if effect.enhance_cost <= current_pp + (1 if use_extra_pp else 0)]
                    enhanced_cost = max(enhance_costs_for_card) if enhance_costs_for_card else 0

                    possible_actions.append({
                        "type": "PLAY_CARD",
                        "card_id": card_id,
                        "enhanced_cost": enhanced_cost,
                        "use_extra_pp": use_extra_pp
                    })

    # 2 필드에 배치된 카드들을 통해 공격 진화 초진화 카드 활성화 액션을 수집합니다.
    player_field_card_ids = game.game_state_manager.get_card_ids_in_zone(current_player, Zone.FIELD)
    opponent_field_card_ids = game.game_state_manager.get_card_ids_in_zone(opponent_id, Zone.FIELD)

    for card_id in player_field_card_ids:
        available_actions, _ = game.get_available_actions(card_id, current_player)

        # 2-1 추종자 공격 액션을 검증하고 추가합니다.
        if "추종자 공격" in available_actions:
            opponent_targets_id = [opp_card_id for opp_card_id in opponent_field_card_ids if game.game_state_manager.get_type(opp_card_id) == CardType.FOLLOWER] + [opponent_id]
            for target_id in opponent_targets_id:
                if game.rule_engine.validate_attack(card_id, target_id):
                    possible_actions.append({
                        "type": "ATTACK",
                        "attacker_id": card_id,
                        "target_id": target_id
                    })

        # 2-2 추종자 진화 액션을 추가합니다.
        if "추종자 진화" in available_actions:
            possible_actions.append({
                "type": "EVOLVE",
                "card_id": card_id
            })

        # 2-3 추종자 초진화 액션을 추가합니다.
        if "추종자 초진화" in available_actions:
            possible_actions.append({
                "type": "SUPER_EVOLVE",
                "card_id": card_id
            })

        # 2-4 카드 활성화 액션을 추가합니다.
        if "카드 활성화(Engage)" in available_actions:
            possible_actions.append({
                "type": "ENGAGE",
                "card_id": card_id
            })

    # 3 언제나 선택 가능한 턴 종료 액션을 추가합니다.
    possible_actions.append({
        "type": "END_TURN"
    })

    return possible_actions


def run_fuzzing(runs: int = 1, max_turns: int = 20) -> Tuple[bool, Optional[Exception]]:
    """지정된 횟수만큼 게임 세션을 반복 생성하여 퍼징 테스트를 수행합니다. 오류 발생 시 예외 객체를 반환합니다."""
    card_data.load_card_databases('card_database/3_parsed_database/card_database_parsed.json')
    
    for run_idx in range(runs):
        game = None
        try:
            # 게임 클래스 초기화 시 Monkey Patching된 GameGUI가 MockGUI로 구동되어 자동 선택됩니다.
            game = Game("player1", "player2")
            
            current_player = "player1"
            
            for turn_num in range(1, max_turns + 1):
                # 승리 조건 등으로 한쪽 플레이어 체력이 0 이하가 되면 조기 종료합니다.
                p1_hp = game.game_state_manager.players["player1"].current_defense
                p2_hp = game.game_state_manager.players["player2"].current_defense
                if p1_hp <= 0 or p2_hp <= 0:
                    break

                action_count = 0
                max_actions_per_turn = 30
                
                while True:
                    # 턴 시작 상태의 특수 카드 선택 효과 등을 먼저 자동 처리합니다.
                    game.process_player_choice()

                    # 가능한 모든 유효 액션을 수집합니다.
                    possible_actions = get_all_possible_actions(game, current_player)
                    if not possible_actions:
                        game.end_turn(current_player)
                        break

                    # 무한 루프 방지를 위해 일정량 이상 액션이 지속되면 강제로 턴을 종료시킵니다.
                    action_count += 1
                    if action_count > max_actions_per_turn:
                        game.end_turn(current_player)
                        break

                    # 무작위 액션 하나를 선택하여 진행합니다.
                    action = random.choice(possible_actions)
                    
                    if action["type"] == "PLAY_CARD":
                        game.play_card(current_player, action["card_id"], action["enhanced_cost"], action["use_extra_pp"])
                    elif action["type"] == "ATTACK":
                        target_type = game.game_state_manager.get_type(action["target_id"])
                        if target_type == CardType.LEADER:
                            game.attack_leader(action["attacker_id"])
                        else:
                            game.attack_follower(action["attacker_id"], action["target_id"])
                    elif action["type"] == "EVOLVE":
                        game.evolve_follower(action["card_id"], current_player)
                    elif action["type"] == "SUPER_EVOLVE":
                        game.super_evolve_follower(action["card_id"], current_player)
                    elif action["type"] == "ENGAGE":
                        game.engage_card(action["card_id"], current_player)
                    elif action["type"] == "END_TURN":
                        game.end_turn(current_player)
                        break
                
                # 플레이어 턴을 전환합니다.
                current_player = game.opponent_id[current_player]

        except Exception as e:
            # 예외 감지 시 현재의 게임 상태와 분석 보고서를 즉시 작성합니다.
            exc_info = analyze_exception(e)
            state_snapshot = extract_state_snapshot(game)
            generate_report(exc_info, state_snapshot)
            return False, e

    return True, None


def analyze_exception(exc: Exception) -> Dict[str, str]:
    """발생한 예외 객체를 파싱하여 예외 종류 메시지 트레이스백 문자열을 추출합니다."""
    tb_str = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    return {
        "error_type": type(exc).__name__,
        "message": str(exc),
        "traceback": tb_str
    }


def extract_state_snapshot(game: Optional[Game]) -> Dict[str, Any]:
    """예외가 발생한 시점의 게임 도메인 정보를 안전하게 캡처하여 스냅샷 딕셔너리로 만듭니다."""
    snapshot = {}
    if not game:
        return {"error": "게임 인스턴스가 존재하지 않습니다."}
    try:
        gsm = game.game_state_manager
        p1 = gsm.players.get("player1")
        p2 = gsm.players.get("player2")
        
        snapshot = {
            "turn": gsm.turn_number,
            "active_player": gsm.current_turn_player_id,
            "p1_hp": p1.current_defense if p1 else 0,
            "p2_hp": p2.current_defense if p2 else 0,
            "p1_pp": p1.current_pp if p1 else 0,
            "p2_pp": p2.current_pp if p2 else 0,
            "p1_hand": [gsm.get_card_name(cid) for cid in gsm.get_card_ids_in_zone("player1", Zone.HAND)] if p1 else [],
            "p2_hand": [gsm.get_card_name(cid) for cid in gsm.get_card_ids_in_zone("player2", Zone.HAND)] if p2 else [],
            "p1_field": [gsm.get_card_name(cid) for cid in gsm.get_card_ids_in_zone("player1", Zone.FIELD)] if p1 else [],
            "p2_field": [gsm.get_card_name(cid) for cid in gsm.get_card_ids_in_zone("player2", Zone.FIELD)] if p2 else []
        }
    except Exception as e:
        snapshot = {
            "error": f"상태 스냅샷 생성 중 실패함 {str(e)}."
        }
    return snapshot


def generate_report(analysis_result: Dict[str, str], game_state: Dict[str, Any], filepath: str = "fuzzing_report.md") -> bool:
    """분석 결과와 게임 스냅샷 데이터를 기반으로 마크다운 보고서 파일을 생성합니다."""
    try:
        content = []
        content.append("# 퍼징 테스트 에러 분석 리포트")
        content.append("")
        content.append("## 1 에러 기본 요약")
        content.append(f"- **에러 유형** {analysis_result.get('error_type')}")
        content.append(f"- **에러 메시지** {analysis_result.get('message')}")
        content.append("")
        content.append("## 2 에러 발생 시점 게임 상태 스냅샷")
        content.append(f"- **현재 진행 턴** {game_state.get('turn')}")
        content.append(f"- **현재 턴 플레이어** {game_state.get('active_player')}")
        content.append(f"- **플레이어 1 체력** {game_state.get('p1_hp')} (PP {game_state.get('p1_pp')})")
        content.append(f"- **플레이어 2 체력** {game_state.get('p2_hp')} (PP {game_state.get('p2_pp')})")
        content.append("")
        content.append("### 플레이어 1 손패 카드 목록")
        content.append(f"{game_state.get('p1_hand')}")
        content.append("")
        content.append("### 플레이어 2 손패 카드 목록")
        content.append(f"{game_state.get('p2_hand')}")
        content.append("")
        content.append("### 플레이어 1 필드 카드 목록")
        content.append(f"{game_state.get('p1_field')}")
        content.append("")
        content.append("### 플레이어 2 필드 카드 목록")
        content.append(f"{game_state.get('p2_field')}")
        content.append("")
        content.append("## 3 상세 트레이스백 정보")
        content.append("```text")
        content.append(analysis_result.get("traceback", ""))
        content.append("```")
        content.append("")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
        return True
    except Exception:
        return False


def load_agent_config(filepath: str = "agent.json") -> Dict[str, Any]:
    """에이전트 제어 정보를 정의한 JSON 파일을 로드하여 파이썬 딕셔너리로 제공합니다."""
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


if __name__ == "__main__":
    # 에이전트 설정 파일 경로를 탐색하여 로드합니다.
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".agents", "agents", "svsim-debug-fuzz", "agent.json")
    config = load_agent_config(config_path)
    run_count = config.get("parameters", {}).get("run_count", 10)
    max_turns = config.get("parameters", {}).get("max_turns", 20)
    
    print(f"퍼징 테스트를 {run_count}회 시작합니다.")
    success, error = run_fuzzing(run_count, max_turns)
    if success:
        print("퍼징 테스트가 오류 없이 완료되었습니다.")
        sys.exit(0)
    else:
        print(f"퍼징 테스트 도중 오류가 발생했습니다. {error}")
        sys.exit(1)
