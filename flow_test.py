from pydantic import BaseModel

from crewai.flow.flow import Flow, listen, start

class TopicState(BaseModel):
    topic: str = ""

# --- Класс Flow: state — обычный dict ---
class TypedFlow(Flow[TopicState]):

    # @start: точка входа, выполняется первым автоматически
    @start()
    def prepare(self):
        print("Шаг 1: подготовка")
        # записываем данные в state — общий "рюкзак" для всех шагов
        self.state.topic = "локальные LLM vs облачные API"   # доступ как к атрибуту, не через ["..."]
        return "данные подготовлены"   # возвращаемое значение уйдёт в слушателя

    # @listen: сработает ПОСЛЕ завершения prepare()
    # результат prepare() приходит как аргумент result
    @listen("prepare")
    def finish(self, result):
        print("Шаг 2: завершение")
        # читаем из state то, что положил другой шаг
        print("Тема из state:", self.state.topic)
        print("Результат из предыдущего шага:", result)
        return "Flow завершён"


# --- Запуск ---
if __name__ == "__main__":
    flow = TypedFlow()
    final = flow.kickoff()          # запускает граф от @start
    print("Финальный результат:", final)
