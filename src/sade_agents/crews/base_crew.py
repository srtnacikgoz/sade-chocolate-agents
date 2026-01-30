"""
Sade Chocolate - Base Crew Utilities.

Yardimci fonksiyonlar ve base class'lar.
Crew kompozisyonlarinda kullanilan ortak araclar.
"""

import time
from typing import Callable, TypeVar
from crewai import Task
from sade_agents.agents.base import SadeAgent

T = TypeVar("T")


def create_task_with_context(
    description: str,
    expected_output: str,
    agent: SadeAgent,
    context: list[Task] | None = None,
) -> Task:
    """
    Task olusturur, context dependency'leri ile.

    Args:
        description: Gorev aciklamasi
        expected_output: Beklenen cikti formati
        agent: Gorevi calistiracak agent
        context: Bagimli oldugu onceki task'lar (optional)

    Returns:
        Configured Task instance
    """
    task_kwargs = {
        "description": description,
        "expected_output": expected_output,
        "agent": agent,
    }
    if context:
        task_kwargs["context"] = context

    return Task(**task_kwargs)


def timed_execution(func: Callable[..., T]) -> Callable[..., tuple[T, float]]:
    """
    Fonksiyon calisma suresini olcer.

    Decorator olarak kullanilabilir.
    Returns tuple of (result, execution_time_seconds).

    Kullanim:
        @timed_execution
        def my_function():
            return "result"

        result, elapsed = my_function()
    """
    def wrapper(*args, **kwargs) -> tuple[T, float]:
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        return result, elapsed
    return wrapper


def requires_approval(agent: SadeAgent) -> bool:
    """
    Agent'in onay gerektirip gerektirmedigini kontrol eder.

    Supervised veya mixed autonomy level'e sahip agent'lar
    kritik kararlari almadan once kullanici onayi gerektirir.

    Args:
        agent: Kontrol edilecek SadeAgent instance

    Returns:
        True if agent.autonomy_level in ["supervised", "mixed"]
    """
    return agent.autonomy_level in ("supervised", "mixed")


__all__ = [
    "create_task_with_context",
    "timed_execution",
    "requires_approval",
]
