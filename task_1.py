import logging
import random
from typing import Dict, Deque
import time
import sys
import timeit
from colorama import init, Fore
from collections import deque

init(autoreset=True)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)


class SlidingWindowRateLimiter:
    """
    Реалізація Rate Limiter із алгоритмом Sliding Window.
    Для кожного user_id зберігаємо deque з таймштампами (time.time()).
    Користувач може надіслати max_requests за window_size сек.
    """

    def __init__(self, window_size: int = 10, max_requests: int = 1):
        self.window_size = window_size
        self.max_requests = max_requests
        # user_messages[user_id] = deque([...timestamps...])
        self.user_messages: Dict[str, Deque[float]] = {}

    def _cleanup_window(self, user_id: str, current_time: float) -> None:
        """Видаляє з deque усі таймштампи, що вийшли за межі window_size."""
        if user_id not in self.user_messages:
            return
        timestamps = self.user_messages[user_id]
        cutoff = current_time - self.window_size
        while timestamps and timestamps[0] < cutoff:
            timestamps.popleft()
        # Якщо порожній — видаляємо
        if not timestamps:
            del self.user_messages[user_id]

    def can_send_message(self, user_id: str) -> bool:
        """Чи може user_id відправити повідомлення зараз?"""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        if user_id not in self.user_messages:
            return True
        return len(self.user_messages[user_id]) < self.max_requests

    def record_message(self, user_id: str) -> bool:
        """
        Реєструє повідомлення. Повертає True, якщо вдалося (не перевищено ліміт),
        інакше False.
        """
        current_time = time.time()
        self._cleanup_window(user_id, current_time)

        if user_id not in self.user_messages:
            self.user_messages[user_id] = deque()

        timestamps = self.user_messages[user_id]
        if len(timestamps) < self.max_requests:
            timestamps.append(current_time)
            return True
        else:
            return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """Скільки секунд треба зачекати, щоб було дозволено відправити?"""
        current_time = time.time()
        self._cleanup_window(user_id, current_time)
        if user_id not in self.user_messages:
            return 0.0
        timestamps = self.user_messages[user_id]
        if len(timestamps) < self.max_requests:
            return 0.0
        earliest = timestamps[0]
        allow_time = earliest + self.window_size
        wait = allow_time - current_time
        return max(wait, 0.0)


def demo_scenario():
    """
    Демонстраційна функція, що відтворює логіку:
      - 10 повідомлень від користувачів 1..5,
      - очікування 4 сек,
      - ще 10 повідомлень.
    Використовує SlidingWindowRateLimiter(window_size=10, max_requests=1).
    """
    limiter = SlidingWindowRateLimiter(window_size=10, max_requests=1)

    print(Fore.CYAN + "\n=== Симуляція потоку повідомлень (10 шт) ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1
        can_send = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"{Fore.GREEN if can_send else Fore.YELLOW}"
            + f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if can_send else f'× (очікування %.1fс)' % wait_time}"
        )

        time.sleep(random.uniform(0.1, 1.0))

    print(Fore.CYAN + "\nОчікуємо 4 секунди...")
    time.sleep(4)

    print(Fore.CYAN + "\n=== Нова серія повідомлень після очікування (ще 10 шт) ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        can_send = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"{Fore.GREEN if can_send else Fore.YELLOW}"
            + f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if can_send else f'× (очікування %.1fс)' % wait_time}"
        )

        time.sleep(random.uniform(0.1, 1.0))


def main():
    sys.setrecursionlimit(10**7)

    setup_code = "from __main__ import demo_scenario"
    stmt_code = "demo_scenario()"

    # Запустимо 1 раз (number=1).
    elapsed = timeit.timeit(stmt=stmt_code, setup=setup_code, number=1)
    print(
        Fore.CYAN
        + f"\nЧас виконання сценарію (з урахуванням time.sleep та random.uniform) = {elapsed:.2f} сек"
    )


if __name__ == "__main__":
    main()
