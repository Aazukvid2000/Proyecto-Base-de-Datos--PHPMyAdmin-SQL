# 🏪 Cafetería El Rincón Mexicano - Sistema SQL con MySQL

## 📋 Descripción General

Este proyecto implementa un **sistema completo de gestión para una cafetería mexicana** utilizando tecnologías SQL relacionales tradicionales. El sistema permite gestionar productos, postres, categorías y realizar búsquedas avanzadas con **relaciones entre tablas**, todo desarrollado con **FastAPI**, **MySQL** y **Docker**.

### 🎯 Objetivo Académico
Demostrar el uso de bases de datos relacionales (MySQL) implementando características como:
- Relaciones entre tablas con Foreign Keys
- Consultas JOIN para datos relacionados
- Relaciones muchos a muchos con tablas intermedias
- API REST moderna con documentación automática
- ORM con SQLAlchemy para mapeo objeto-relacional
- Containerización con Docker

---

## 🗂️ Estructura del Proyecto

```
CARAMELITOAPIMONGO/
├── 📄 buscador.html          # Interfaz web para búsquedas
├── 🐳 docker-compose.yml     # Orquestación de contenedores
├── 🐳 Dockerfile            # Configuración del contenedor Python
├── 🐍 main.py               # API FastAPI principal
├── 📦 requirements.txt      # Dependencias de Python
└── 📁 __pycache__/          # Cache de Python (auto-generado)
```

### 📁 Descripción de Archivos

| Archivo | Descripción | Función Principal |
|---------|-------------|-------------------|
| `buscador.html` | Interfaz web responsiva | Frontend para búsquedas en tiempo real |
| `docker-compose.yml` | Configuración Docker | Orquesta FastAPI, MySQL y PHPMyAdmin |
| `Dockerfile` | Imagen Python | Configuración del contenedor de la API |
| `main.py` | API Backend | Lógica de negocio, modelos SQLAlchemy y endpoints |
| `requirements.txt` | Dependencias Python | Especifica librerías SQL necesarias |

---

## 🚀 Instalación y Configuración

### Prerrequisitos
- **Docker** y **Docker Compose** instalados
- **Puerto 8000** (API), **3307** (MySQL), **8080** (PHPMyAdmin) disponibles

### 🛠️ Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd CARAMELITOAPIMONGO
   ```

2. **Levantar los servicios**
   ```bash
   docker-compose up --build -d
   ```

3. **Verificar que todo funcione**
   ```bash
   # Esperar 15-20 segundos para que MySQL inicialice
   curl http://localhost:8000/productos/
   ```

### 🔄 Reinicialización Completa
```bash
docker-compose down -v  # Borra datos
docker-compose up --build -d
```

---

## 🌐 Servicios y Puertos

| Servicio | URL | Puerto | Credenciales |
|----------|-----|--------|--------------|
| **API REST** | http://localhost:8000 | 8000 | - |
| **Documentación API** | http://localhost:8000/docs | 8000 | - |
| **Buscador Web** | http://localhost:8000/buscador | 8000 | - |
| **MySQL** | localhost:3307 | 3307 | user/password |
| **PHPMyAdmin** | http://localhost:8080 | 8080 | user/password |

---

## 📊 Estructura de la Base de Datos SQL

### 🏗️ Tablas y Relaciones

#### 1. **categorias** - Tabla principal de categorías
```sql
CREATE TABLE categorias (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT
);
```

#### 2. **productos** - Productos de la cafetería
```sql
CREATE TABLE productos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    categoria_id INT,
    descripcion TEXT,
    precio DECIMAL(10,2),
    disponible INT DEFAULT 1,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);
