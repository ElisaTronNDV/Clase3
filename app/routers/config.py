from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.schemas import SystemConfigOut, SystemConfigUpdate
from app.system_config import get_or_create_system_config

router = APIRouter(prefix="/config", tags=["config"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=SystemConfigOut)
def read_config(db: Session = Depends(get_db)):
    return get_or_create_system_config(db)


@router.put("", response_model=SystemConfigOut)
def update_config(config_in: SystemConfigUpdate, db: Session = Depends(get_db)):
    config = get_or_create_system_config(db)
    config.tolerance_mm = config_in.tolerance_mm
    db.commit()
    db.refresh(config)
    return config
