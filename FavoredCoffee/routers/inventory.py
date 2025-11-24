from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlmodel import Session

from ..database import get_session
from ..security import get_current_warehouse_user # <-- Rol de Bodeguero
from ..schemas import InventoryUploadResponse
from ..logic.logic_inventory import process_inventory_file

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
    # Protegido para Bodegueros y Admins
    dependencies=[Depends(get_current_warehouse_user)] 
)

@router.post("/upload", response_model=InventoryUploadResponse)
async def upload_inventory_file(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Endpoint para carga masiva de inventario (CSV o Excel).
    """
    if not file:
        raise HTTPException(status_code=400, detail="No se envió ningún archivo")

    file_content = await file.read()
    
    result = process_inventory_file(
        db=session, 
        file_content=file_content, 
        file_type=file.content_type
    )
    
    return result