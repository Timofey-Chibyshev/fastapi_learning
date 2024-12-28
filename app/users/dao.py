from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload, joinedload

from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.users.models import User, Role, UserRoles
from sqlalchemy.future import select


class UsersDAO(BaseDAO):
    model = User

    @classmethod
    async def create_role(cls, role_name: str):
        async with async_session_maker() as session:
            async with session.begin():
                query = select(Role).filter_by(name=role_name)
                result = await session.execute(query)
                if result.scalar_one_or_none():
                    raise ValueError("Роль уже существует!")

                new_role = Role(name=role_name)
                session.add(new_role)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return new_role

    @classmethod
    async def delete_role(cls, role_id: int):
        async with async_session_maker() as session:
            async with session.begin():
                query = select(Role).filter_by(id=role_id)
                result = await session.execute(query)
                role = result.scalar_one_or_none()

                if not role:
                    raise ValueError("Роль не найдена!")

                # Удаление роли
                await session.delete(role)
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise e
                return {"message": "Роль удалена!"}

    @classmethod
    async def assign_role_to_user(cls, user_id: int, role_name: str):
        async with async_session_maker() as session:
            async with session.begin():
                # Загружаем пользователя и его роли с использованием selectinload для жадной загрузки ролей
                query = select(User).options(selectinload(User.roles)).filter_by(id=user_id)
                result = await session.execute(query)
                user = result.scalar_one_or_none()

                if not user:
                    raise ValueError(f"Пользователь с id={user_id} не найден!")

                # Удаляем старые роли пользователя
                for user_role in user.roles:
                    session.delete(user_role)  # Удаляем каждый элемент в таблице связи

                # Находим нужную роль
                query_role = select(Role).filter_by(name=role_name)
                result_role = await session.execute(query_role)
                role = result_role.scalar_one_or_none()

                if not role:
                    raise ValueError(f"Роль с именем '{role_name}' не найдена!")

                # Проверяем, не назначена ли уже эта роль пользователю
                if any(r.role.name == role_name for r in user.roles):  # Правильная проверка
                    raise ValueError(f"Пользователь уже имеет роль '{role_name}'.")

                # Создаем запись в таблице связи между пользователем и ролью
                user_role = UserRoles(user_id=user.id, role_id=role.id)
                session.add(user_role)

                # Фиксируем изменения в базе данных
                try:
                    await session.commit()
                except SQLAlchemyError as e:
                    await session.rollback()
                    raise ValueError(f"Ошибка при присвоении роли: {e}")

                return {"message": f"Роль '{role_name}' успешно присвоена пользователю с id={user_id}"}

    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).options(joinedload(cls.model.roles))

            if filter_by:
                query = query.filter_by(**filter_by)

            result = await session.execute(query)
            result = result.unique()  # Убираем дублирующиеся строки
            users = result.scalars().all()
            return users

