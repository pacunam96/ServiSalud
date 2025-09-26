# 🏥 SaludService - Sistema de Gestión de Salud

Sistema web desarrollado en Python con Streamlit que permite gestionar bases de datos de salud de Colombia, incluyendo análisis de disponibilidad de servicios, predicción de demanda y visualización para la comunidad.

## 🚀 Características

- **Autenticación segura** con roles de usuario
- **6 bases de datos de salud** de Colombia (datos.gov.co)
- **Análisis de disponibilidad** de servicios de salud
- **Predicción de demanda** con análisis temporal y estacional
- **Dashboard comunitario** con información para jornadas de salud
- **Visualizaciones interactivas** con Plotly
- **Exportación de datos** en formato CSV

## 📋 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git

## 🛠️ Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/SaludService.git
cd SaludService
```

### 2. Crear entorno virtual

```bash
# Crear entorno virtual
python -m venv env

# Activar entorno virtual
# En Windows:
env\Scripts\activate

# En macOS/Linux:
source env/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación estará disponible en: `http://localhost:8501`

### 5. Acceder con credenciales de prueba

Una vez que la aplicación esté ejecutándose:
1. Ve a `http://localhost:8501`
2. Usa las credenciales de prueba:
   - **Usuario:** `admin`
   - **Contraseña:** `1234`
3. ¡Explora todas las funcionalidades!

## 🔐 Credenciales de Acceso

### 👤 Usuario de Prueba (Recomendado para empezar)
```
Usuario: admin
Contraseña: 1234
```

**¡Usa estas credenciales para probar la aplicación inmediatamente!**

### 📝 Registro de Nuevos Usuarios
- **Usuario:** Tu email (de dominio permitido: gmail.com, hotmail.com)
- **Contraseña:** Debe cumplir estos requisitos:
  - Entre 8 y 20 caracteres
  - Al menos 1 minúscula
  - Al menos 1 mayúscula
  - Al menos 1 número
  - Al menos 1 caracter especial (@$!%*?&)

**Ejemplo de contraseña válida:** `Abcd@1234`

## 📊 Bases de Datos Disponibles

El sistema incluye 6 bases de datos de salud de Colombia:

1. **Dataset de Salud 1** (`i3fe-nzem`)
2. **Dataset de Salud 2** (`fm7q-3ytn`)
3. **Dataset de Salud 3** (`y42m-qq7z`)
4. **Dataset de Salud 4** (`f4c7-t4am`)
5. **Dataset de Salud 5** (`tz38-fg9k`)
6. **Dataset de Salud 6** (`x395-2tbn`)

## 🎯 Funcionalidades

### 📊 Gestión de Datos
- Carga de bases de datos desde datos.gov.co
- Visualización de datos en tablas interactivas
- Búsqueda y filtrado de información
- Exportación a CSV

### 🏥 Disponibilidad de Servicios
- Mapeo geográfico de servicios de salud
- Análisis de distribución por ubicación
- Clasificación por tipos de servicios
- Métricas de disponibilidad

### 📈 Predicción de Demanda
- Análisis temporal de consultas
- Predicción con promedio móvil
- Análisis estacional
- Identificación de patrones de demanda

### 👥 Dashboard Comunitario
- Información para jornadas de salud
- Estimación de recursos necesarios
- Calendario de actividades
- Información de contacto

## 🛠️ Estructura del Proyecto

```
SaludService/
├── app.py                 # Aplicación principal
├── requirements.txt       # Dependencias
├── README.md             # Este archivo
└── env/                  # Entorno virtual (no incluir en git)
```

## 📦 Dependencias

- `streamlit` - Framework web
- `streamlit-authenticator` - Autenticación
- `pandas` - Manipulación de datos
- `sodapy` - Cliente para APIs de Socrata
- `plotly` - Visualizaciones interactivas
- `requests` - Peticiones HTTP
- `numpy` - Cálculos numéricos

## 🚀 Despliegue

### Despliegue Local
```bash
streamlit run app.py
```

### Despliegue en la Nube
Para desplegar en plataformas como Heroku, Railway, o Streamlit Cloud:

1. Crear archivo `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

2. Configurar variables de entorno si es necesario

### 🎯 Acceso Rápido
**Para probar inmediatamente después del despliegue:**
- Usuario: `admin`
- Contraseña: `1234`

## 🤝 Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📝 Notas de Desarrollo

- El sistema usa `streamlit-authenticator` para la autenticación
- Los datos se obtienen de la API de datos.gov.co usando Socrata
- Las visualizaciones se generan con Plotly
- El sistema es compatible con Python 3.8+

## 🐛 Solución de Problemas

### Error de puerto ocupado
```bash
# En macOS, deshabilitar AirPlay Receiver
# System Preferences > General > AirDrop & Handoff
```

### Error de dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Error de autenticación
- Verificar que las credenciales cumplan los requisitos
- Usar el usuario preconfigurado: admin/1234

## 📞 Soporte

Para reportar bugs o solicitar features, crear un issue en el repositorio.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

**Desarrollado con ❤️ para mejorar el acceso a la información de salud en Colombia**
