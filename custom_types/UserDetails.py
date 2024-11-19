from dataclasses import dataclass, asdict, field
from typing import Optional


@dataclass
class APIKeys:
    openai_api_key: Optional[str] = None
    llama_api_key: Optional[str] = None


@dataclass
class UserDetails:
    first_name: str = ""
    last_name: str = ""
    date_of_birth: str = ""
    email: str = ""
    company_name: Optional[str] = None
    job_title: str = ""
    hashed_password: str = ""
    personality: str = ""
    description: Optional[str] = None
    choosen_llm: Optional[str] = None
    api_keys: APIKeys = field(default_factory=lambda: APIKeys("", ""))
    created: Optional[str] = None
    last_update: Optional[str] = None

    def to_dict(self):
        return asdict(self)
