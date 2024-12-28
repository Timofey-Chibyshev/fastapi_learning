from datetime import datetime, date
from typing import Optional
import re
from pydantic import BaseModel, Field, EmailStr, validator, ConfigDict, field_validator
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import date

from app.fields.schemas import SField


# class SField(BaseModel):
#     model_config = ConfigDict(from_attributes=True)
#     id: int
#     name: str = Field(..., min_length=1, max_length=100, description="Название поля, от 1 до 100 символов")
#     area_hectares: float = Field(..., gt=0, description="Площадь поля в гектарах, должна быть больше 0")
#     crop_rotation: Optional[str] = Field(None, max_length=100,
#                                          description="Информация о севообороте, не более 100 символов")
#     cultivation_technology: Optional[str] = Field(None, max_length=100,
#                                                   description="Технология возделывания, не более 100 символов")
#     coordinates: Optional[str] = Field(None, pattern=r'^\(\-?\d+(\.\d+)?,\s*\-?\d+(\.\d+)?\)$',
#                                        description="Координаты поля в формате (широта, долгота)")
#     farmer_id: int = Field(..., description="ID фермера, к которому относится поле")
#
#     @field_validator('area_hectares')
#     def validate_area_hectares(cls, value):
#         if value <= 0:
#             raise ValueError('Площадь поля должна быть больше 0')
#         return value
#
#     @field_validator('coordinates')
#     def validate_coordinates(cls, value):
#         if value and not re.match(r'^\(\-?\d+(\.\d+)?,\s*\-?\d+(\.\d+)?\)$', value):
#             raise ValueError('Координаты должны быть в формате (широта, долгота)')
#         return value


class SFarmer(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    phone_number: str = Field(..., unique=True, max_length=15,
                              description="Номер телефона в международном формате, начинающийся с '+'")
    first_name: str = Field(..., min_length=1, max_length=50, description="Имя фермера, от 1 до 50 символов")
    last_name: str = Field(..., min_length=1, max_length=50, description="Фамилия фермера, от 1 до 50 символов")
    date_of_birth: date = Field(..., description="Дата рождения фермера в формате ГГГГ-ММ-ДД")
    email: EmailStr = Field(..., description="Электронная почта фермера")
    address: str = Field(..., min_length=10, max_length=200, description="Адрес фермера, не более 200 символов")
    photo: Optional[str] = Field(None, max_length=100, description="Фото фермера")

    fields: List['SField'] = Field(default_factory=list, description="Список полей")  # Безопасный способ для инициализации списка

    # Валидация номера телефона
    @field_validator("phone_number", mode="before")
    @classmethod
    def validate_phone_number(cls, value):
        if not re.match(r'^\+\d{1,15}$', value):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 1 до 15 цифр')
        return value

    # Валидация даты рождения
    @field_validator("date_of_birth", mode="before")
    @classmethod
    def validate_date_of_birth(cls, value):
        if value >= date.today():
            raise ValueError('Дата рождения должна быть в прошлом')
        return value

    # Свойство для получения количества полей
    @property
    def number_of_fields(self) -> int:
        """Возвращает количество полей у фермера."""
        return len(self.fields)

    # Свойство для получения общей площади полей в гектарах
    @property
    def total_area_hectares(self) -> float:
        """Возвращает общую площадь всех полей в гектарах."""
        return sum(field.area_hectares for field in self.fields)


class SFarmerAdd(BaseModel):
    phone_number: str = Field(..., title="Номер телефона", max_length=20, description="Уникальный номер телефона фермера")
    first_name: str = Field(..., title="Имя", max_length=100, description="Имя фермера")
    last_name: str = Field(..., title="Фамилия", max_length=100, description="Фамилия фермера")
    farm_name: Optional[str] = Field(None, title="Название фермы", max_length=200, description="Название фермы фермера")
    date_of_birth: date = Field(..., title="Дата рождения", description="Дата рождения фермера")
    email: EmailStr = Field(..., title="Email", description="Электронная почта фермера")
    address: str = Field(..., title="Адрес", description="Адрес фермера")
    photo: Optional[str] = Field(None, title="Фото", description="URL фотографии фермера")

    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+79261234567",
                "first_name": "Иван",
                "last_name": "Иванов",
                "farm_name": "Ферма Иванова",
                "date_of_birth": "1980-05-10",
                "email": "ivan.ivanov@example.com",
                "address": "Тульская область, Россия",
                "photo": "https://example.com/photo.jpg"
            }
        }


class SFarmerUpdDesc(BaseModel):
    first_name: Optional[str] = Field(..., title="Имя", max_length=100, description="Имя фермера")
    last_name: Optional[str] = Field(..., title="Фамилия", max_length=100, description="Фамилия фермера")
    date_of_birth: Optional[date] = Field(..., title="Дата рождения", description="Дата рождения фермера")

    phone_number: Optional[str] = Field(None, title="Номер телефона", max_length=20, description="Новый номер телефона фермера")
    farm_name: Optional[str] = Field(None, title="Название фермы", max_length=200, description="Новое название фермы фермера")
    email: Optional[EmailStr] = Field(None, title="Email", description="Новая электронная почта фермера")
    address: Optional[str] = Field(None, title="Адрес", description="Новый адрес фермера")
    photo: Optional[str] = Field(None, title="Фото", description="Новый URL фотографии фермера")
    #Возможно лучше убрать возможность задавать новые имя, фамилию, дату рождения

    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+79261234567",
                "first_name": "Иван",
                "last_name": "Иванов",
                "farm_name": "Ферма Иванова",
                "date_of_birth": "1980-05-10",
                "email": "ivan.ivanov@example.com",
                "address": "Тульская область, Россия",
                "photo": "https://example.com/photo.jpg"
            }
        }
