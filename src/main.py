from __future__ import annotations
import argparse, sys
from typing import List
from .input_manager import load_inputs
from .crawler import SiteCrawler
from .models import RestaurantResult, MenuItem
from .output_generator import save_results

def should_escalate(heuristic_candidates, min_conf=0.65) -> bool:
    if not heuristic_candidates:
        return True
    if max(c[6] for c in heuristic_candidates) < min_conf:
        return True
    return False

def map_type_label(code: str, menutypes: dict) -> str:
    return menutypes.get(code, code)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="input/restaurants.json")
    ap.add_argument("--types", default="input/menutypes.json")
    ap.add_argument("--formats", default="input/menuformats.json")
    ap.add_argument("--out", default="output/output.json")
    ap.add_argument("--prompt", default="prompts/menu_agent_prompt.txt")
    ap.add_argument("--depth", type=int, default=3)
    args = ap.parse_args()

    restaurants, menutypes, formats = load_inputs(args.input, args.types, args.formats)
    results: List[RestaurantResult] = []

    for name, url in restaurants.items():
        print(f"\n[Processing]: {name} -> {url}")
        res = RestaurantResult(name=name, url=url)
        crawler = SiteCrawler(name, url, menutypes)
        crawler.crawl_site()

        # TODO: let's not expose the crawler internals, wrap it in get function and shallow copy
        res.cookie_banner_accept = crawler._cookie_accept
        res.menus = crawler._menu_items

        if not res.menus:
            res.status = "no_menus_found"

        results.append(res)

    save_results(args.out, results)
    print(f"\n(I hope) Done. Saved in {args.out}")

if __name__ == "__main__":
    sys.exit(main())
