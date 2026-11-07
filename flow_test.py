from crewai.flow.flow import Flow,and_,or_,router, listen, start
from pydantic import BaseModel
from typing import Literal


class TopicState(BaseModel):
    topic: str = ""
    length: int = 0


# --- Класс Flow: state — обычный dict ---
class RouterFlow(Flow[TopicState]):
    # @start: точка входа, выполняется первым автоматически
    @start()
    def prepare(self):
        print("Шаг 1: подготовка")
        self.state.topic = "локальные LLM vs облачные API"
        self.state.length = len(self.state.topic)  # считаем метрику сразу
        return "данные подготовлены"
    
        # --- Два независимых шага: оба после prepare ---
    @listen("prepare")
    def step_a(self, result):
        print("step_a выполнен")
        return "результат A"

    @listen("prepare")
    def step_b(self, result):
        print("step_b выполнен")
        return "результат B"


    # --- Шаг 2: стрелка на путях ---
    # @router("prepare") = "после prepare() запусти меня"
    # метод НЕ делает работу — только возвращает метку-строку
    @router("prepare")
    def classify(self, result)-> Literal['long', 'short']:
        print(f"Шаг 2: классификация (длина = {self.state.length})")
        if self.state.length > 30:
            return "long"
        return "short"
    
    # --- Ветка А: слушатель подписан на МЕТКУ "long" ---
    # обратите внимание: триггер — имя РОУТЕР-МЕТОДА ("classify"),
    # а метка приходит одним аргументом
    @listen("long")
    def handle_long(self,label):  # label == "long"
        print("Ветка LONG: тема длинная, делаем развёрнутый разбор")
        return f"long-ветка для: {self.state.topic}"

    # --- Ветка B: слушатель подписан на МЕТКУ "short" ---
    @listen("short")
    def handle_short(self,label):  # label == "short"
        print("Ветка SHORT: тема короткая, короткий конспект")
        return f"short-ветка для: {self.state.topic}"
    
        # --- or_: сработает, когда завершится ЛЮБОЙ из step_a/step_b ---
    @listen(or_("step_a", "step_b"))
    def on_any(self, result):
        print(f"or_ сработал, пришло: {result!r}")
        return "or-шаг завершён"

        # --- and_: сработает, когда завершатся ОБА step_a и step_b ---
    @listen(and_("step_a", "step_b"))
    def on_all(self, result):
        print(f"and_ сработал, пришло: {result!r}")
        return "and-шаг завершён"


# --- Запуск ---
if __name__ == "__main__":
    flow = RouterFlow()
    path = flow.plot("flow_test_graph.html", show=False) # docs: .html добавится автоматически
    print("Схема графа:", path)
    final = flow.kickoff()  # запускает граф от @start
    print("Финальный результат:", final)
