"""
리포트 출력.

특정 에이전트(과제: 첫 번째 에이전트) 시점에서,
다른 모든 에이전트 각각에 대해 '알고 있는 사실'과 '관계(Reflection)'를 정리한다.
터미널에 출력하고 파일로도 저장한다.
"""

from __future__ import annotations

from agent import Agent


def build_report(viewer: Agent, all_agents: list[Agent]) -> str:
    """viewer 시점의 리포트 텍스트를 만든다."""
    lines: list[str] = []
    lines.append("=" * 56)
    lines.append(f"  관계 리포트 - '{viewer.name}' 시점")
    lines.append(f"  ({viewer.profile_line()})")
    lines.append("=" * 56)

    others = [a for a in all_agents if a is not viewer]
    for other in others:
        lines.append("")
        lines.append(f"[ {other.name} ]")

        facts = viewer.known_facts(other.name)
        lines.append("- 알고 있는 사실:")
        if facts:
            for fact in facts:
                lines.append(f"    * {fact}")
        else:
            lines.append("    * (아는 사실 없음 - 만난 적이 없거나 대화가 없었음)")

        reflection = viewer.reflection_on(other.name)
        lines.append("- 관계(Reflection):")
        lines.append(f"    {reflection if reflection else '(형성된 관계 없음)'}")

    lines.append("")
    lines.append("=" * 56)
    return "\n".join(lines)


def save_report(text: str, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
