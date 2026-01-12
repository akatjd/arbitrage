from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # 거래소 API 키 (공개 API만 사용할 경우 선택사항)
    binance_api_key: Optional[str] = None
    binance_secret_key: Optional[str] = None
    upbit_access_key: Optional[str] = None
    upbit_secret_key: Optional[str] = None

    # 서버 설정
    host: str = "0.0.0.0"
    port: int = 8000

    # 업데이트 주기
    price_update_interval: float = 1.0

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
