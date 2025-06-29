from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, ForeignKey, Table, or_, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from typing import List, Optional
import enum
import os

# Configuración de la base de datos
DATABASE_URL = "mysql+pymysql://user:password@db:3306/fastapi_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Tabla intermedia para la relación muchos a muchos entre productos y postres
productos_postres = Table(
    'productos_postres',
    Base.metadata,
    Column('producto_id', Integer, ForeignKey('productos.id'), primary_key=True),
    Column('postre_id', Integer, ForeignKey('postres.id'), primary_key=True)
)

# Modelo de Categorías
class Categoria(Base):
    __tablename__ = "categorias"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, index=True)
    descripcion = Column(Text)
    
    # Relaciones
    productos = relationship("Producto", back_populates="categoria_rel")
    postres = relationship("Postre", back_populates="categoria_rel")

# Modelo de la base de datos - Productos
class Producto(Base):
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    descripcion = Column(Text)
    precio = Column(Float)
    disponible = Column(Integer, default=1)
    
    # Relación con categoría
    categoria_rel = relationship("Categoria", back_populates="productos")
    
    # Relación muchos a muchos con postres
    postres_relacionados = relationship("Postre", secondary=productos_postres, back_populates="productos_relacionados")

# Modelo de la base de datos - Postres
class Postre(Base):
    __tablename__ = "postres"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True)
    descripcion = Column(Text)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    rebanadas = Column(Integer)
    precio_rebanada = Column(Float)
    precio_total = Column(Float)
    disponible = Column(Integer, default=1)
    
    # Relación con categoría
    categoria_rel = relationship("Categoria", back_populates="postres")
    
    # Relación muchos a muchos con productos
    productos_relacionados = relationship("Producto", secondary=productos_postres, back_populates="postres_relacionados")

# Esquemas Pydantic para Categorías
class CategoriaBase(BaseModel):
    nombre: str
    descripcion: str

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaResponse(CategoriaBase):
    id: int
    
    class Config:
        orm_mode = True

# Esquemas Pydantic para Productos
class ProductoBase(BaseModel):
    nombre: str
    categoria_id: int
    descripcion: str
    precio: float
    disponible: Optional[int] = 1

class ProductoCreate(ProductoBase):
    postres_ids: Optional[List[int]] = []

class ProductoResponse(BaseModel):
    id: int
    nombre: str
    categoria_id: int
    descripcion: str
    precio: float
    disponible: int
    categoria_rel: Optional[CategoriaResponse] = None
    
    class Config:
        orm_mode = True

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    categoria_id: Optional[int] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    disponible: Optional[int] = None
    postres_ids: Optional[List[int]] = None

# Esquemas Pydantic para Postres
class PostreBase(BaseModel):
    nombre: str
    descripcion: str
    categoria_id: int
    rebanadas: int
    precio_rebanada: float
    precio_total: float
    disponible: Optional[int] = 1

class PostreCreate(PostreBase):
    productos_ids: Optional[List[int]] = []

class PostreResponse(BaseModel):
    id: int
    nombre: str
    descripcion: str
    categoria_id: int
    rebanadas: int
    precio_rebanada: float
    precio_total: float
    disponible: int
    categoria_rel: Optional[CategoriaResponse] = None
    
    class Config:
        orm_mode = True

class PostreUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None
    rebanadas: Optional[int] = None
    precio_rebanada: Optional[float] = None
    precio_total: Optional[float] = None
    disponible: Optional[int] = None
    productos_ids: Optional[List[int]] = None

