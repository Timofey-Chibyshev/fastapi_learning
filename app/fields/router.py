from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.fields.dao import FieldsDAO
from app.fields.rb import RBField
from app.fields.schemas import SField, SFieldAdd, SFieldUpdDesc

router = APIRouter(prefix='/fields', tags=['Работа с полями'])


@router.get("/", summary="Получить все поля")
async def get_all_fields(
    request_body: RBField = Depends(),
    session: AsyncSession = Depends(get_db_session)
) -> list[SField]:
    return await FieldsDAO.find_fields(session, **request_body.to_dict())


@router.get("/{field_id}", summary="Получить одно поле по id")
async def get_field_by_id(
    field_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> SField | dict:
    rez = await FieldsDAO.find_full_data(session, field_id)
    if rez is None:
        return {'message': f'Поле с ID {field_id} не найдено!'}
    return rez


@router.get("/by_filter", summary="Получить одно поле по фильтру")
async def get_field_by_filter(
    request_body: RBField = Depends(),
    session: AsyncSession = Depends(get_db_session)
) -> SField | dict:
    rez = await FieldsDAO.find_one_or_none(session, **request_body.to_dict())
    if rez is None:
        return {'message': f'Поле с указанными вами параметрами не найдено!'}
    return rez


@router.post("/add/", summary='Добавить информацию поле')
async def register_field(
    field: SFieldAdd,
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    check = await FieldsDAO.add_field(session, field_data=field.dict())
    if check:
        return {"message": "Поле успешно добавлено!", "field": field}
    else:
        return {"message": "Ошибка при добавлении поля!"}


@router.delete("/delete/{field_id}", summary='Удалить информацию о поле')
async def dell_field_by_id(
    field_id: int,
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    check = await FieldsDAO.delete_field_by_id(session, field_id)
    if check:
        return {"message": f"Поле с ID {field_id} удалено!"}
    else:
        return {"message": "Ошибка при удалении поля!"}


@router.put("/update_description/", summary='Обновить информацию о поле')
async def update_field_description(
    field_id: int,
    field_data: SFieldUpdDesc,
    session: AsyncSession = Depends(get_db_session)
) -> dict:
    update_data = field_data.dict(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="Нет данных для обновления")

    check = await FieldsDAO.update_field(session, field_id, update_data)

    if "error" in check:
        raise HTTPException(status_code=404, detail=check["error"])

    return {"success": check["success"]}
