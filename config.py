"""
시뮬레이션 공통 설정.

.env 파일이 있으면 값을 읽고, 없으면 기본값을 사용한다.
모델, 활동 시간, 공간 목록, 에이전트 프로필을 모두 여기서 관리한다.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

# --- LLM 설정 ---
# 호출이 많은 시뮬레이션이라 기본은 gpt-4o-mini. 품질을 높이려면 .env에서 gpt-4o로 교체.
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.3"))

# --- 시뮬레이션 시간/일수 ---
NUM_DAYS = int(os.getenv("NUM_DAYS", "2"))  # 과제 요구: 가상의 이틀

# 활동 시간 범위를 시간대(슬롯)로 나눈 것. 08:00 ~ 22:00 사이를 대표 시간대로 표현.
TIME_SLOTS = ["08:00", "11:00", "14:00", "17:00", "20:00"]

# --- 공간 목록 ---
# "집"은 각 에이전트의 개인 공간이라 서로 만나지 않는다(아래 world.py에서 개인 집으로 변환).
# 나머지는 공용 공간이라 같은 시간대에 모이면 자동으로 대화가 시작된다.
HOME = "집"
PUBLIC_PLACES = ["학교", "카페", "도서관", "레스토랑", "공원", "헬스장"]
ALL_PLACES = [HOME] + PUBLIC_PLACES

# 한 번 만났을 때 주고받는 발언 수(라운드 길이). 너무 길면 호출/비용이 늘어난다.
CONV_TURNS = int(os.getenv("CONV_TURNS", "4"))

# 리포트 기준이 되는 에이전트(과제: "Index 1번(첫 번째) 에이전트"). 0-based로 첫 번째.
REPORT_AGENT_INDEX = 0

# --- 에이전트 프로필 ---
# 직업/성격이 서로 달라서 하루 동선이 자연스럽게 겹치도록 구성했다.
AGENT_PROFILES = [
    {
        "name": "이익준",
        "age": 21,
        "job": "대학생(의예과)",
        "personality": "호기심이 많고 외향적이며, 새로운 사람과 어울리는 것을 좋아한다.",
    },
    {
        "name": "김지향",
        "age": 27,
        "job": "동네 카페 사장 겸 바리스타",
        "personality": "차분하고 다정하며, 사람을 관찰하고 이야기를 들어주는 것을 즐긴다.",
    },
    {
        "name": "박진우",
        "age": 34,
        "job": "프리랜서 소프트웨어 개발자",
        "personality": "내향적이고 분석적이며, 혼자 도서관에서 집중해 일하는 것을 선호한다.",
    },
    {
        "name": "윤진서",
        "age": 23,
        "job": "헬스 트레이너",
        "personality": "활기차고 직설적이며, 운동과 건강에 대한 이야기를 즐긴다.",
    },
]

# --- 초기 Memory/관계 주입(선택) ---
# 일부 에이전트는 이미 아는 사이로 시작 -> "이미 만난 상대(주제 대화)"와
# "처음 만나는 상대(인사부터)" 두 경로를 모두 시뮬레이션할 수 있다.
INITIAL_KNOWLEDGE = {
    "이익준": {
        "facts": {
            "김지향": ["동네 카페 사장님이다.", "가끔 카페에 들러 인사하는 사이다."],
        },
        "relations": {
            "김지향": "단골로 가는 카페의 사장님. 편하게 인사하는 가벼운 친분이 있다.",
        },
    },
    "김지향": {
        "facts": {
            "이익준": ["동네 카페 사장님이다.", "가끔 카페에 들러 인사하는 사이다."],
        },
        "relations": {
            "이익준": "카페에 자주 오는 친근한 단골 대학생. 인사를 나누는 사이다.",
        },
    },
}

# 리포트 저장 경로
REPORT_PATH = os.getenv("REPORT_PATH", "report.txt")