# Función para inicializar la base de datos con datos de ejemplo
def init_db():
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Crear categorías si no existen
        if db.query(Categoria).count() == 0:
            categorias = [
                Categoria(nombre="torta", descripcion="Tortas tradicionales mexicanas"),
                Categoria(nombre="cuernito", descripcion="Cuernitos y croissants horneados"),
                Categoria(nombre="quesadilla", descripcion="Quesadillas de tortilla de maíz"),
                Categoria(nombre="taco", descripcion="Tacos variados"),
                Categoria(nombre="baguette", descripcion="Baguettes gourmet"),
                Categoria(nombre="bebida", descripcion="Bebidas frías y calientes"),
                Categoria(nombre="postre", descripcion="Postres y dulces"),
                Categoria(nombre="pastel", descripcion="Pasteles completos y por rebanada"),
                Categoria(nombre="postre_frio", descripcion="Postres fríos y helados")
            ]
            for cat in categorias:
                db.add(cat)
            db.commit()
        
        # Obtener IDs de categorías
        cat_dict = {cat.nombre: cat.id for cat in db.query(Categoria).all()}
        
        # Verificar si ya existen productos para evitar duplicados
        if db.query(Producto).count() == 0:
            productos_iniciales = [
                # Tortas
                Producto(
                    nombre="Torta de Jamón", 
                    categoria_id=cat_dict["torta"],
                    descripcion="Torta con jamón, queso, aguacate, jitomate y lechuga en pan telera", 
                    precio=45.0
                ),
                Producto(
                    nombre="Torta de Milanesa", 
                    categoria_id=cat_dict["torta"],
                    descripcion="Torta con milanesa de res empanizada, aguacate, jitomate, lechuga y frijoles", 
                    precio=60.0
                ),
                Producto(
                    nombre="Torta Cubana", 
                    categoria_id=cat_dict["torta"],
                    descripcion="Torta con jamón, queso, milanesa, salchicha, chorizo, huevo, aguacate y frijoles", 
                    precio=85.0
                ),
                
                # Cuernitos
                Producto(
                    nombre="Cuernito de Jamón y Queso", 
                    categoria_id=cat_dict["cuernito"],
                    descripcion="Croissant horneado relleno de jamón y queso gouda derretido", 
                    precio=38.0
                ),
                Producto(
                    nombre="Cuernito 3 Quesos", 
                    categoria_id=cat_dict["cuernito"],
                    descripcion="Croissant horneado relleno de queso manchego, gouda y philadelphia", 
                    precio=42.0
                ),
                
                # Quesadillas
                Producto(
                    nombre="Quesadilla de Queso", 
                    categoria_id=cat_dict["quesadilla"],
                    descripcion="Tortilla de maíz hecha a mano rellena de queso Oaxaca", 
                    precio=25.0
                ),
                Producto(
                    nombre="Quesadilla de Hongos", 
                    categoria_id=cat_dict["quesadilla"],
                    descripcion="Tortilla de maíz hecha a mano rellena de hongos guisados y queso", 
                    precio=30.0
                ),
                Producto(
                    nombre="Quesadilla de Tinga", 
                    categoria_id=cat_dict["quesadilla"],
                    descripcion="Tortilla de maíz hecha a mano rellena de tinga de pollo y queso", 
                    precio=35.0
                ),
                
                # Tacos
                Producto(
                    nombre="Taco de Pastor", 
                    categoria_id=cat_dict["taco"],
                    descripcion="Tortilla de maíz con carne de cerdo marinada en adobo y piña", 
                    precio=18.0
                ),
                Producto(
                    nombre="Taco de Suadero", 
                    categoria_id=cat_dict["taco"],
                    descripcion="Tortilla de maíz con carne de res suadero, cilantro y cebolla", 
                    precio=20.0
                ),
                Producto(
                    nombre="Taco de Barbacoa", 
                    categoria_id=cat_dict["taco"],
                    descripcion="Tortilla de maíz con carne de barbacoa de borrego, cilantro y cebolla", 
                    precio=25.0
                ),
                
                # Baguettes
                Producto(
                    nombre="Baguette Italiano", 
                    categoria_id=cat_dict["baguette"],
                    descripcion="Pan baguette con jamón serrano, queso provolone, tomate y pesto", 
                    precio=65.0
                ),
                Producto(
                    nombre="Baguette de Pollo", 
                    categoria_id=cat_dict["baguette"],
                    descripcion="Pan baguette con pollo a la plancha, queso manchego, lechuga y jitomate", 
                    precio=60.0
                ),
                
                # Bebidas
                Producto(
                    nombre="Café Americano", 
                    categoria_id=cat_dict["bebida"],
                    descripcion="Café de grano recién molido, 12 oz", 
                    precio=30.0
                ),
                Producto(
                    nombre="Agua de Horchata", 
                    categoria_id=cat_dict["bebida"],
                    descripcion="Agua fresca de arroz con canela y vainilla, 16 oz", 
                    precio=25.0
                ),
                Producto(
                    nombre="Limonada", 
                    categoria_id=cat_dict["bebida"],
                    descripcion="Limonada natural con un toque de menta, 16 oz", 
                    precio=28.0
                ),
                
                # Postres individuales en productos
                Producto(
                    nombre="Rebanada de Pastel de Chocolate", 
                    categoria_id=cat_dict["postre"],
                    descripcion="Rebanada individual de pastel de chocolate", 
                    precio=45.0
                ),
                Producto(
                    nombre="Flan Individual", 
                    categoria_id=cat_dict["postre"],
                    descripcion="Porción individual de flan napolitano", 
                    precio=35.0
                )
            ]
            
            for producto in productos_iniciales:
                db.add(producto)
            
            db.commit()
        
        # Verificar si ya existen postres para evitar duplicados
        if db.query(Postre).count() == 0:
            postres_iniciales = [
                Postre(
                    nombre="Pastel de Chocolate",
                    descripcion="Delicioso pastel de chocolate con ganache de chocolate oscuro y decorado con fresas",
                    categoria_id=cat_dict["pastel"],
                    rebanadas=12,
                    precio_rebanada=45.0,
                    precio_total=540.0
                ),
                Postre(
                    nombre="Cheesecake de Fresa",
                    descripcion="Tarta de queso cremosa con base de galleta y cobertura de fresas naturales",
                    categoria_id=cat_dict["pastel"],
                    rebanadas=10,
                    precio_rebanada=50.0,
                    precio_total=500.0
                ),
                Postre(
                    nombre="Pastel Tres Leches",
                    descripcion="Esponjoso pastel bañado en tres tipos de leche con crema chantilly y canela",
                    categoria_id=cat_dict["pastel"],
                    rebanadas=16,
                    precio_rebanada=35.0,
                    precio_total=560.0
                ),
                Postre(
                    nombre="Tarta de Manzana",
                    descripcion="Clásica tarta de manzana con masa crujiente y manzanas caramelizadas",
                    categoria_id=cat_dict["pastel"],
                    rebanadas=8,
                    precio_rebanada=40.0,
                    precio_total=320.0
                ),
                Postre(
                    nombre="Pastel de Zanahoria",
                    descripcion="Húmedo pastel de zanahoria con nueces y betún de queso crema",
                    categoria_id=cat_dict["pastel"],
                    rebanadas=12,
                    precio_rebanada=42.0,
                    precio_total=504.0
                ),
                Postre(
                    nombre="Tiramisú",
                    descripcion="Postre italiano con capas de bizcocho bañado en café, mascarpone y cacao",
                    categoria_id=cat_dict["postre_frio"],
                    rebanadas=9,
                    precio_rebanada=55.0,
                    precio_total=495.0
                ),
                Postre(
                    nombre="Pastel Red Velvet",
                    descripcion="Suave pastel de terciopelo rojo con betún de queso crema",
                    categoria_id=cat_dict["pastel"],
                    rebanadas=14,
                    precio_rebanada=48.0,
                    precio_total=672.0
                ),
                Postre(
                    nombre="Flan Napolitano Familiar",
                    descripcion="Flan casero de tamaño familiar con caramelo y vainilla",
                    categoria_id=cat_dict["postre_frio"],
                    rebanadas=10,
                    precio_rebanada=25.0,
                    precio_total=250.0
                )
            ]
            
            for postre in postres_iniciales:
                db.add(postre)
            
            db.commit()
            
            # Crear algunas relaciones entre productos y postres
            # Por ejemplo, relacionar las rebanadas individuales con los pasteles completos
            pastel_chocolate = db.query(Postre).filter(Postre.nombre == "Pastel de Chocolate").first()
            rebanada_chocolate = db.query(Producto).filter(Producto.nombre == "Rebanada de Pastel de Chocolate").first()
            
            if pastel_chocolate and rebanada_chocolate:
                pastel_chocolate.productos_relacionados.append(rebanada_chocolate)
                db.commit()
    
    except Exception as e:
        print(f"Error al inicializar la base de datos: {str(e)}")
        db.rollback()
    finally:
        db.close()

