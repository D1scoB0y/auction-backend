from pydantic import BaseModel, ConfigDict, Field, field_validator

import src.user.validators as _auth_validators


class Username(BaseModel):
    username: str

    @field_validator('username')
    def special_symbols_checking(cls, value: str) -> str:
        return _auth_validators.validate_username(value)


class Email(BaseModel):
    email: str

    @field_validator('email')
    def email_validation(cls, value: str) -> str:
        return _auth_validators.validate_email(value)


class PhoneNumber(BaseModel):
    phone_number: str | None = Field(alias='phoneNumber')

    @field_validator('phone_number')
    def phone_validation(cls, value: str | None) -> str | None:
        return _auth_validators.validate_phone(value)


class Password(BaseModel):
    password: str

    @field_validator('password')
    def password_validation(cls, value: str) -> str:
        return _auth_validators.validate_password(value)


class LoginUser(BaseModel):
    email: str
    password: str


class RegistrationUser(Username, Email, Password):
    recaptcha_token: str = Field(default='', alias='recaptchaToken')


class UpdateUser(Username, Email, PhoneNumber):
    contacts: str | None


class ChangePassword(BaseModel):
    new_password: str = Field(min_length=8, max_length=64, alias='newPassword')
    current_password: str = Field(alias='currentPassword')


class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(alias='newPassword')


class LoginWithGoogle(BaseModel):
    token: str


class ReadUser(Username, Email, PhoneNumber):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: int = Field(alias='userId')
    email_is_verified: bool = Field(alias='emailIsVerified')
    phone_number_is_verified: bool = Field(alias='phoneNumberIsVerified')
    is_seller: bool = Field(alias='isSeller')
    created_via_google: bool = Field(alias='createdViaGoogle')
    contacts: str | None
