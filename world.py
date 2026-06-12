from __future__ import annotations

import random

import config
import dialogue
from agent import Agent


def plan_day(agent: Agent, day: int) -> dict[str, str]:
    """직업 기반 랜덤 일정 생성"""

    schedule = {}

    for slot in config.TIME_SLOTS:

        if "대학생" in agent.job:
            choices = [
                "학교",
                "학교",
                "카페",
                "도서관",
                "집",
            ]

        elif "카페" in agent.job:
            choices = [
                "카페",
                "카페",
                "카페",
                "레스토랑",
                "집",
            ]

        elif "개발자" in agent.job:
            choices = [
                "도서관",
                "도서관",
                "카페",
                "집",
            ]

        elif "트레이너" in agent.job:
            choices = [
                "헬스장",
                "공원",
                "카페",
                "집",
            ]

        else:
            choices = config.ALL_PLACES

        schedule[slot] = random.choice(choices)

    agent.schedule = schedule
    return schedule


def _resolve_location(agent: Agent, place: str) -> str:
    """집은 개인 공간으로 처리"""

    if place == config.HOME:
        return f"{agent.name}의 집"

    return place


def run_simulation(agents: list[Agent], days: int) -> None:
    """days일 동안 시뮬레이션"""

    for day in range(1, days + 1):

        print(f"\n{'=' * 56}")
        print(f"  가상 {day}일차 시작")
        print(f"{'=' * 56}")

        print("\n[하루 계획 수립]")

        for agent in agents:

            plan_day(agent, day)

            plan_text = ", ".join(
                f"{slot} {place}"
                for slot, place in agent.schedule.items()
            )

            print(f"  - {agent.name}: {plan_text}")

        for slot in config.TIME_SLOTS:

            location_groups = {}

            for agent in agents:

                place = agent.schedule.get(
                    slot,
                    config.HOME,
                )

                location = _resolve_location(
                    agent,
                    place,
                )

                location_groups.setdefault(
                    location,
                    [],
                ).append(agent)

            for location, group in location_groups.items():

                if (
                    location in config.PUBLIC_PLACES
                    and len(group) >= 2
                ):

                    names = ", ".join(
                        a.name
                        for a in group
                    )

                    print(
                        f"\n[{day}일차 {slot}] "
                        f"{location}에서 만남: {names}"
                    )

                    transcript = dialogue.run_round(
                        group,
                        location,
                        slot,
                        day,
                    )

                    for speaker, line in transcript:

                        print(
                            f"    {speaker}: {line}"
                        )

    print(f"\n{'=' * 56}")
    print("  시뮬레이션 종료")
    print(f"{'=' * 56}")