```

#### 3. **postres** - Postres por rebanadas
```sql
CREATE TABLE postres (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    categoria_id INT,
    rebanadas INT,
    precio_rebanada DECIMAL(10,2),
    precio_total DECIMAL(10,2),
    disponible INT DEFAULT 1,
    FOREIGN KEY (categoria_id) REFERENCES categorias(id)
);
```

#### 4. **productos_postres** - Tabla intermedia (Muchos a Muchos)
```sql
CREATE TABLE productos_postres (
    producto_id INT,
    postre_id INT,
    PRIMARY KEY (producto_id, postre_id),
    FOREIGN KEY (producto_id) REFERENCES productos(id),
    FOREIGN KEY (postre_id) REFERENCES postres(id)
);
```

### 🔗 **Relaciones Implementadas**

#### **Uno a Muchos**
- `categorias` → `productos` (Una categoría tiene muchos productos)
- `categorias` → `postres` (Una categoría tiene muchos postres)

#### **Muchos a Muchos**
- `productos` ↔ `postres` (Productos relacionados con postres vía tabla intermedia)

---

## 🔌 API Endpoints

### 📍 Endpoints Principales

#### **Información General**
- `GET /` - Información de la API
- `GET /buscador` - Página web del buscador

#### **🏷️ Categorías**
- `GET /categorias/` - Listar todas las categorías
- `POST /categorias/` - Crear nueva categoría

#### **🌮 Productos**
- `GET /productos/` - Listar productos (paginado)
- `GET /productos/{id}` - Obtener producto específico
- `GET /productos/categoria/{categoria_id}` - Productos por categoría
- `GET /productos/{id}/postres` - **Postres relacionados** con el producto
- `POST /productos/` - Crear producto (con relaciones)
- `PUT /productos/{id}` - Actualizar producto
- `DELETE /productos/{id}` - Eliminar producto

#### **🍰 Postres**
- `GET /postres/` - Listar postres (paginado)
- `GET /postres/{id}` - Obtener postre específico
- `GET /postres/categoria/{categoria_id}` - Postres por categoría
- `GET /postres/{id}/productos` - **Productos relacionados** con el postre
- `POST /postres/` - Crear postre (con relaciones)
- `PUT /postres/{id}` - Actualizar postre
- `DELETE /postres/{id}` - Eliminar postre

#### **🔍 Búsquedas**
- `GET /buscar/{termino}` - Búsqueda global con JOINs

### 📝 Ejemplos de Uso

#### Buscar productos con "taco"
```bash
curl http://localhost:8000/buscar/taco
```

#### Crear producto con relaciones
```bash
curl -X POST http://localhost:8000/productos/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Taco de Carnitas",
    "categoria_id": 4,
    "descripcion": "Taco con carne de cerdo",
    "precio": 22.0,
    "disponible": 1,
    "postres_ids": [1, 2]
  }'
```

#### Obtener postres relacionados con un producto
```bash
curl http://localhost:8000/productos/1/postres
```

---

## 💻 Tecnologías Utilizadas

### **Backend**
- **FastAPI** 0.104.1 - Framework web moderno y rápido
- **SQLAlchemy** 2.0.23 - ORM para bases de datos relacionales
- **PyMySQL** 1.1.0 - Driver de MySQL para Python
- **Pydantic** 2.5.0 - Validación de datos
- **Uvicorn** 0.23.2 - Servidor ASGI

### **Base de Datos**
- **MySQL** 8.0 - Base de datos relacional
- **PHPMyAdmin** - Interfaz web para administrar MySQL

### **DevOps**
- **Docker** & **Docker Compose** - Containerización
- **CORS** - Configurado para desarrollo

### **Frontend**
- **HTML5** con CSS3 moderno
- **JavaScript** (Vanilla) para interactividad
- **Responsive Design** - Compatible con móviles

---

## ✨ Características Técnicas Destacadas

### 🔢 **Auto-incremento Nativo MySQL**
- IDs auto-incrementales nativos de MySQL
- Secuencias automáticas (1, 2, 3...) sin configuración adicional
- Integridad referencial garantizada por la base de datos

### 🔗 **Relaciones SQL Tradicionales**
- **Foreign Keys** para integridad referencial
- **Relaciones uno a muchos** con SQLAlchemy relationships
- **Relaciones muchos a muchos** con tabla intermedia
- **JOINs automáticos** para consultas relacionadas

### 🔍 **Búsqueda con JOINs**
- Búsquedas que incluyen datos de tablas relacionadas
- Consultas optimizadas con JOINs SQL
- Búsqueda en categorías mediante relaciones

### 🛡️ **Validaciones y Constraints**
- Validaciones a nivel de base de datos (NOT NULL, UNIQUE)
- Validaciones de API con Pydantic
- Foreign Key constraints para integridad
- Transacciones ACID automáticas

### 📱 **ORM con SQLAlchemy**
- Mapeo objeto-relacional automático
- Lazy loading de relaciones
- Consultas SQL generadas automáticamente
- Migraciones automáticas de esquema

---

## 🧪 Datos de Prueba

El sistema incluye datos de ejemplo para testing:

### **Categorías** (9 categorías)
- torta, cuernito, quesadilla, taco, baguette, bebida, postre, pastel, postre_frio

### **Productos** (18 productos de ejemplo)
- Tortas: Jamón, Milanesa, Cubana
- Tacos: Pastor, Suadero, Barbacoa
- Quesadillas: Queso, Hongos, Tinga
- Bebidas: Café Americano, Horchata, Limonada
- Y más...

### **Postres** (8 postres de ejemplo)
- Pastel de Chocolate, Cheesecake de Fresa, Tres Leches
- Tarta de Manzana, Red Velvet, Tiramisú
- Y más...

### **Relaciones** (Datos relacionados)
- Rebanada de Pastel de Chocolate → Pastel de Chocolate (relación producto-postre)

---

## 🔧 Comandos Útiles

### **Verificar estado de servicios**
```bash
docker-compose ps
```

### **Ver logs en tiempo real**
```bash
docker-compose logs -f fastapi
docker-compose logs -f db
```

### **Conectar a MySQL directamente**
```bash
docker exec -it <container_name> mysql -u user -p
```

### **Acceder a PHPMyAdmin**
```
URL: http://localhost:8080
Usuario: user
Contraseña: password
```

### **Detener servicios**
```bash
docker-compose down
```

### **Limpiar volúmenes (CUIDADO: borra datos)**
```bash
docker-compose down -v
```

---

## 📈 Casos de Uso SQL

1. **Gestión Relacional**: CRUD con relaciones Foreign Key
2. **Consultas JOIN**: Búsquedas que cruzan múltiples tablas
3. **Integridad Referencial**: Constraints automáticos de la BD
4. **Relaciones Muchos a Muchos**: Productos relacionados con postres
5. **Transacciones ACID**: Consistencia automática de datos

---

## 🎓 Valor Académico SQL

Este proyecto demuestra:

### **Conceptos de Bases de Datos Relacionales**
- Normalización de datos (1NF, 2NF, 3NF)
- Relaciones entre tablas con Foreign Keys
- Consultas JOIN (INNER, LEFT, RIGHT)
- Constraints y validaciones de BD

### **Comparación SQL vs. NoSQL**
- Auto-incremento nativo vs. simulado
- Relaciones FK vs. referencias por valor
- JOINs vs. agregaciones
- ACID vs. eventual consistency

### **ORM y Mapeo Objeto-Relacional**
- SQLAlchemy como abstracción de SQL
- Relationships y lazy loading
- Query building automático
- Migraciones de esquema

### **Arquitectura de Tres Capas**
- Capa de Presentación (HTML/JS)
- Capa de Lógica de Negocio (FastAPI)
- Capa de Datos (MySQL)

---

## 📊 Consultas SQL Ejemplares

### **Búsqueda con JOINs**
```sql
SELECT p.*, c.nombre as categoria_nombre 
FROM productos p 
JOIN categorias c ON p.categoria_id = c.id 
WHERE LOWER(p.nombre) LIKE '%taco%' 
   OR LOWER(c.nombre) LIKE '%taco%';
