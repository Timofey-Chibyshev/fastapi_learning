from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Optional
import re


class SFieldBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название поля, от 1 до 100 символов")
    area_hectares: float = Field(..., gt=0, description="Площадь поля в гектарах, должна быть больше 0")
    crop_rotation: Optional[str] = Field(None, max_length=100, description="Информация о севообороте, не более 100 символов")
    cultivation_technology: Optional[str] = Field(None, max_length=100, description="Технология возделывания, не более 100 символов")
    coordinates: Optional[str] = Field(..., description="Координаты поля в формате (широта, долгота)")
    farmer_id: int = Field(..., description="ID фермера, к которому относится поле")

    @field_validator('area_hectares')
    def validate_area_hectares(cls, value):
        if value <= 0:
            raise ValueError('Площадь поля должна быть больше 0')
        return value

    @field_validator('coordinates')
    def validate_coordinates(cls, value):
        if value and not re.match(r'^\(\-?\d+(\.\d+)?,\s*\-?\d+(\.\d+)?\)$', value):
            raise ValueError('Координаты должны быть в формате (широта, долгота)')
        return value


class SField(SFieldBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class SFieldAdd(SFieldBase):
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Поле А",
                "area_hectares": 10.5,
                "crop_rotation": "Пшеница - Горох - Рапс",
                "cultivation_technology": "No-till обработка",
                "coordinates": '[{"lat": 54.123, "lon": 37.456}, {"lat": 54.124, "lon": 37.457}]',
                "farmer_id": 1
            }
        }


class SFieldUpdDesc(SFieldBase):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Название поля, от 1 до 100 символов")
    area_hectares: Optional[float] = Field(None, gt=0, description="Площадь поля в гектарах, должна быть больше 0")
    crop_rotation: Optional[str] = Field(None, max_length=100, description="Информация о севообороте, не более 100 символов")
    cultivation_technology: Optional[str] = Field(None, max_length=100, description="Технология возделывания, не более 100 символов")
    coordinates: Optional[str] = Field(..., description="Координаты поля в формате (широта, долгота)")
    farmer_id: Optional[int] = Field(None, description="ID фермера, к которому относится поле")
