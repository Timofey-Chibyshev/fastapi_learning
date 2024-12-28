from fastapi import APIRouter, Depends, HTTPException
from app.fields.dao import FieldsDAO
from app.fields.rb import RBField
from app.fields.schemas import SField, SFieldAdd, SFieldUpdDesc

router = APIRouter(prefix='/fields', tags=['Работа с полями'])


@router.get("/", summary="Получить все поля")
async def get_all_fields(request_body: RBField = Depends()) -> list[SField]:
    return await FieldsDAO.find_fields(**request_body.to_dict())


@router.get("/{field_id}", summary="Получить одно поле по id")
async def get_field_by_id(field_id: int) -> SField | dict:
    rez = await FieldsDAO.find_full_data(field_id=field_id)
    if rez is None:
        return {'message': f'Поле с ID {field_id} не найдено!'}
    return rez


@router.get("/by_filter", summary="Получить одно поле по фильтру")
async def get_field_by_filter(request_body: RBField = Depends()) -> SField | dict:
    rez = await FieldsDAO.find_one_or_none(**request_body.to_dict())
    if rez is None:
        return {'message': f'Поле с указанными вами параметрами не найдено!'}
    return rez


@router.post("/add/", summary='Добавить информацию поле')
async def register_field(field: SFieldAdd) -> dict:
    check = await FieldsDAO.add_field(field_data=field.dict())
    if check:
        return {"message": "Поле успешно добавлено!", "field": field}
    else:
        return {"message": "Ошибка при добавлении поля!"}


@router.delete("/delete/{field_id}", summary='Удалить информацию о поле')
async def dell_field_by_id(field_id: int) -> dict:
    check = await FieldsDAO.delete_field_by_id(field_id=field_id)
    if check:
        return {"message": f"Поле с ID {field_id} удалено!"}
    else:
        return {"message": "Ошибка при удалении поля!"}


@router.put("/update_description/", summary='Обновить информацию о поле')
async def update_field_description(field_id: int, field_data: SFieldUpdDesc) -> dict:
    update_data = field_data.dict(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="Нет данных для обновления")

    check = await FieldsDAO.update_field(field_id, update_data)

    if "error" in check:
        raise HTTPException(status_code=404, detail=check["error"])

    return {"success": check["success"]}
