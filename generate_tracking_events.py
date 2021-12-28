import json
import pickle
import time
from pathlib import Path
from random import choice, randint

import yaml
from usp.tree import sitemap_tree_for_homepage


def get_tracking_events_urls(alias: str, web_homepage: str) -> list:
    """
    Retrieves list of pages for given web homepage - from internet or saved file. In
    case of retrieval from internet list is saved in local folder using provided alias
        Parameters:
            :param alias: alias for web homepage
            :param web_homepage: web homepage internet address
        Returns:
            list of pages urls
    """
    if Path(alias + ".pkl").is_file():
        with open(alias + ".pkl", "rb") as f:
            taxfix_pages_urls = pickle.load(f)
    else:
        tree = sitemap_tree_for_homepage(web_homepage)
        taxfix_pages_urls = [page.url for page in tree.all_pages()]
        with open(alias + ".pkl", "wb") as f:
            pickle.dump(taxfix_pages_urls, f)
    return taxfix_pages_urls


def generate_tracking_event(pages: list, max_amount_users: int) -> dict:
    """
    Generates simulated single tracking event
        Parameters:
            :param pages: list of web_page pages
            :param max_amount_users: maximum id of an user to generate
            :r: object
        Returns:
            dict with single event generated data
    """
    user_id = randint(0, max_amount_users)
    return {
        "Id": user_id,
        "Url": choice(pages),
        "Timestamp": int(time.time()) - randint(0, 5),
    }


def generate_tracking_events(
    pages: list, n_events: int = 5, max_amount_users: int = 5
) -> None:
    """
    Creating generated_events.txt file with tracking events
        Parameters:
            :param pages: list of web_page pages
            :param n_events: int number of events to generate
            :param max_amount_users: int maximum id of an user to generate
    """
    with open("generated_events.txt", "w") as f:
        for event_id in range(n_events):
            event = generate_tracking_event(
                max_amount_users=max_amount_users, pages=pages
            )
            f.write(str(json.dumps(event)) + " \n")
    print("Events generated")


if __name__ == "__main__":
    configuration = yaml.load(
        open("configuration.yml", "r"), Loader=yaml.FullLoader
    ).get("events_generator")
    pages = get_tracking_events_urls(
        alias=configuration["alias"], web_homepage=configuration["web_homepage"]
    )
    generate_tracking_events(
        pages=pages,
        n_events=configuration["n_events"],
        max_amount_users=configuration["max_amount_users"],
    )
