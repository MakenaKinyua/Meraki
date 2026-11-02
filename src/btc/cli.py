import logging
import sqlite3

from src.btc.config import DB_PATH
from src.explanations.generator import explain_ingredient


def main():
    logging.basicConfig(level=logging.WARNING)   

    conn = sqlite3.connect(DB_PATH)
    print("Hello, type an ingredient name eg: Azelaic acid. Use 'q' to quit).\n")

    try:
        while True:
            name = input("Ingredient: ").strip()
            if name.lower() in {"q", "quit", "exit"}:
                break
            if not name:
                continue

            result = explain_ingredient(conn, name)

            if result.status == "ok":
                print(f"\n[{result.match_type} match: {result.matched_name}]")
                print(result.explanation, "\n")
            elif result.status == "not_found":
                print(f"\nNo match found for '{name}'.\n")
            else:
                print(f"\nSomething went wrong: {result.error}\n")
    finally:
        conn.close()


if __name__ == "__main__":
    main()