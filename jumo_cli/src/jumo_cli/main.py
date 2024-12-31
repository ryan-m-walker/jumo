import requests
from rich.console import Console

console = Console()


def main():
    while True:
        console.print("[User]: ", style="bold blue", end="")
        query = input("")

        if query.strip() == "exit" or query.strip() == "quit":
            break

        if query.strip() == "":
            continue

        res = requests.post("http://localhost:8000/chat", json={"input": query})

        console.print("[Jumo]: ", style="bold red", end="")
        print(res.json()["response"])


if __name__ == "__main__":
    main()
