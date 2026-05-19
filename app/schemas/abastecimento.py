from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.core.validators import validate_cpf
from app.models.abastecimento import TipoCombustivel


class AbastecimentoCreate(BaseModel):
    id_posto: int = Field(..., gt=0)
    data_hora: datetime
    tipo_combustivel: TipoCombustivel
    preco_por_litro: float = Field(..., gt=0)
    volume_abastecido: float = Field(..., gt=0)
    cpf_motorista: str

    @field_validator("data_hora")
    @classmethod
    def data_hora_not_future(cls, v: datetime) -> datetime:
        from datetime import timezone

        now = datetime.now(timezone.utc)
        v_aware = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        if v_aware > now:
            raise ValueError("data_hora cannot be in the future")
        return v

    @field_validator("cpf_motorista")
    @classmethod
    def cpf_must_be_valid(cls, v: str) -> str:
        if not validate_cpf(v):
            raise ValueError("CPF is invalid (check digits do not match)")
        return v


class AbastecimentoResponse(BaseModel):
    id: int
    id_posto: int
    data_hora: datetime
    tipo_combustivel: TipoCombustivel
    preco_por_litro: float
    volume_abastecido: float
    cpf_motorista: str
    improper_data: bool

    model_config = {"from_attributes": True}


class PaginatedResponse(BaseModel):
    total: int
    page: int
    size: int
    items: list[AbastecimentoResponse]
