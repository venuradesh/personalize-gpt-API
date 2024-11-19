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
    description: Optional[str] = None
    choosen_llm: Optional[str] = None
    api_keys: APIKeys = field(default_factory=lambda: APIKeys("", ""))
    created: Optional[str] = None
    last_update: Optional[str] = None

    def to_dict(self, include_doc_id: bool = False):
        data = asdict(self)
        if not include_doc_id:
            data.pop('_id', None)

        return data
