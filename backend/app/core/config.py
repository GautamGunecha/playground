from functools import lru_cache
from typing import Literal, Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_MAX_SAFE_PAYLOAD_BYTES = 90_000

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PLAYGROUND_", env_file=".env", extra="ignore")

    env: Literal["dev", "test", "prod"] = "dev"
    log_level: str = "INFO"

    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "postgresql+asyncpg://playground:playground@localhost:5432/playground"

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])
    rate_limit_per_minute: int = 30
    max_queue_depth: int = 500

    max_source_bytes: int = 64 * 1024
    max_stdin_bytes: int = 64 * 1024

    stream_name: str = "executions:stream"
    consumer_group: str = "workers"
    execution_result_ttl_s: int = 3600

    worker_concurrency: int = 4
    worker_job_timeout_s: float = 50.0
    worker_visibility_timeout_ms: int = 60_000
    worker_max_deliveries: int = 3
    max_output_bytes: int = 64 * 1024
    sandbox_runtime: str | None = None

    @model_validator(mode="after")
    def _check_invariants(self) -> Self:
        if self.worker_job_timeout_s * 1000 >= self.worker_visibility_timeout_ms:
            raise ValueError(
                "worker_job_timeout_s must be shorter than worker_visibility_timeout_ms, "
                "otherwise jobs that are still running get reclaimed by other workers"
            )

        if max(self.max_source_bytes, self.max_stdin_bytes) > _MAX_SAFE_PAYLOAD_BYTES:
            raise ValueError(f"source/stdin limits must be <= {_MAX_SAFE_PAYLOAD_BYTES} bytes")
        
        return self

    @lru_cache
    def get_settings() -> Settings:
        return Settings()
