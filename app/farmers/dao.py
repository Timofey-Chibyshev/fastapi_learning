from sqlalchemy.orm import joinedload, selectinload
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.farmers.models import Farmer
from app.fields.models import Field
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError


class FarmerDAO(BaseDAO):
    model = Farmer

    # @classmethod
    # async def find_all(cls, **filter_by):
    #     async with async_session_maker() as session:
    #         # Преобразуем filter_by в список условий filter
    #         filters = [getattr(cls.model, key) == value for key, value in filter_by.items()]
    #         query = select(cls.model).filter(*filters)
    #
    #         # Добавим предзагрузку для связанного поля, если оно есть
    #         # Пример: если у вас есть поле 'fields', которое нужно загрузить заранее
    #         query = query.options(selectinload(cls.model.fields))  # Можно использовать joinedload или selectinload
    #
    #         result = await session.execute(query)
    #         return result.scalars().all()

    @classmethod
    async def find_full_data(cls, farmer_id: int):
        """
        Получает полную информацию о фермере, включая все его поля.
        """
        async with async_session_maker() as session:
            # Создаем запрос для получения фермера с его полями
            query = (select(cls.model)
                     .options(joinedload(cls.model.fields))  # Присоединяем связанные поля
                     .filter_by(id=farmer_id))

            # Выполняем запрос
            result = await session.execute(query)
            farmer_info = result.unique().scalar_one_or_none()

            # Если фермер не найден, возвращаем None
            if not farmer_info:
                return None

            # Преобразуем данные фермера в словарь
            farmer_data = farmer_info.to_dict()

            # Добавляем информацию о каждом поле фермера
            farmer_data['fields'] = [field.to_dict() for field in farmer_info.fields]

            return farmer_data

    # @classmethod
    # async def add(cls, **values):
    #     async with async_session_maker() as session:
    #         async with session.begin():
    #             # Создаем нового фермера
    #             new_instance = cls.model(**values)
    #             session.add(new_instance)
    #
    #             try:
    #                 # Пытаемся сохранить изменения
    #                 await session.commit()
    #             except IntegrityError as e:
    #                 await session.rollback()
    #                 # Проверяем, относится ли ошибка к дублирующему email
    #                 if "farmers_email_key" in str(e):
    #                     raise ValueError("Этот email уже используется. Пожалуйста, введите другой.")
    #                 # Если ошибка не связана с уникальным ограничением, пробрасываем дальше
    #                 raise e
    #             return new_instance
