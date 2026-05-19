from app.models.abastecimento import TipoCombustivel

REFERENCE_PRICES: dict[TipoCombustivel, float] = {
    TipoCombustivel.GASOLINA: 6.00,
    TipoCombustivel.ETANOL: 4.20,
    TipoCombustivel.DIESEL: 6.50,
}

ANOMALY_THRESHOLD = 0.25


def check_anomaly(tipo_combustivel: TipoCombustivel, preco_por_litro: float) -> bool:
    reference = REFERENCE_PRICES[tipo_combustivel]
    return preco_por_litro > reference * (1 + ANOMALY_THRESHOLD)
