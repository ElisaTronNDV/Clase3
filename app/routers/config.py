from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import SystemConfig
from app.schemas import SystemConfigOut, SystemConfigUpdate

router = APIRouter(prefix="/config", tags=["config"], dependencies=[Depends(get_current_user)])


def _get_or_create_config(db: Session) -> SystemConfig:
    config = db.query(SystemConfig).first()
    if config is None:
        config = SystemConfig(tolerance_mm=1.0)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


@router.get("", response_model=SystemConfigOut)
def read_config(db: Session = Depends(get_db)):
    return _get_or_create_config(db)


@router.put("", response_model=SystemConfigOut)
def update_config(config_in: SystemConfigUpdate, db: Session = Depends(get_db)):
    config = _get_or_create_config(db)
    config.tolerance_mm = config_in.tolerance_mm
    db.commit()
    db.refresh(config)
    return config
