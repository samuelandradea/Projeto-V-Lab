from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import verify_api_key
from app.core.database import get_db
from app.models.abastecimento import Abastecimento, TipoCombustivel
from app.repositories.abastecimento import AbastecimentoRepository
from app.schemas.abastecimento import (
    AbastecimentoCreate,
    AbastecimentoResponse,
    PaginatedResponse,
)
from app.services.abastecimento import check_anomaly

router = APIRouter(prefix="/api/v1", tags=["abastecimentos"])


@router.post(
    "/abastecimentos",
    response_model=AbastecimentoResponse,
    status_code=201,
    dependencies=[Depends(verify_api_key)],
)
async def create_abastecimento(
    payload: AbastecimentoCreate,
    db: AsyncSession = Depends(get_db),
):
    improper = check_anomaly(payload.tipo_combustivel, payload.preco_por_litro)

    abastecimento = Abastecimento(
        id_posto=payload.id_posto,
        data_hora=payload.data_hora,
        tipo_combustivel=payload.tipo_combustivel,
        preco_por_litro=payload.preco_por_litro,
        volume_abastecido=payload.volume_abastecido,
        cpf_motorista=payload.cpf_motorista,
        improper_data=improper,
    )

    repo = AbastecimentoRepository(db)
    created = await repo.create(abastecimento)
    return created


@router.get("/abastecimentos", response_model=PaginatedResponse)
async def list_abastecimentos(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    tipo_combustivel: TipoCombustivel | None = None,
    data_inicio: datetime | None = None,
    data_fim: datetime | None = None,
    db: AsyncSession = Depends(get_db),
):
    repo = AbastecimentoRepository(db)
    items, total = await repo.list_paginated(
        page=page,
        size=size,
        tipo_combustivel=tipo_combustivel,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )
    return PaginatedResponse(total=total, page=page, size=size, items=items)


@router.get(
    "/motoristas/{cpf}/historico",
    response_model=list[AbastecimentoResponse],
)
async def get_historico(cpf: str, db: AsyncSession = Depends(get_db)):
    repo = AbastecimentoRepository(db)
    return await repo.get_by_cpf(cpf)
