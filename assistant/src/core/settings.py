from pydantic_settings import BaseSettings, SettingsConfigDict


class ElasticsearchSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="ELASTIC_")
    url: str = ""

    @property
    def host(self) -> str:
        return self.url.split(":")[0]

    @property
    def port(self) -> int:
        return int(self.url.split(":")[1])
