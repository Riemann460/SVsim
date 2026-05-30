# -*- coding: utf-8 -*-
import ast
import io
import os
import re
import tokenize

def is_sentence(text: str) -> bool:
    clean = text.rstrip(".").strip()
    if not clean:
        return False
    # 괄호를 제거한 텍스트로 문장 여부를 체크합니다.
    clean = re.sub(r"\(.*?\)$", "", clean).strip()
    return clean.endswith(('다', '요', '오', '죠', '까', '네'))

target_files = [
    "tests/scenario_helper.py",
    "tests/test_scenario_builder.py",
    "src/models/card.py",
    "src/models/crest.py",
    "src/models/deck.py",
    "src/models/field.py",
    "src/models/graveyard.py",
    "src/models/hand.py",
    "src/models/player.py",
    "src/common/card_data.py",
    "src/common/effect.py",
    "src/common/enums.py",
    "src/common/event.py",
    "src/common/listener.py",
    "src/engine/effect_processor.py",
    "src/engine/event_manager.py",
    "src/engine/game_state_manager.py",
    "src/engine/main_game_logic.py",
    "src/engine/rule_engine.py",
    "ui/gui.py",
    "main.py",
    "card_data_pipeline/1_data_acquisition/add_korean_names.py",
    "card_data_pipeline/1_data_acquisition/analyze_effects.py",
    "card_data_pipeline/1_data_acquisition/card_data_crawl.py",
    "card_data_pipeline/1_data_acquisition/check_parsing_rate.py",
    "card_data_pipeline/1_data_acquisition/convert_database.py",
    "card_data_pipeline/1_data_acquisition/parse_script.py",
    "card_data_pipeline/2_manual_data_refinement/manual_editor.py"
]

for filepath in target_files:
    if not os.path.exists(filepath):
        continue

    print(f"Processing {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. docstring 수정 (AST 사용)
    # AST로 docstring 노드를 찾아서 텍스트를 교체합니다.
    try:
        tree = ast.parse(content)
    except SyntaxError:
        continue

    replacements = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            docstring = ast.get_docstring(node)
            if docstring:
                lines = docstring.split("\n")
                changed = False
                new_lines = []
                for line in lines:
                    line_strip = line.strip()
                    if line_strip.startswith("-") or len(line_strip.split()) <= 1:
                        new_lines.append(line)
                        continue
                    if not is_sentence(line_strip) and line_strip.endswith("."):
                        # 구문인데 마침표가 있으면 제거합니다.
                        # 공백 유지를 위해 rsplit 사용
                        idx = line.rfind(".")
                        new_line = line[:idx] + line[idx+1:]
                        new_lines.append(new_line)
                        changed = True
                    else:
                        new_lines.append(line)
                
                if changed:
                    new_docstring = "\n".join(new_lines)
                    # content 내의 기존 docstring 리터럴을 찾아서 교체합니다.
                    # 간단히 replace를 수행하기 위해 docstring의 raw representation을 찾습니다.
                    # 단, 겹따옴표/홑따옴표 삼중 따옴표 등 형식이 다양하므로 조심스럽게 매칭합니다.
                    # 여기서는 안전을 위해 content 내의 정확한 매칭 텍스트를 찾아 바꿉니다.
                    # docstring이 홑따옴표나 겹따옴표 삼중으로 둘러싸여 있으므로 content를 직접 수정합니다.
                    # (간단히 raw content replace)
                    # 이를 위해 regex 패턴으로 삼중따옴표 안의 원본 docstring을 매칭합니다.
                    escaped_old = re.escape(docstring)
                    # 삼중 홑따옴표 혹은 삼중 겹따옴표 패턴
                    pattern = rf"(['\"]{{3}}){escaped_old}(['\"]{{3}})"
                    
                    def repl_func(match):
                        return f"{match.group(1)}{new_docstring}{match.group(2)}"
                    
                    content = re.sub(pattern, repl_func, content)

    # 2. 한 줄 주석 수정 (tokenize 사용)
    # tokenize로 주석의 라인 번호와 문자 위치를 찾아서 문자열 조작을 수행합니다.
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(content).readline))
    except Exception:
        continue

    # 토큰들은 줄번호(1-indexed) 순으로 정렬되어 있으므로, 
    # 라인 단위로 쪼개서 각 주석 토큰을 교체합니다.
    lines = content.splitlines(keepends=True)
    changed_lines = False

    for token in tokens:
        if token.type == tokenize.COMMENT:
            comment_text = token.string[1:].strip()
            if not comment_text:
                continue
            
            # 주석 규정을 엄격하게 준수합니다 문구를 삭제합니다.
            compliance_pattern = r"\.?\s*주석\s*규정을\s*엄격하게\s*준수합니다\.?"
            clean_text = re.sub(compliance_pattern, "", comment_text).strip()
            if clean_text != comment_text:
                comment_text = clean_text
                changed_lines = True
            
            words = comment_text.split()
            if len(words) > 1:
                if not comment_text.startswith("TODO") and not comment_text.startswith("FIXME"):
                    if not is_sentence(comment_text) and comment_text.endswith("."):
                        # 구문 주석에서 마침표를 제거합니다.
                        comment_text = comment_text.rstrip(".")
                        changed_lines = True
            
            # 변경된 주석을 적용합니다.
            # token.start[0]은 1-based 라인 번호입니다.
            line_idx = token.start[0] - 1
            line = lines[line_idx]
            
            # token.start[1]은 라인 내의 주석 시작 인덱스 (# 문자 위치)입니다.
            comment_start_idx = token.start[1]
            
            # 라인의 앞부분 유지 + 새로운 주석 조립
            new_comment_line = line[:comment_start_idx] + "# " + comment_text
            # 개행문자 복구
            if line.endswith("\n"):
                new_comment_line += "\n"
            elif line.endswith("\r\n"):
                new_comment_line += "\r\n"
                
            if lines[line_idx] != new_comment_line:
                lines[line_idx] = new_comment_line
                changed_lines = True

    if changed_lines:
        new_content = "".join(lines)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated {filepath}")

print("Done!")