```

### **Relación Muchos a Muchos**
```sql
SELECT pos.* 
FROM postres pos
JOIN productos_postres pp ON pos.id = pp.postre_id
WHERE pp.producto_id = 1;
```

### **Agregaciones por Categoría**
```sql
SELECT c.nombre, COUNT(p.id) as total_productos
FROM categorias c
LEFT JOIN productos p ON c.id = p.categoria_id
GROUP BY c.id, c.nombre;
```

---

## 🏆 Resultados de Aprendizaje Alcanzados

### **Al finalizar este proyecto, se demuestra dominio en:**

1. **Fundamentos de SQL**: Comprensión profunda de MySQL y bases de datos relacionales

2. **Diseño Relacional**: Normalización, relaciones y integridad referencial

3. **ORM Avanzado**: Mapeo objeto-relacional con SQLAlchemy

4. **Consultas Complejas**: JOINs, subqueries y agregaciones SQL

5. **Arquitectura MVC**: Separación clara de responsabilidades

6. **Desarrollo Full-Stack**: Integración completa frontend-backend-database

---

## 📝 Comparación con Versión NoSQL

| Aspecto | **SQL (Esta versión)** | **NoSQL (MongoDB)** |
|---------|----------------------|-------------------|
| **Base de Datos** | MySQL 8.0 | MongoDB 7.0 |
| **Puerto API** | 8000 | 8090 |
| **ORM/ODM** | SQLAlchemy | Beanie |
| **Admin UI** | PHPMyAdmin | Mongo Express |
| **IDs** | Auto-increment nativo | Simulado con contadores |
| **Relaciones** | Foreign Keys + JOINs | Referencias + agregaciones |
| **Consultas** | SQL con JOINs | Queries de documentos |
| **Integridad** | Constraints de BD | Validaciones de aplicación |
| **Escalabilidad** | Vertical (tradicional) | Horizontal (distribuida) |

---

## 📞 Soporte y Documentación

- **Documentación API**: http://localhost:8000/docs (Swagger UI automático)
- **Redoc**: http://localhost:8000/redoc (Documentación alternativa)
- **PHPMyAdmin**: http://localhost:8080 (user/password)
- **MySQL Workbench**: Conectar a `localhost:3307` con user/password

---

## 📝 Notas Importantes

1. **Persistencia**: Los datos se mantienen en volúmenes Docker
2. **Seguridad**: Configurado para desarrollo, NO para producción
3. **Performance**: Optimizado con índices MySQL automáticos
4. **Compatibilidad**: Probado en Linux, macOS y Windows con Docker
5. **Transacciones**: ACID automático con MySQL

---

**Desarrollado por**: [Sinuhé Vidals Sibaja]  
**Universidad**: [Universidad Tenológica de la Mixteca]  
**Materia**: Base de Datos - Implementación SQL  
**Fecha**: [28 de Junio del 2025]

---

*Este proyecto demuestra la implementación práctica de sistemas relacionales SQL aplicados a casos de uso reales del sector alimentario, contrastando con enfoques NoSQL modernos.*