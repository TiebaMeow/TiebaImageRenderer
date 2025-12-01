from pydantic import BaseModel

import tomllib


class Config(BaseModel):
    host: str = "localhost"
    port: int = 39334
    key: str = ""


def load_config(path: str) -> Config:
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return Config(**data)
    except FileNotFoundError:
        # Return default config if file is missing
        return Config()


config = load_config("config.toml")