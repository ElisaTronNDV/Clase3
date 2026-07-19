from sqlalchemy.orm import Session

from app.models import SystemConfig


def get_or_create_system_config(db: Session) -> SystemConfig:
    config = db.query(SystemConfig).first()
    if config is None:
        config = SystemConfig(tolerance_mm=1.0)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config
