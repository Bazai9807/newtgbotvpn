from __future__ import annotations

from dataclasses import dataclass
from environs import Env


@dataclass
class TgBot:
    token: str  # Токен для доступа к телеграм-боту
    admin_ids: list[int]  # Список id администраторов бота
    serv: list[str]
    ykassa: list[str]


@dataclass
class Config:
    tg_bot: TgBot


def load_config(path: str | None = None) -> Config:

    env: Env = Env()
    env.read_env(path)

    return Config(tg_bot=TgBot(token=env('BOTV_TOKEN'),
                               admin_ids=list(map(int, env.list('ADMIN_IDS'))),
                               serv=env.list('SERV'),
                               ykassa=env.list('YOUKASSA'))
                  )
