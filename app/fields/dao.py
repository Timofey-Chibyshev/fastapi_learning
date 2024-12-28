from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException
from sqlalchemy.orm import joinedload

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.farmers.models import Farmer
from app.fields.models import Field
from sqlalchemy.future import select
from sqlalchemy import insert, delete, event, update


@event.listens_for(Field, 'after_insert')
async def receive_after_insert(mapper, connection, target):
    # Получаем ID фермера
    farmer_id = target.farmer_id

    # Извлекаем текущие поля фермера
    result = await connection.execute(
        select(Farmer).where(Farmer.id == farmer_id)
    )
    farmer = result.scalar_one_or_none()  # Получаем одного фермера или None

    # Проверяем, существует ли фермер
    if farmer is None:
        raise ValueError(f"Фермер с ID {farmer_id} не существует")

    # Получаем текущее состояние полей
    current_fields = farmer.fields or []  # Получаем текущие поля или пустой список

    # Обновляем список полей фермера, добавляя новое поле
    updated_fields = current_fields + [target]

    # Выполняем обновление записи фермера с новыми полями
    farmer.fields = updated_fields  # Обновляем поле в модели
    await connection.commit()  # Не забывайте коммитить изменения


@event.listens_for(Field, 'after_delete')
def receive_after_delete(mapper, connection, target):
    farmer_id = target.farmer_id
    # Удаляем поле из списка полей фермера
    connection.execute(
        update(Farmer)
        .where(Farmer.id == farmer_id)
        .values(fields=[f for f in Farmer.fields if f.id != target.id])
    )


class FieldsDAO(BaseDAO):
    model = Field

    @classmethod
    async def find_fields(cls, **field_data):
        async with async_session_maker() as session:
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
    async def find_full_data(cls, field_id):
        async with async_session_maker() as session:
            query = select(cls.model).options(joinedload(cls.model.farmer)).filter_by(id=field_id)
            result = await session.execute(query)
            field_info = result.scalar_one_or_none()

            if not field_info:
                return None

            field_data = field_info.to_dict()
            field_data['farmer'] = field_info.farmer.last_name
            return field_data

    @classmethod
    async def add_field(cls, field_data: dict) -> int:
        async with async_session_maker() as session:
            async with session.begin():
                # Проверяем, существует ли фермер с данным ID
                farmer_id = field_data.get('farmer_id')
                farmer = await session.get(Farmer, farmer_id)

                if not farmer:
                    raise HTTPException(status_code=404, detail=f"Фермер с ID {farmer_id} не существует")

                # Проверяем, существует ли поле с таким же именем
                existing_field_stmt = select(Field).where(Field.name == field_data['name'])
                existing_field_result = await session.execute(existing_field_stmt)
                existing_field = existing_field_result.scalar_one_or_none()

                if existing_field:
                    # Поле уже существует, возвращаем его ID
                    raise HTTPException(
                        status_code=400,
                        detail=f"Поле с именем '{field_data['name']}' уже существует"
                    )

                # Если поле не существует, добавляем новое
                new_field = Field(**field_data)
                session.add(new_field)
                await session.flush()  # Генерируем ID нового поля

                return new_field.id

    @classmethod
    async def delete_field_by_id(cls, field_id: int):
        async with async_session_maker() as session:
            async with session.begin():
                # Находим поле по ID
                query = select(Field).filter_by(id=field_id)
                result = await session.execute(query)
                field_to_delete = result.scalar_one_or_none()

                # Проверяем, существует ли поле
                if not field_to_delete:
                    return None

                # Удаляем поле
                await session.execute(delete(Field).filter_by(id=field_id))

                await session.commit()

                return field_id

    @classmethod
    async def update_field(cls, field_id: int, field_data: dict):
        async with async_session_maker() as session:

            # Проверяем, существует ли поле с данным ID
            query = select(cls.model).filter_by(id=field_id)
            result = await session.execute(query)
            field = result.scalar_one_or_none()

            if not field:
                return {"error": f"Поле с ID {field_id} не найдено"}

            # Проверяем, существует ли фермер с данным ID
            farmer_id = field_data.get('farmer_id')
            farmer = await session.get(Farmer, farmer_id)

            if not farmer:
                raise HTTPException(status_code=404, detail=f"Фермер с ID {farmer_id} не существует")


            # Обновляем поле
            update_stmt = (
                update(cls.model)
                .where(cls.model.id == field_id)
                .values(**field_data)
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(update_stmt)
            await session.commit()

            return {"success": f"Поле с ID {field_id} успешно обновлено"}
