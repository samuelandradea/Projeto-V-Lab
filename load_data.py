"""Script de carga: envia N abastecimentos com dados fake para a API."""

import argparse
import random
import sys

import httpx
from faker import Faker

fake = Faker("pt_BR")

API_URL = "http://localhost:8000/api/v1/abastecimentos"
API_KEY = "vlab-secret-key-2024"

TIPOS = ["GASOLINA", "ETANOL", "DIESEL"]
PRICE_RANGES = {
    "GASOLINA": (5.00, 8.50),
    "ETANOL": (3.50, 6.00),
    "DIESEL": (5.50, 9.00),
}


def generate_valid_cpf() -> str:
    digits = [random.randint(0, 9) for _ in range(9)]

    total = sum(d * (10 - i) for i, d in enumerate(digits))
    remainder = total % 11
    digits.append(0 if remainder < 2 else 11 - remainder)

    total = sum(d * (11 - i) for i, d in enumerate(digits))
    remainder = total % 11
    digits.append(0 if remainder < 2 else 11 - remainder)

    return "".join(str(d) for d in digits)


def main():
    parser = argparse.ArgumentParser(description="Load fake data into the API")
    parser.add_argument("-n", type=int, default=50, help="Number of records to send")
    parser.add_argument("--url", default=API_URL, help="API URL")
    parser.add_argument("--api-key", default=API_KEY, help="API Key")
    args = parser.parse_args()

    success = 0
    errors = 0

    with httpx.Client(timeout=10) as client:
        for i in range(args.n):
            tipo = random.choice(TIPOS)
            low, high = PRICE_RANGES[tipo]
            payload = {
                "id_posto": random.randint(1, 500),
                "data_hora": fake.date_time_between(
                    start_date="-1y", end_date="now"
                ).isoformat(),
                "tipo_combustivel": tipo,
                "preco_por_litro": round(random.uniform(low, high), 2),
                "volume_abastecido": round(random.uniform(5, 80), 2),
                "cpf_motorista": generate_valid_cpf(),
            }
            try:
                resp = client.post(
                    args.url,
                    json=payload,
                    headers={"X-API-Key": args.api_key},
                )
                if resp.status_code == 201:
                    success += 1
                else:
                    errors += 1
                    print(f"[{i+1}] Error {resp.status_code}: {resp.text}")
            except Exception as e:
                errors += 1
                print(f"[{i+1}] Request failed: {e}")

    print(f"\nDone: {success} success, {errors} errors out of {args.n} requests")


if __name__ == "__main__":
    main()