# Crear la app FastAPI
app = FastAPI(
    title="API Cafetería El Rincón Mexicano",
    description="API para gestionar los productos y postres de una cafetería/restaurante mexicano con relaciones entre tablas",
    version="3.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especifica los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Obtener la conexión a la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Inicializar la base de datos al iniciar la aplicación
@app.on_event("startup")
def startup():
    init_db()

# Endpoint raíz
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Cafetería El Rincón Mexicano - v3.0"}

# Endpoint para servir el buscador HTML
@app.get("/buscador")
async def get_buscador():
    """
    Sirve la página HTML del buscador
    """
    if os.path.exists("buscador.html"):
        return FileResponse("buscador.html")
    else:
        raise HTTPException(status_code=404, detail="Archivo buscador.html no encontrado")

# ==================== ENDPOINTS PARA CATEGORÍAS ====================

@app.get("/categorias/", response_model=List[CategoriaResponse], tags=["categorias"])
def listar_categorias(db: Session = Depends(get_db)):
    """
    Obtiene todas las categorías disponibles.
    """
    categorias = db.query(Categoria).all()
    return categorias

@app.post("/categorias/", response_model=CategoriaResponse, tags=["categorias"])
def crear_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    """
    Crea una nueva categoría.
    """
    db_categoria = Categoria(**categoria.dict())
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

# ==================== ENDPOINTS PARA PRODUCTOS ====================

@app.get("/productos/", response_model=List[ProductoResponse], tags=["productos"])
def listar_productos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtiene todos los productos disponibles en la cafetería.
    """
    productos = db.query(Producto).offset(skip).limit(limit).all()
    return productos

@app.get("/productos/{producto_id}", response_model=ProductoResponse, tags=["productos"])
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un producto específico por su ID.
    """
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@app.get("/productos/categoria/{categoria_id}", response_model=List[ProductoResponse], tags=["productos"])
def obtener_productos_por_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """
    Obtiene todos los productos de una categoría específica.
    """
    productos = db.query(Producto).filter(Producto.categoria_id == categoria_id).all()
    return productos

@app.get("/productos/{producto_id}/postres", response_model=List[PostreResponse], tags=["productos"])
def obtener_postres_relacionados(producto_id: int, db: Session = Depends(get_db)):
    """
    Obtiene todos los postres relacionados con un producto.
    """
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto.postres_relacionados

@app.post("/productos/", response_model=ProductoResponse, tags=["productos"])
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo producto en la base de datos.
    """
    # Verificar que la categoría existe
    categoria = db.query(Categoria).filter(Categoria.id == producto.categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Crear el producto sin las relaciones
    producto_data = producto.dict()
    postres_ids = producto_data.pop('postres_ids', [])
    
    db_producto = Producto(**producto_data)
    db.add(db_producto)
    db.commit()
    
    # Agregar relaciones con postres si se especificaron
    if postres_ids:
        for postre_id in postres_ids:
            postre = db.query(Postre).filter(Postre.id == postre_id).first()
            if postre:
                db_producto.postres_relacionados.append(postre)
        db.commit()
    
    db.refresh(db_producto)
    return db_producto

@app.put("/productos/{producto_id}", response_model=ProductoResponse, tags=["productos"])
def actualizar_producto(producto_id: int, producto: ProductoUpdate, db: Session = Depends(get_db)):
    """
    Actualiza un producto existente.
    """
    db_producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    update_data = producto.dict(exclude_unset=True)
    postres_ids = update_data.pop('postres_ids', None)
    
    # Verificar categoría si se está actualizando
    if 'categoria_id' in update_data:
        categoria = db.query(Categoria).filter(Categoria.id == update_data['categoria_id']).first()
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    for key, value in update_data.items():
        setattr(db_producto, key, value)
    
    # Actualizar relaciones con postres si se especificaron
    if postres_ids is not None:
        db_producto.postres_relacionados.clear()
        for postre_id in postres_ids:
            postre = db.query(Postre).filter(Postre.id == postre_id).first()
            if postre:
                db_producto.postres_relacionados.append(postre)
    
    db.commit()
    db.refresh(db_producto)
    return db_producto

@app.delete("/productos/{producto_id}", tags=["productos"])
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    """
    Elimina un producto de la base de datos.
    """
    db_producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if db_producto is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    db.delete(db_producto)
    db.commit()
    return {"message": f"Producto {db_producto.nombre} eliminado correctamente"}

# ==================== ENDPOINTS PARA POSTRES ====================

@app.get("/postres/", response_model=List[PostreResponse], tags=["postres"])
def listar_postres(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtiene todos los postres disponibles en la cafetería.
    """
    postres = db.query(Postre).offset(skip).limit(limit).all()
    return postres

@app.get("/postres/{postre_id}", response_model=PostreResponse, tags=["postres"])
def obtener_postre(postre_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un postre específico por su ID.
    """
    postre = db.query(Postre).filter(Postre.id == postre_id).first()
    if postre is None:
        raise HTTPException(status_code=404, detail="Postre no encontrado")
    return postre

@app.get("/postres/categoria/{categoria_id}", response_model=List[PostreResponse], tags=["postres"])
def obtener_postres_por_categoria(categoria_id: int, db: Session = Depends(get_db)):
    """
    Obtiene todos los postres de una categoría específica.
    """
    postres = db.query(Postre).filter(Postre.categoria_id == categoria_id).all()
    return postres

@app.get("/postres/{postre_id}/productos", response_model=List[ProductoResponse], tags=["postres"])
def obtener_productos_relacionados(postre_id: int, db: Session = Depends(get_db)):
    """
    Obtiene todos los productos relacionados con un postre.
    """
    postre = db.query(Postre).filter(Postre.id == postre_id).first()
    if postre is None:
        raise HTTPException(status_code=404, detail="Postre no encontrado")
    return postre.productos_relacionados

@app.post("/postres/", response_model=PostreResponse, tags=["postres"])
def crear_postre(postre: PostreCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo postre en la base de datos.
    """
    # Verificar que la categoría existe
    categoria = db.query(Categoria).filter(Categoria.id == postre.categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Crear el postre sin las relaciones
    postre_data = postre.dict()
    productos_ids = postre_data.pop('productos_ids', [])
    
    # Validar que el precio total sea coherente con precio por rebanada
    if postre_data['precio_total'] != (postre_data['rebanadas'] * postre_data['precio_rebanada']):
        postre_data['precio_total'] = postre_data['rebanadas'] * postre_data['precio_rebanada']
    
    db_postre = Postre(**postre_data)
    db.add(db_postre)
    db.commit()
    
    # Agregar relaciones con productos si se especificaron
    if productos_ids:
        for producto_id in productos_ids:
            producto = db.query(Producto).filter(Producto.id == producto_id).first()
            if producto:
                db_postre.productos_relacionados.append(producto)
        db.commit()
    
    db.refresh(db_postre)
    return db_postre

@app.put("/postres/{postre_id}", response_model=PostreResponse, tags=["postres"])
def actualizar_postre(postre_id: int, postre: PostreUpdate, db: Session = Depends(get_db)):
    """
    Actualiza un postre existente.
    """
    db_postre = db.query(Postre).filter(Postre.id == postre_id).first()
    if db_postre is None:
        raise HTTPException(status_code=404, detail="Postre no encontrado")
    
    update_data = postre.dict(exclude_unset=True)
    productos_ids = update_data.pop('productos_ids', None)
    
    # Verificar categoría si se está actualizando
    if 'categoria_id' in update_data:
        categoria = db.query(Categoria).filter(Categoria.id == update_data['categoria_id']).first()
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Si se actualizan rebanadas o precio_rebanada, recalcular precio_total
    if 'rebanadas' in update_data or 'precio_rebanada' in update_data:
        rebanadas = update_data.get('rebanadas', db_postre.rebanadas)
        precio_rebanada = update_data.get('precio_rebanada', db_postre.precio_rebanada)
        update_data['precio_total'] = rebanadas * precio_rebanada
    
    for key, value in update_data.items():
        setattr(db_postre, key, value)
    
    # Actualizar relaciones con productos si se especificaron
    if productos_ids is not None:
        db_postre.productos_relacionados.clear()
        for producto_id in productos_ids:
            producto = db.query(Producto).filter(Producto.id == producto_id).first()
            if producto:
                db_postre.productos_relacionados.append(producto)
    
    db.commit()
    db.refresh(db_postre)
    return db_postre

@app.delete("/postres/{postre_id}", tags=["postres"])
def eliminar_postre(postre_id: int, db: Session = Depends(get_db)):
    """
    Elimina un postre de la base de datos.
    """
    db_postre = db.query(Postre).filter(Postre.id == postre_id).first()
    if db_postre is None:
        raise HTTPException(status_code=404, detail="Postre no encontrado")
    
    db.delete(db_postre)
    db.commit()
    return {"message": f"Postre {db_postre.nombre} eliminado correctamente"}

# ==================== ENDPOINTS DE BÚSQUEDA ====================

@app.get("/buscar/{termino}", tags=["busqueda"])
def buscar_global(termino: str, db: Session = Depends(get_db)):
    """
    Busca un término en productos y postres (nombre, descripción y categoría).
    La búsqueda es case-insensitive.
    """
    # Convertir el término a minúsculas para búsqueda case-insensitive
    termino_lower = f"%{termino.lower()}%"
    
    # Buscar en productos
    productos = db.query(Producto).join(Categoria).filter(
        or_(
            func.lower(Producto.nombre).like(termino_lower),
            func.lower(Producto.descripcion).like(termino_lower),
            func.lower(Categoria.nombre).like(termino_lower),
            func.lower(Categoria.descripcion).like(termino_lower)
        )
    ).all()
    
    # Buscar en postres
    postres = db.query(Postre).join(Categoria).filter(
        or_(
            func.lower(Postre.nombre).like(termino_lower),
            func.lower(Postre.descripcion).like(termino_lower),
            func.lower(Categoria.nombre).like(termino_lower),
            func.lower(Categoria.descripcion).like(termino_lower)
        )
    ).all()
    
    # Formatear resultados
    resultados = {
        "termino_busqueda": termino,
        "productos": [
            {
                "tipo": "Producto",
                "id": p.id,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "categoria": p.categoria_rel.nombre if p.categoria_rel else "Sin categoría",
                "precio": f"${p.precio:.2f}",
                "disponible": "Sí" if p.disponible else "No"
            }
            for p in productos
        ],
        "postres": [
            {
                "tipo": "Postre",
                "id": p.id,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "categoria": p.categoria_rel.nombre if p.categoria_rel else "Sin categoría",
                "precio_rebanada": f"${p.precio_rebanada:.2f}",
                "precio_total": f"${p.precio_total:.2f}",
                "rebanadas": p.rebanadas,
                "disponible": "Sí" if p.disponible else "No"
            }
            for p in postres
        ],
        "total_resultados": len(productos) + len(postres)
    }
    
    return resultados

# Punto de entrada para ejecutar la aplicación con uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)