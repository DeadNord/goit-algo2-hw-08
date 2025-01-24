import logging
import random
from typing import Dict
import time
import sys
import timeit
from colorama import init, Fore

init(autoreset=True)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s"
)
logger = logging.getLogger(__name__)


class ThrottlingRateLimiter:
    """
    Реалізація Rate Limiter із алгоритмом Throttling:
    - Кожен користувач має min_interval (10с за умовою).
    - Якщо з часу останнього повідомлення не минуло min_interval, не можна відправити.
    """

    def __init__(self, min_interval: float = 10.0):
        self.min_interval = min_interval
        # user_last_message[user_id] = таймштамп (time.time()) останнього повідомлення
        self.user_last_message: Dict[str, float] = {}

    def can_send_message(self, user_id: str) -> bool:
        """
        Перевіряє, чи може user_id відправити повідомлення зараз.
        Якщо користувача ще немає або час минув >= min_interval => True
        """
        current_time = time.time()
        if user_id not in self.user_last_message:
            return True  # перше повідомлення завжди дозволене
        last_time = self.user_last_message[user_id]
        return (current_time - last_time) >= self.min_interval

    def record_message(self, user_id: str) -> bool:
        """
        Реєструє спробу відправити повідомлення.
        Якщо can_send_message==True, оновлює час і повертає True.
        Інакше повертає False.
        """
        if self.can_send_message(user_id):
            self.user_last_message[user_id] = time.time()
            return True
        else:
            return False

    def time_until_next_allowed(self, user_id: str) -> float:
        """
        Повертає час (секунди), через скільки стане можливим відправити повідомлення.
        Якщо можна прямо зараз — 0.0
        """
        if user_id not in self.user_last_message:
            return 0.0
        current_time = time.time()
        last_time = self.user_last_message[user_id]
        diff = current_time - last_time
        wait = self.min_interval - diff
        return max(wait, 0.0)


def demo_scenario():
    """
    Демонстраційна функція:
      - відправляємо 10 повідомлень (user_id=1..5),
      - очікуємо 10 секунд (щоб переконатися, що інтервал справді відкритий),
      - ще 10 повідомлень.
    """
    limiter = ThrottlingRateLimiter(min_interval=10.0)

    print(Fore.CYAN + "\n=== Симуляція потоку повідомлень (Throttling) ===")
    for message_id in range(1, 11):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"{Fore.GREEN if result else Fore.YELLOW}"
            + f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування %.1fс)' % wait_time}"
        )

        # Симулюємо випадкову затримку між повідомленнями
        time.sleep(random.uniform(0.1, 1.0))

    print(Fore.CYAN + "\nОчікуємо 10 секунд...")
    time.sleep(10)

    print(Fore.CYAN + "\n=== Нова серія повідомлень після очікування ===")
    for message_id in range(11, 21):
        user_id = message_id % 5 + 1
        result = limiter.record_message(str(user_id))
        wait_time = limiter.time_until_next_allowed(str(user_id))

        print(
            f"{Fore.GREEN if result else Fore.YELLOW}"
            + f"Повідомлення {message_id:2d} | Користувач {user_id} | "
            f"{'✓' if result else f'× (очікування %.1fс)' % wait_time}"
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
        + f"\nЧас виконання сценарію Throttling (з урахуванням sleep) = {elapsed:.2f} сек"
    )


if __name__ == "__main__":
    main()
