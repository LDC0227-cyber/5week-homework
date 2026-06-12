"""
대화 시스템 (기본 구조).

- 2명 이상의 에이전트가 한 라운드에서 대화한다.
- 처음 만나는 사이면 인사/자기소개부터 시작하고 주제를 강제하지 않는다.
- 이미 아는 사이면 각자의 Memory를 바탕으로 주제를 꺼낸다.
- 라운드가 끝나면 LLM이 각 참여자에 대한 사실(Fact)을 추출해
  '그 사람을 제외한' 나머지 참여자의 Memory에 저장한다.
- 라운드가 끝나면 참여한 모든 쌍에 대해 Reflection을 갱신한다.
"""

from __future__ import annotations

import json

import config
import llm
from agent import Agent


def _others(speaker: Agent, participants: list[Agent]) -> list[Agent]:
    return [a for a in participants if a is not speaker]


def _lookup(data: dict, name: str):
    """LLM이 '정하늘 씨'처럼 이름을 변형해 키로 써도 최대한 찾아 준다."""
    if name in data:
        return data[name]
    for key, value in data.items():
        k = str(key).strip()
        if k == name or name in k or k in name:
            return value
    return None


def _generate_utterance(
    speaker: Agent,
    participants: list[Agent],
    place: str,
    transcript: list[tuple[str, str]],
    topic: str | None = None,
) -> str:
    """speaker가 지금 상황에서 할 한 마디를 생성한다."""
    others = _others(speaker, participants)
    others_names = ", ".join(a.name for a in others)

    # 화자 기준으로 '이미 아는 사람'과 '처음 보는 사람'을 구분한다.
    new_others = [o for o in others if not speaker.has_met(o.name)]
    known_others = [o for o in others if speaker.has_met(o.name)]

    # 상대들에 대해 현재 알고 있는 것
    knowledge_lines = []
    for o in others:
        knowledge_lines.append(f"- {o.name}: {speaker.memory_brief(o.name)}")
    knowledge = "\n".join(knowledge_lines)

    # 지금까지의 대화
    if transcript:
        history = "\n".join(f"{name}: {text}" for name, text in transcript)
    else:
        history = "(아직 아무도 말하지 않음. 당신이 첫 마디를 한다.)"

    if known_others and not new_others:
        guide = (
            "이 자리에 있는 사람들은 모두 당신이 전에 만난 적 있는 사이다. "
            "'처음 뵙겠습니다' 같은 초면 인사는 절대 하지 말고, 아는 사이답게 안부를 묻거나 "
            "알고 있는 사실·지난 관계를 이어 자연스럽게 이야기하라."
        )
    elif new_others and not known_others:
        guide = (
            "이 자리에는 처음 보는 사람만 있다. 가벼운 인사와 짧은 자기소개부터 자연스럽게 시작하라. "
            "억지로 특정 주제를 꺼내지 말고, 분위기에 맞게 이야기하라."
        )
    else:
        new_names = ", ".join(o.name for o in new_others)
        known_names = ", ".join(o.name for o in known_others)
        guide = (
            f"처음 보는 사람({new_names})과 이미 아는 사람({known_names})이 함께 있다. "
            f"처음 보는 사람에게는 가볍게 인사하되, 아는 사람에게는 초면 인사 없이 아는 사이답게 대하라."
        )

    # 주제(topic)는 선택 사항. 주어지면 그 주제로 이끈다(단, 순수 초면 자리에서는 인사가 우선).
    pure_first_meeting = bool(new_others) and not known_others
    if topic and not pure_first_meeting:
        guide += f" 이번 대화의 주제는 '{topic}'이다. 이 주제를 중심으로 자연스럽게 이야기하라."

    system = (
        f"당신은 '{speaker.name}'이라는 사람으로 롤플레이한다.\n"
        f"프로필: {speaker.profile_line()}\n"
        "당신의 성격과 말투를 일관되게 유지하라. "
        "한국어로, 실제 사람처럼 한두 문장으로 짧고 자연스럽게 말하라. "
        "따옴표나 지문 없이 대사만 출력하라."
    )
    user = (
        f"장소: {place}\n"
        f"함께 있는 사람: {others_names}\n"
        f"이들에 대해 당신이 아는 것:\n{knowledge}\n\n"
        f"지금까지의 대화:\n{history}\n\n"
        f"{guide}\n"
        f"이제 '{speaker.name}'으로서 할 다음 한 마디를 말하라."
    )
    
    line = llm.chat(system, user)
    # 모델이 가끔 'name: 대사' 형태로 내놓으면 이름 접두사를 떼어 준다.
    prefix = f"{speaker.name}:"
    if line.startswith(prefix):
        line = line[len(prefix) :].strip()
    return line


