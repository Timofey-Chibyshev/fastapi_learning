from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class SUserBase(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    phone_number: str = Field(..., description="Номер телефона в международном формате, начинающийся с '+'")
    first_name: str = Field(..., min_length=3, max_length=50, description="Имя, от 3 до 50 символов")
    last_name: str = Field(..., min_length=3, max_length=50, description="Фамилия, от 3 до 50 символов")

    @field_validator("email")
    def validate_email(cls, value: str) -> str:
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", value):
            raise ValueError("Некорректный формат электронной почты. Проверьте адрес.")
        return value

    @field_validator("phone_number")
    def validate_phone_number(cls, value: str) -> str:
        if not re.match(r'^\+\d{5,15}$', value):
            raise ValueError(
                "Номер телефона должен начинаться с '+' и содержать от 5 до 15 цифр. Пример: +1234567890"
            )
        return value

    @field_validator("first_name", "last_name")
    def validate_name(cls, value: str) -> str:
        if not value.isalpha():
            raise ValueError("Имя и фамилия должны содержать только буквы.")
        if len(value) < 3 or len(value) > 50:
            raise ValueError("Имя и фамилия должны содержать от 3 до 50 символов.")
        return value


class SUserRegister(SUserBase):
    password: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 50 символов")

    @field_validator("password")
    def validate_password(cls, value: str) -> str:
        if len(value) < 5 or len(value) > 50:
            raise ValueError("Пароль должен содержать от 5 до 50 символов.")
        if not any(char.isdigit() for char in value):
            raise ValueError("Пароль должен содержать хотя бы одну цифру.")
        if not any(char.isalpha() for char in value):
            raise ValueError("Пароль должен содержать хотя бы одну букву.")
        if " " in value:
            raise ValueError("Пароль не должен содержать пробелов.")
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "Password123",
                "phone_number": "+79261234567",
                "first_name": "Иван",
                "last_name": "Иванов"
            }
        }


class SUserAuth(BaseModel):
    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")
