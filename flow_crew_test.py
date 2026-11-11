# Фаза 3: Crew внутри Flow
# Flow решает ЧТО делать (граф шагов), Crew — КТО делает работу внутри шага.

from crewai import Agent, Crew, CrewOutput, LLM, Process, Task
from crewai.flow.flow import Flow, listen, start
from pydantic import BaseModel

# --- LLM: та же связка, что проверена в Сессии 1 (CrewAI → LiteLLM → Ollama) ---
# Эксперимент сравнения моделей: qwen2.5-coder:7b (базовый прогон) vs gemma4:12b
llm = LLM(
    model="ollama/gemma4:12b",
    base_url="http://localhost:11434",
)


# --- State Flow: данные живут здесь и передаются между шагами ---
class TopicState(BaseModel):
    topic: str = ""
    analysis: str = ""   # сюда ляжет результат работы Crew
    report: str = ""     # сюда ляжет отчёт Crew-писателя


class CrewFlow(Flow[TopicState]):

    # --- Шаг 1: обычный Python-код, БЕЗ LLM ---
    @start()
    def begin(self):
        print("Шаг 1 (код): тема кладётся в state")
        self.state.topic = "локальные LLM vs облачные API"
        return self.state.topic

    # --- Шаг 2: ВОТ ОНА, главная точка Фазы 3 — Crew внутри шага Flow ---
    @listen("begin")
    def run_crew(self, result):
        print("Шаг 2 (LLM): Crew выполняется внутри шага Flow")

        analyst = Agent(
            role="Технический аналитик",
            goal="Сделать краткий анализ заданной темы",
            backstory=(
                "Опытный аналитик в области AI-инфраструктуры. "
                "Всегда отвечаешь на русском языке."
            ),
            llm=llm,
            max_iterations=5,
        )

        analysis_task = Task(
            # Вход Crew берётся ИЗ STATE FLOW — это вход данных в чёрный ящик
            description=(
                f"Проанализируй тему: {self.state.topic}. "
                "Дай 3-5 ключевых пунктов: в чём разница подхода, "
                "плюсы и минусы каждого варианта."
            ),
            expected_output="Структурированный список из 3-5 пунктов на русском языке.",
            agent=analyst,
        )

        crew = Crew(
            agents=[analyst],
            tasks=[analysis_task],
            process=Process.sequential,
            verbose=True,
        )

        crew_result = crew.kickoff()  # без stream=True вернёт CrewOutput, с stream=True — обёртку
        if not isinstance(crew_result, CrewOutput):  # сужение типа для Pylance
            raise TypeError("streaming-режим в этом эксперименте не поддерживается")

        # Выход Crew СОХРАНЯЕТСЯ В STATE FLOW — выход данных из чёрного ящика
        self.state.analysis = crew_result.raw
        return self.state.analysis
    
    
    # --- Шаг 3: второй Crew — писатель берёт анализ ИЗ STATE ---
    @listen("run_crew")
    def write_report(self, result):
        print("Шаг 3 (LLM): второй Crew — писатель работает с анализом из state")

        writer = Agent(
            role="Технический писатель",
            goal="Превратить технический анализ в читабельный отчёт для руководителя",
            backstory=(
                "Опытный технический писатель в IT. Пишешь ясно, структурированно, "
                "на русском языке."
            ),
            llm=llm,
            max_iterations=5,
        )

        report_task = Task(
            description=(
                "На основе анализа ниже подготовь отчёт для руководителя.\n\n"
                f"Анализ:\n{self.state.analysis}\n\n"
                "Структура отчёта: 1) краткое резюме в 2-3 предложениях, "
                "2) сравнение подходов по критериям, 3) рекомендация с обоснованием."
            ),
            expected_output="Отчёт на русском языке: резюме, сравнение, рекомендация.",
            agent=writer,
        )

        report_crew = Crew(
            agents=[writer],
            tasks=[report_task],
            process=Process.sequential,
            verbose=True,
        )

        report_result = report_crew.kickoff()
        if not isinstance(report_result, CrewOutput):
            raise TypeError("streaming-режим в этом эксперименте не поддерживается")

        self.state.report = report_result.raw
        return self.state.report

    


# --- Запуск ---
if __name__ == "__main__":
    flow = CrewFlow()
    final = flow.kickoff()          # запускает граф шагов от @start
    print("\n=== Финал Flow ===")
    print(final)
    print("\n=== Весь state после прогона ===")   # доска целиком: topic / analysis / report
    print(flow.state.model_dump())
