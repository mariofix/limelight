import requests


def fetch(slug: str, url: str = None) -> dict:
    # Fix if needed
    if url and url[-1] == "/":
        url = f"{url}json"
    elif url and url[-1] != "/":
        url = f"{url}/json"

    # Set if not available
    if not url:
        url = f"https://pypi.org/pypi/{slug}/json"

    print(f"Fetching {url}")
    data = requests.get(url)
    data.raise_for_status()
    json_data = data.json()
    salida: dict = {"pypi_json_url": url, "last_serial": json_data["last_serial"], **json_data["info"]}
    return salida
