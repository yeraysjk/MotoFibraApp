# backend/routes/piezas.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import PiezaBasica, PiezaDetalles
from pydantic import BaseModel
from fastapi import Form
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from typing import Optional, List
from fastapi import Query
from typing import Literal

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Clase para la creación de piezas básicas
class PiezaBasicaCreate(BaseModel):
    nombre: str
    marca: Literal[
        "Kawasaki", "Aprilia", "Yamaha", "Honda", "Suzuki",
        "Ducati", "Triumph"
    ]  # Marcas permitidas
    referencia: str
    cliente: Literal["MotoFibra", "S2Concept"]  # Clientes permitidos
    categoria: Literal[
        "guardabarros", "quillas", "depositos", "escopas",
        "frontal", "laterales", "colin"
    ]  # Categorías permitidas

    @classmethod
    def as_form(
        cls,
        nombre: str = Form(...),
        marca: str = Form(...),
        referencia: str = Form(...),
        cliente: str = Form(...),
        categoria: str = Form(...),
    ):
        return cls(nombre=nombre, marca=marca, referencia=referencia, cliente=cliente, categoria=categoria)

# Clase para los detalles de la pieza
class PiezaDetallesCreate(BaseModel):
    pieza_id: int
    tiempo_fabricacion: float
    tiempo_pintado: float
    tiempo_lijado: float
    tiempo_masillado: float
    costo: float
    gasto_resina: float


@router.get("/piezas", response_class=HTMLResponse)
def obtener_piezas(
    request: Request,
    filtro_nombre: Optional[str] = Query(None),
    filtro_marca: Optional[str] = Query(None),
    filtro_categoria: Optional[str] = Query(None),
    filtro_cliente: Optional[str] = Query(None),  # Filtro por cliente
    db: Session = Depends(get_db)
):
    # Query base
    query = db.query(PiezaBasica)

    # Aplicar filtros si están definidos
    if filtro_nombre:
        query = query.filter(PiezaBasica.nombre.ilike(f"%{filtro_nombre}%"))
    if filtro_marca:
        query = query.filter(PiezaBasica.marca == filtro_marca)
    if filtro_categoria:
        query = query.filter(PiezaBasica.categoria == filtro_categoria)
    if filtro_cliente:
        query = query.filter(PiezaBasica.cliente == filtro_cliente)  # Filtro por cliente

    piezas = query.all()

    return templates.TemplateResponse(
        "piezas.html",
        {"request": request, "piezas": piezas}
    )


# Ruta para crear una nueva pieza
@router.get("/piezas/nueva", response_class=HTMLResponse)
async def nueva_pieza(request: Request):
    return templates.TemplateResponse("nueva_pieza.html", {"request": request})

@router.post("/piezas/nueva")
def crear_pieza(
    nombre: str = Form(...),
    marca: str = Form(...),
    referencia: str = Form(...),
    cliente: str = Form(...),
    categoria: str = Form(...),
    tiempo_fabricacion: Optional[float] = Form(None),
    tiempo_pintado: Optional[float] = Form(None),
    costo: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    nueva_pieza = PiezaBasica(
        nombre=nombre,
        marca=marca,
        referencia=referencia,
        cliente=cliente,
        categoria=categoria
    )
    db.add(nueva_pieza)
    db.commit()
    db.refresh(nueva_pieza)

    if tiempo_fabricacion or tiempo_pintado or costo:
        detalles = PiezaDetalles(
            pieza_id=nueva_pieza.id,
            tiempo_fabricacion=tiempo_fabricacion,
            tiempo_pintado=tiempo_pintado,
            costo=costo
        )
        db.add(detalles)
        db.commit()

    return RedirectResponse(url="/piezas", status_code=303)


# Ruta para crear detalles de una pieza
@router.post("/piezas_detalles")
def crear_detalles_pieza(detalles: PiezaDetallesCreate, db: Session = Depends(get_db)):
    # Verificar si la pieza básica existe
    db_pieza = db.query(PiezaBasica).filter(PiezaBasica.id == detalles.pieza_id).first()
    if not db_pieza:
        raise HTTPException(status_code=404, detail="Pieza básica no encontrada")

    # Crear los detalles de la pieza
    db_detalles = PiezaDetalles(
        pieza_id=detalles.pieza_id,
        tiempo_fabricacion=detalles.tiempo_fabricacion,
        tiempo_pintado=detalles.tiempo_pintado,
        tiempo_lijado=detalles.tiempo_lijado,
        tiempo_masillado=detalles.tiempo_masillado,
        costo=detalles.costo,
        gasto_resina=detalles.gasto_resina
    )
    db.add(db_detalles)
    db.commit()
    db.refresh(db_detalles)

    return {"message": "Detalles de la pieza agregados correctamente"}


@router.post("/piezas/agregar_varias")
def agregar_varias_piezas(
        piezas: List[PiezaBasicaCreate], db: Session = Depends(get_db)
):
    piezas_db = []
    for pieza in piezas:
        pieza_db = PiezaBasica(
            nombre=pieza.nombre,
            marca=pieza.marca,
            referencia=pieza.referencia,
            cliente=pieza.cliente,
            categoria=pieza.categoria
        )
        piezas_db.append(pieza_db)

    # Agregar todas las piezas a la base de datos
    db.add_all(piezas_db)
    db.commit()

    # Retornar respuesta exitosa
    return {"message": "Piezas agregadas exitosamente", "piezas": piezas}


# Ruta para editar una pieza
@router.get("/piezas/{pieza_id}/editar", response_class=HTMLResponse)
async def editar_pieza(pieza_id: int, request: Request, db: Session = Depends(get_db)):
    pieza = db.query(PiezaBasica).filter(PiezaBasica.id == pieza_id).first()
    if pieza is None:
        raise HTTPException(status_code=404, detail="Pieza no encontrada")

    # Aquí deberías pasar la pieza y el objeto request a la plantilla
    return templates.TemplateResponse("editar_pieza.html", {"request": request, "pieza": pieza})

# Ruta POST para actualizar una pieza existente
@router.post("/piezas/{pieza_id}/editar", response_class=RedirectResponse)
async def actualizar_pieza(pieza_id: int, nombre: str = Form(...), marca: str = Form(...),
                           referencia: str = Form(...), db: Session = Depends(get_db)):
    pieza = db.query(PiezaBasica).filter(PiezaBasica.id == pieza_id).first()
    if pieza is None:
        raise HTTPException(status_code=404, detail="Pieza no encontrada")

    # Actualizar la pieza
    pieza.nombre = nombre
    pieza.marca = marca
    pieza.referencia = referencia
    db.commit()
    db.refresh(pieza)

    # Redirigir después de la actualización
    return RedirectResponse(url=f"/piezas/{pieza_id}", status_code=303)
