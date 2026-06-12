class Agent:

    def __init__(self, name, age, job, personality):

        self.name = name
        self.age = age
        self.job = job
        self.personality = personality

        # 상대방에 대한 정보 저장
        self.memory = {}

        # 관계 요약 저장
        self.relations = {}

        # 시간대별 일정
        self.schedule = {}

    def add_facts(self, about, facts):

        if about not in self.memory:
            self.memory[about] = []

        for fact in facts:

            fact = fact.strip()

            if fact and fact not in self.memory[about]:
                self.memory[about].append(fact)

    def known_facts(self, about):

        if about in self.memory:
            return self.memory[about]

        return []

    def set_reflection(self, about, reflection):

        self.relations[about] = reflection.strip()

    def reflection_on(self, about):

        if about in self.relations:
            return self.relations[about]

        return ""

    def has_met(self, other_name):

        return (
            other_name in self.memory
            or other_name in self.relations
        )

    def profile_line(self):

        return (
            f"{self.name}"
            f"({self.age}세, {self.job}) - "
            f"{self.personality}"
        )

    def memory_brief(self, about):

        text = ""

        if about in self.relations:
            text += "관계: "
            text += self.relations[about]
            text += "\n"

        if about in self.memory:
            text += "알고 있는 사실: "
            text += ", ".join(self.memory[about])

        if text.strip() == "":
            text = "처음 만나는 사람"

        return text

    def __repr__(self):

        return f"<Agent {self.name}>"