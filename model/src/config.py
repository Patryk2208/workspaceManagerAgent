import os
from dataclasses import dataclass, field

@dataclass
class ModelConfig:
    server_host: str = field(default_factory=lambda: os.getenv("SERVER_HOST", "localhost"))
    server_port: int = field(default_factory=lambda: int(os.getenv("SERVER_PORT", "8080")))

    max_windows: int = field(default_factory=lambda: int(os.getenv("MAX_WINDOWS", "20")))
    grid_rows: int = field(default_factory=lambda: int(os.getenv("GRID_ROWS", "6")))
    grid_cols: int = field(default_factory=lambda: int(os.getenv("GRID_COLS", "4")))

    poll_interval: float = field(default_factory=lambda: float(os.getenv("POLL_INTERVAL", "1.0")))
    request_timeout: float = field(default_factory=lambda: float(os.getenv("REQUEST_TIMEOUT", "5.0")))

    redis_host: str = field(default_factory=lambda: os.getenv("REDIS_HOST", "localhost"))
    redis_port: int = field(default_factory=lambda: int(os.getenv("REDIS_PORT", "6379")))
    redis_test_db: int = field(default_factory=lambda: int(os.getenv("REDIS_DB", "0")))
    redis_pre_training_db: int = field(default_factory=lambda: int(os.getenv("REDIS_DB", "1")))
    redis_prod_db: int = field(default_factory=lambda: int(os.getenv("REDIS_DB", "2")))

    # Derived properties
    @property
    def server_url(self) -> str:
        return f"https://{self.server_host}:{self.server_port}"

    @property
    def grid_size(self) -> int:
        return self.grid_rows * self.grid_cols


config = ModelConfig()
