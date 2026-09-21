from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql://geocine:geocine@localhost:5432/geocine"
    cors_origins: str = "http://localhost:8000,http://127.0.0.1:8000"
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    map_default_lat: float = 53.9
    map_default_lon: float = 27.55
    map_default_zoom: int = 5

    @property
    def cors_origin_list(self) -> list[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


settings = Settings()
