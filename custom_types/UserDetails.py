from dataclasses import dataclass, asdict, field
from typing import Optional


@dataclass
class APIKeys:
    openai_api_key: Optional[str] = None
    llama_api_key: Optional[str] = None


@dataclass
class UserDetails:
    _id: Optional[str] = None
    first_name: str = ""
    last_name: str = ""
    date_of_birth: str = ""
    email: str = ""
    company_name: Optional[str] = None
    job_title: str = ""
    hashed_password: str = ""
    personality: str = ""
    country: str = ""
    description: Optional[str] = None
    choosen_llm: str = ""
    api_keys: APIKeys = field(default_factory=lambda: APIKeys("", ""))
    created: str = ""
    last_update: str = ""
    reset_token: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

    def to_dict(self, include_doc_id: bool = False, include_tokens: bool = False):
        data = asdict(self)
        if not include_doc_id:
            data.pop('_id', None)

        if not include_tokens:
            data.pop('access_token', None)
            data.pop('reset_token', None)
            data.pop('refresh_token', None)

        return data
    
    def to_user_profile_dict(self) -> dict:
        excluded_fields = {'access_token', 'refresh_token', 'hashed_password', 'reset_token'}
        return {key: value for key, value in asdict(self).items() if key not in excluded_fields}


@dataclass
class UserProfile:
    _id:Optional[str] = None
    first_name: str = ""
    last_name: str = ""
    date_of_birth: str = ""
    email: str = ""
    job_title: str = ""
    country: str = ""
    personality: str = ""
    description: str = ""

    def to_dict(self) -> dict:
        return asdict(self)
