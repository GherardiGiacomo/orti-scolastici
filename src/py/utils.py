import sys
import traceback
from pathlib import Path
from types import TracebackType

import requests
from bs4 import BeautifulSoup
from dotenv import dotenv_values
from loguru import logger

from src.py.exc import MissingDBUrlError


def handle_exception(
    exc_type: type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType | None,
) -> None:
    logger.exception(
        "Uncaught exception occurred\n"
        f"Type: {exc_type}\n"
        f"Value: {exc_value}\n"
        f"Traceback:\n{''.join(traceback.format_tb(exc_traceback))}",
    )


sys.excepthook = handle_exception

ENV_VARS = dotenv_values(Path(__file__).parent.parent.parent / ".env")


def get_db_url() -> str:
    env_db_url = ENV_VARS.get("DB_URL")
    if env_db_url:
        return f"postgresql://{env_db_url.split('://')[1]}"
    raise MissingDBUrlError


def parse_db_url(url: str) -> tuple[str, str, str, str, str]:
    host = url.split("@")[1].split(":")[0]
    try:
        port = url.split(f"{host}:")[1].split("/")[0]
    except IndexError:
        port = "5432"
    user = url.split("//")[1].split(":")[0]
    password = url.split(":")[2].split("@")[0]
    database = url.split("/")[-1]
    return host, port, user, password, database


def parse_italian_municipalities() -> None:
    municipalities_filepath = (
        Path(__file__).parent / "custom_data" / "italian_municipalities.py"
    )
    if Path.exists(municipalities_filepath):
        return
    r = requests.get(
        "https://dait.interno.gov.it/territorio-e-autonomie-locali/sut/elenco_codici_comuni.php",
        headers={
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
            ),
        },
        timeout=10,
    )
    soup = BeautifulSoup(r.text, "html.parser")
    data: list[tuple[str, str]] = []
    for row in soup.find("table").find("tbody").find_all("tr"):  # type: ignore # noqa: PGH003, E501
        td_tags = row.find_all("td")  # type: ignore # noqa: PGH003
        if len(td_tags) >= 2:  # type: ignore # noqa: PGH003
            municipality = td_tags[1].text.strip()  # type: ignore # noqa: PGH003
            province = td_tags[2].text.strip()  # type: ignore # noqa: PGH003
            data.append((municipality, province))  # type: ignore # noqa: PGH003
    with Path.open(municipalities_filepath, "w") as f:
        f.write("municipalities = [\n")
        for d in data:
            municipality, province = d
            f.write(f'    ("{municipality}", "{province}"),\n')
        f.write("]\n")


parse_italian_municipalities()
