from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    neo4j_uri: str = Field(..., env="NEO4J_URI")
    neo4j_user: str = Field(..., env="NEO4J_USER")
    neo4j_password: str = Field(..., env="NEO4J_PASSWORD")
    redis_url: str = Field(..., env="REDIS_URL")
    
settings = Settings()