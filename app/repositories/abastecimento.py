from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.abastecimento import Abastecimento, TipoCombustivel


class AbastecimentoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, abastecimento: Abastecimento) -> Abastecimento:
        self.db.add(abastecimento)
        await self.db.commit()
        await self.db.refresh(abastecimento)
        return abastecimento

    async def list_paginated(
        self,
        page: int,
        size: int,
        tipo_combustivel: TipoCombustivel | None = None,
        data_inicio: datetime | None = None,
        data_fim: datetime | None = None,
    ) -> tuple[list[Abastecimento], int]:
        query = select(Abastecimento)
        count_query = select(func.count()).select_from(Abastecimento)

        if tipo_combustivel:
            query = query.where(Abastecimento.tipo_combustivel == tipo_combustivel)
            count_query = count_query.where(
                Abastecimento.tipo_combustivel == tipo_combustivel
            )
        if data_inicio:
            query = query.where(Abastecimento.data_hora >= data_inicio)
            count_query = count_query.where(Abastecimento.data_hora >= data_inicio)
        if data_fim:
            query = query.where(Abastecimento.data_hora <= data_fim)
            count_query = count_query.where(Abastecimento.data_hora <= data_fim)

        total = (await self.db.execute(count_query)).scalar() or 0

        offset = (page - 1) * size
        query = query.offset(offset).limit(size).order_by(Abastecimento.id)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def get_by_cpf(self, cpf: str) -> list[Abastecimento]:
        query = (
            select(Abastecimento)
            .where(Abastecimento.cpf_motorista == cpf)
            .order_by(Abastecimento.data_hora.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
