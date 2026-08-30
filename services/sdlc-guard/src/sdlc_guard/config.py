from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = "SDLC-Guard"
    openai_api_key: str = ""
    openai_model: str = "gpt-5-mini"
    ragflow_base_url: str = "http://ragflow.ragflow.svc.cluster.local"
    ragflow_api_key: str = ""
    ragflow_dataset_name: str = "sdlc-guard-ecommerce-demo"
    ragflow_dataset_id: str = ""
    ragflow_required: bool = False
    database_url: str = "postgresql+psycopg://sdlcguard:sdlcguard@traceability-postgres:5432/sdlcguard"
    retrieval_size: int = 12
    similarity_threshold: float = 0.15
    vector_similarity_weight: float = 0.35


@lru_cache

def get_settings() -> Settings:
    return Settings()
