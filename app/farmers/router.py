from fastapi import APIRouter, Depends, HTTPException
from app.farmers.dao import FarmerDAO
from app.farmers.rb import RBFarmer
from app.farmers.schemas import SFarmer, SFarmerAdd, SFarmerUpdDesc
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix='/farmers', tags=['Работа с фермерами'])


@router.get("/", summary="Получить всех фермеров")
async def get_all_farmers(request_body: RBFarmer = Depends()) -> list[SFarmer]:
    return await FarmerDAO.find_all(**request_body.to_dict())


@router.get("/{id}", summary="Получить одного фермера по id")
async def get_farmer_by_id(farmer_id: int) -> SFarmer | dict:
    rez = await FarmerDAO.find_full_data(farmer_id)
    if rez is None:
        return {'message': f'Farmer с ID {farmer_id} не найден!'}
    return rez


@router.get("/by_filter", summary="Получить одного фермера по фильтру")
async def get_farmer_by_filter(request_body: RBFarmer = Depends()) -> SFarmer | dict:
    rez = await FarmerDAO.find_one_or_none(**request_body.to_dict())
    if rez is None:
        return {'message': f'Фермер с указанными вами параметрами не найден!'}
    return rez


@router.post("/add/", summary="Добавить фермера")
async def register_farmer(farmer: SFarmerAdd) -> dict:
    try:
        # Пытаемся добавить фермера
        check = await FarmerDAO.add(**farmer.dict())
        return {"message": "Фермер успешно добавлен!", "farmer": farmer}
    except IntegrityError as e:
        # Проверяем на ошибку уникальности email
        if "farmers_email_key" in str(e.orig):
            raise HTTPException(
                status_code=400,
                detail="Этот email уже используется. Пожалуйста, введите другой."
            )
        raise HTTPException(status_code=500, detail="Ошибка базы данных.")
    except Exception as e:
        # Общая обработка ошибок
        raise HTTPException(status_code=500, detail="Непредвиденная ошибка сервера.")


@router.put("/update_description/", summary='Обновить информацию о фермере')
async def update_farmer_description(farmer: SFarmerUpdDesc) -> dict:
    # check = await FarmerDAO.update(filter_by={'first_name': farmer.first_name,
    #                                           'second_name': farmer.second_name,
    #                                           'date_of_birth': farmer.date_of_birth},
    #                                major_description={'phone_number': farmer.phone_number,
    #                                                   'farm_name': farmer.farm_name,
    #                                                   'email': farmer.email,
    #                                                   'address': farmer.address,
    #                                                   'photo': farmer.photo})
    update_data = {}
    if farmer.phone_number:
        update_data['phone_number'] = farmer.phone_number
    if farmer.farm_name:
        update_data['farm_name'] = farmer.farm_name
    if farmer.email:
        update_data['email'] = farmer.email
    if farmer.address:
        update_data['address'] = farmer.address
    if farmer.photo:
        update_data['photo'] = farmer.photo

    check = await FarmerDAO.update(filter_by={
        'first_name': farmer.first_name,
        'last_name': farmer.last_name,
        'date_of_birth': farmer.date_of_birth
    }, **update_data)
    if check:
        return {"message": "Описание фермера успешно обновлено!", "farmer": farmer}
    else:
        return {"message": "Ошибка при обновлении описания фермера!"}


@router.delete("/delete/{farmer_id}", summary='Удалить информацию о фермере')
async def delete_farmer(farmer_id: int) -> dict:
    check = await FarmerDAO.delete(id=farmer_id)
    if check:
        return {"message": f"Фермер с ID {farmer_id} удален!"}
    else:
        return {"message": "Ошибка при удалении фермера!"}
