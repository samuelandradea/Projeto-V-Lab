from app.core.validators import validate_cpf
from app.models.abastecimento import TipoCombustivel
from app.services.abastecimento import check_anomaly


class TestCPFValidation:
    def test_valid_cpf(self):
        assert validate_cpf("52998224725") is True

    def test_invalid_cpf_wrong_digits(self):
        assert validate_cpf("52998224720") is False

    def test_invalid_cpf_all_same_digits(self):
        assert validate_cpf("11111111111") is False

    def test_invalid_cpf_wrong_length(self):
        assert validate_cpf("1234567") is False

    def test_invalid_cpf_non_numeric(self):
        assert validate_cpf("5299822472a") is False


class TestAnomalyDetection:
    def test_normal_price_not_flagged(self):
        assert check_anomaly(TipoCombustivel.GASOLINA, 6.00) is False

    def test_price_at_threshold_not_flagged(self):
        assert check_anomaly(TipoCombustivel.GASOLINA, 7.50) is False

    def test_price_above_threshold_flagged(self):
        assert check_anomaly(TipoCombustivel.GASOLINA, 7.51) is True

    def test_diesel_anomaly(self):
        assert check_anomaly(TipoCombustivel.DIESEL, 8.13) is True

    def test_etanol_normal(self):
        assert check_anomaly(TipoCombustivel.ETANOL, 4.00) is False