def converse(
    participants: list[Agent],
    place: str,
    time_slot: str,
    day: int,
    turns: int | None = None,
    topic: str | None = None,
) -> list[tuple[str, str]]:
    """
    한 라운드 대화를 진행하고 (화자, 대사) 목록을 돌려준다.

    turns: 이 라운드의 발언 수(라운드마다 개별 지정 가능). 없으면 config.CONV_TURNS.
    topic: 대화 주제(선택). 없으면 각자 Memory를 바탕으로 자연스럽게 주제를 꺼낸다.
    """
    transcript: list[tuple[str, str]] = []

    # 발언 순서: 참여자를 번갈아 가며 지정된 횟수만큼 말한다.
    order = participants[:]
    n = config.CONV_TURNS if turns is None else turns
    total_turns = max(n, len(participants))
    for i in range(total_turns):
        speaker = order[i % len(order)]
        line = _generate_utterance(speaker, participants, place, transcript, topic)
        transcript.append((speaker.name, line))
    return transcript


def extract_facts(participants: list[Agent], transcript: list[tuple[str, str]]) -> dict[str, list[str]]:
    """대화에서 각 참여자에 대한 사실(Fact)을 추출한다. { 이름: [사실들] }"""
    names = [a.name for a in participants]
    convo_text = "\n".join(f"{name}: {text}" for name, text in transcript)

    system = (
        "너는 대화 분석기다. 주어진 대화에서 각 참가자에 대해 '새롭게 드러난 사실'만 골라낸다. "
        "추측하지 말고 대화에 실제로 나타난 정보만 간결한 한국어 문장으로 정리하라."
    )
    user = (
        f"참가자: {', '.join(names)}\n\n"
        f"대화:\n{convo_text}\n\n"
        "각 참가자에 대해 이 대화에서 드러난 사실을 정리하라. "
        "없으면 빈 배열로 둔다. 반드시 아래 형식의 JSON만 출력하라.\n"
        '{ "facts": { "이름": ["사실1", "사실2"] } }'
    )
    data = llm.chat_json(system, user)
    facts = data.get("facts", {}) or {}
    # 참가자 이름만 남기고 정리(이름 변형 대비해 _lookup 사용)
    return {name: list(_lookup(facts, name) or []) for name in names}


def update_reflections(
    observer: Agent, targets: list[Agent], transcript: list[tuple[str, str]]
) -> dict[str, str]:
    """observer 입장에서 targets 각각에 대한 Reflection(관계 요약)을 갱신한다."""
    convo_text = "\n".join(f"{name}: {text}" for name, text in transcript)

    current_lines = []
    for t in targets:
        prev = observer.reflection_on(t.name) or "(이전 관계 없음 - 이번에 처음 만남)"
        current_lines.append(f"- {t.name}: {prev}")
    current = "\n".join(current_lines)

    system = (
        f"너는 '{observer.name}'의 입장에서 상대에 대한 '누적된 관계와 인상'을 한두 문장으로 요약한다. "
        f"'{observer.name}'의 성격({observer.personality})을 반영하되 과장 없이 담백하게. "
        "한 번의 만남을 묘사하지 말고('처음 만났다', '오늘' 같은 표현 금지) 그 사람과의 전반적 관계로 써라."
    )
    user = (
        f"'{observer.name}'이(가) 다음 사람들에 대해 가지고 있던 기존 관계 요약:\n{current}\n\n"
        f"방금 나눈 대화:\n{convo_text}\n\n"
        f"이 대화를 반영해 각 상대에 대한 '{observer.name}'의 관계 요약을 갱신하라. "
        "특정 만남이 아니라 그 사람에 대한 누적된 관계/인상으로 표현하라. "
        "반드시 아래 형식의 JSON만 출력하라.\n"
        '{ "reflections": { "상대이름": "갱신된 한두 문장 관계 요약" } }'
    )
    data = llm.chat_json(system, user)
    reflections = data.get("reflections", {}) or {}
    result = {}
    for t in targets:
        val = _lookup(reflections, t.name)
        result[t.name] = str(val).strip() if val else observer.reflection_on(t.name)
    return result


def run_round(
    participants: list[Agent],
    place: str,
    time_slot: str,
    day: int,
    turns: int | None = None,
    topic: str | None = None,
) -> list[tuple[str, str]]:
    """
    한 라운드 전체 처리:
    1) 대화 진행(turns/topic은 라운드마다 개별 지정 가능)
    2) Fact 추출 -> 해당 인물을 제외한 나머지 참여자 Memory에 저장
    3) 참여한 모든 쌍에 대해 Reflection 갱신
    """
    transcript = converse(participants, place, time_slot, day, turns=turns, topic=topic)

    # 2) Fact 추출 및 저장 (사실의 주인을 '제외한' 나머지에게 저장)
    facts_by_person = extract_facts(participants, transcript)
    for subject_name, facts in facts_by_person.items():
        if not facts:
            continue
        for listener in participants:
            if listener.name != subject_name:
                listener.add_facts(subject_name, facts)

    # 3) Reflection 갱신 (참여한 모든 쌍)
    for observer in participants:
        targets = _others(observer, participants)
        new_reflections = update_reflections(observer, targets, transcript)
        for target_name, reflection in new_reflections.items():
            observer.set_reflection(target_name, reflection)

    return transcript
