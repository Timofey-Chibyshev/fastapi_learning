from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.future import select
from fastapi import HTTPException


from app.dao.base import BaseDAO
from app.fields.models import Field
from app.farmers.models import Farmer


class FieldsDAO(BaseDAO):
    model = Field

    @classmethod
    async def find_fields(cls, session: AsyncSession, **field_data):
        query = select(cls.model).options(joinedload(cls.model.farmer)).filter_by(**field_data)
        result = await session.execute(query)
        fields_info = result.scalars().all()

        fields_data = []
        for field in fields_info:
            field_dict = field.to_dict()
            field_dict['farmer'] = field.farmer.last_name if field.farmer else None
            fields_data.append(field_dict)

        return fields_data

    @classmethod
    async def find_full_data(cls, session: AsyncSession, field_id: int):
        query = select(cls.model).options(joinedload(cls.model.farmer)).filter_by(id=field_id)
        result = await session.execute(query)
        field_info = result.scalar_one_or_none()

        if not field_info:
            raise HTTPException(status_code=404, detail="Field not found")

        field_data = field_info.to_dict()
        field_data['farmer'] = field_info.farmer.last_name
        return field_data