from crewai import LLM, Agent, Crew, Process, Task

# --- Менеджер: новая модель с tools (11.9B) ---
manager_llm = LLM(
    model="ollama/gemma4:12b",
    base_url="http://localhost:11434",
)

# --- Исполнители: старые, проверенные ---
# Контроль переменных: меняем ТОЛЬКО менеджера
analyst = Agent(
    role="Аналитик",
    goal="Сделать краткий анализ темы",
    backstory="Опытный аналитик. Анализирует тему и выделяет главные тезисы.",
    llm=LLM(model="ollama/qwen2.5-coder:7b", base_url="http://localhost:11434"),
    max_iter=5,
)

writer = Agent(
    role="Писатель",
    goal="Написать короткий отчёт на основе анализа",
    backstory="Технический писатель. Пишет структурированные тексты по готовым тезисам.",
    llm=LLM(model="ollama/qwen2.5-coder:7b", base_url="http://localhost:11434"),
    max_iter=5,
)

task1 = Task(
    description="Проанализируй тему: 'локальные LLM vs облачные API'. Выдели 3 главных тезиса.",
    expected_output="3 тезиса, по одному предложению на каждый.",
    agent=analyst,
)

task2 = Task(
    description="Напиши отчёт на основе анализа.",
    expected_output="Короткий отчёт, 5-6 предложений.",
    agent=writer,
)

crew = Crew(
    agents=[analyst, writer],
    tasks=[task1, task2],
    process=Process.hierarchical,
    manager_llm=manager_llm,
    verbose=True,
)

result = crew.kickoff()
print("\n=== ИТОГ ===")
print(result)
