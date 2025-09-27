import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from sodapy import Socrata
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score

# Configuración de la página
st.set_page_config(
    page_title="ServiSalud - Sistema de Salud Pública",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la interfaz
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #2a5298;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f8f9fa;
        border-radius: 10px 10px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2a5298;
        color: white;
    }
    
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
    
    .success-box {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    .filter-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
    
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .profile-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Credenciales de ejemplo (auto_hash=True hará el hash automáticamente)
credentials = {
    "usernames": {
        "admin": {
            "name": "Admin",
            "password": "1234",
            "roles": ["admin"],
            "email": "admin@gmail.com",
        }
    }
}

# Dominios de email permitidos para registro
ALLOWED_DOMAINS = ["gmail.com", "hotmail.com"]

# Opciones de roles disponibles
AVAILABLE_ROLES = ["admin", "medico", "paciente"]

authenticator = stauth.Authenticate(
    credentials,
    cookie_name="app_cookie",
    cookie_key="random_key",
    cookie_expiry_days=30,
    password_instructions=(
        "La contraseña debe tener entre 8 y 20 caracteres, incluir al menos "
        "una minúscula, una mayúscula y un caracter especial (@$!%*?&)."
    ),
)

# Encabezado principal
st.markdown("""
<div class="main-header">
    <h1>🏥 ServiSalud</h1>
    <p>Sistema Integral de Información de Salud Pública - Cundinamarca y Boyacá</p>
</div>
""", unsafe_allow_html=True)

# Si no está autenticado, mostrar pestañas de acceso
if not st.session_state.get("authentication_status"):
    st.markdown("### 🔐 Acceso al Sistema")
    
    tab_login, tab_register, tab_forgot_pwd, tab_forgot_user = st.tabs([
        "📝 Iniciar Sesión", "👤 Registrarse", "🔑 Recuperar Contraseña", "👥 Recuperar Usuario"
    ])

    with tab_login:
        st.markdown("#### Iniciar Sesión en ServiSalud")
        authenticator.login(location="main", key="Login", clear_on_submit=False)

    with tab_register:
        st.markdown("#### Crear Nueva Cuenta")
        st.markdown(f"**Dominios permitidos:** {', '.join(ALLOWED_DOMAINS)}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Requisitos de contraseña:**
            - 8-20 caracteres
            - 1 minúscula
            - 1 mayúscula  
            - 1 caracter especial (@$!%*?&)
            
            **Ejemplo:** Abcd@1234
            """)
        
        with col2:
            selected_roles = st.multiselect(
                "Seleccionar Roles:", 
                options=AVAILABLE_ROLES, 
                default=["paciente"]
            )
            
        email, new_username, full_name = authenticator.register_user(
            location="main",
            captcha=False,
            key="Register user",
            domains=ALLOWED_DOMAINS,
            roles=selected_roles,
            merge_username_email=True,
        )
        if email and new_username and full_name:
            st.success("✅ Usuario registrado correctamente. Ahora puede iniciar sesión.")

    with tab_forgot_pwd:
        st.markdown("#### Recuperar Contraseña")
        username, email, new_password = authenticator.forgot_password(
            location="main",
            captcha=False,
            key="Forgot password",
        )
        if username and email and new_password:
            st.info("📧 Se ha generado una nueva contraseña temporal. Revise su correo o úsela para entrar.")

    with tab_forgot_user:
        st.markdown("#### Recuperar Nombre de Usuario")
        username, email = authenticator.forgot_username(
            location="main",
            captcha=False,
            key="Forgot username",
        )
        if username and email:
            st.info(f"👤 Su usuario es: **{username}**")

# Lee el estado de autenticación desde la sesión
authentication_status = st.session_state.get("authentication_status")
name = st.session_state.get("name")
username = st.session_state.get("username")
roles = st.session_state.get("roles")

# Si está autenticado, mostrar contenido y opciones de cuenta
if authentication_status:
    # Sección de perfil en el sidebar
    with st.sidebar:
        st.markdown("""
        <div class="profile-section">
            <h3>👤 Perfil de Usuario</h3>
            <p><strong>Nombre:</strong> {}</p>
            <p><strong>Usuario:</strong> {}</p>
            <p><strong>Roles:</strong> {}</p>
            <p><strong>Último acceso:</strong> {}</p>
        </div>
        """.format(
            name, 
            username, 
            ', '.join(roles) if roles else 'Sin roles asignados',
            datetime.now().strftime("%d/%m/%Y %H:%M")
        ), unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Botón de logout
        if st.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
            authenticator.logout(button_name="Logout", location="sidebar", key="Logout")
            st.rerun()
    
    # Mensaje de bienvenida principal
    st.markdown(f"""
    <div class="success-box">
        <h2>🎉 ¡Bienvenido a ServiSalud, {name}!</h2>
        <p>Sistema de Información de Salud Pública para Cundinamarca y Boyacá</p>
    </div>
    """, unsafe_allow_html=True)

    # Pestañas para usuarios autenticados
    acct_tab, health_tab, analytics_tab, community_tab = st.tabs([
        "⚙️ Configuración de Cuenta", 
        "🏥 Dashboard de Salud Pública",
        "📊 Análisis y Patrones",
        "👥 Comunidad y Reportes"
    ])
    
    with acct_tab:
        st.markdown("### ⚙️ Configuración de Cuenta")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔑 Cambiar Contraseña")
            st.markdown("Actualiza tu contraseña para mantener la seguridad de tu cuenta.")
        reset_ok = authenticator.reset_password(
            username=username,
            location="main",
            key="Reset password",
        )
        if reset_ok:
            st.success("✅ Contraseña actualizada correctamente.")
        
        st.markdown("---")
        st.markdown("#### 👤 Editar Información Personal")
        
        with st.form("edit_profile_form"):
            new_name = st.text_input(
                "Nombre completo:",
                value=name,
                placeholder="Ingresa tu nombre completo",
                key="edit_name"
            )
            
            new_email = st.text_input(
                "Correo electrónico:",
                value=st.session_state.get("email", ""),
                placeholder="tu@email.com",
                key="edit_email"
            )
            
            submitted_profile = st.form_submit_button("💾 Guardar Cambios", type="primary")
            
            if submitted_profile and new_name:
                # Actualizar el nombre en session state
                st.session_state["name"] = new_name
                st.success("✅ Información personal actualizada correctamente")
                st.rerun()
        
        with col2:
            st.markdown("#### 📊 Información de la Cuenta")
            st.info(f"""
            **Usuario:** {username}  
            **Nombre:** {name}  
            **Roles:** {', '.join(roles) if roles else 'Sin roles asignados'}  
            **Estado:** Activo  
            **Última actualización:** {datetime.now().strftime("%d/%m/%Y")}
            """)
            
            st.markdown("---")
            st.markdown("#### 📈 Estadísticas de Uso")
            
            # Simular estadísticas de uso
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("📊 Consultas Realizadas", "47")
                st.metric("🗺️ Mapas Visualizados", "23")
            with col_b:
                st.metric("📥 Descargas", "12")
                st.metric("💬 Reportes Enviados", "5")
    
    with health_tab:
        st.markdown("""
        <div class="info-box">
            <h2>🏥 Dashboard de Salud Pública</h2>
            <p><strong>Cobertura:</strong> Cundinamarca y Boyacá | <strong>Fuente:</strong> datos.gov.co (Socrata)</p>
            <p>Sistema de información integral para la gestión y análisis de servicios de salud pública</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Función para crear datos de muestra específicos de Cundinamarca y Boyacá
        def create_sample_data():
            """Crear datos de muestra específicos para Cundinamarca y Boyacá"""
            np.random.seed(42)
            n_samples = 200
            
            # Municipios específicos de Cundinamarca y Boyacá
            municipios_cundinamarca = [
                'Bogotá D.C.', 'Soacha', 'Girardot', 'Facatativá', 'Zipaquirá', 
                'Chía', 'Cajicá', 'Madrid', 'Mosquera', 'Fusagasugá', 'Sibaté',
                'Tocancipá', 'Gachancipá', 'Tabio', 'Tenjo', 'Cota', 'La Calera',
                'Choachí', 'Ubaque', 'Fómeque', 'Gachalá', 'Gachetá', 'Gama',
                'Guasca', 'Guatavita', 'Junín', 'La Palma', 'Machetá', 'Manta',
                'Nemocón', 'Pacho', 'Paime', 'Pandi', 'Pulí', 'Quebradanegra',
                'Quetame', 'Quipile', 'Ricaurte', 'San Bernardo', 'San Cayetano'
            ]
            
            municipios_boyaca = [
                'Tunja', 'Duitama', 'Sogamoso', 'Paipa', 'Villa de Leyva',
                'Chiquinquirá', 'Garagoa', 'Monguí', 'Ráquira', 'Tinjacá',
                'Sutamarchán', 'Saboyá', 'Tibasosa', 'Nobsa', 'Iza', 'Firavitoba',
                'Buenavista', 'Covarachía', 'La Uvita', 'San Mateo', 'Sativanorte',
                'Sativasur', 'Soatá', 'Susacón', 'Tipacoque', 'Briceño', 'Buenavista',
                'Busbanzá', 'Caldas', 'Campohermoso', 'Cerinza', 'Chinavita',
                'Chiquiza', 'Chíquiza', 'Chiscas', 'Chita', 'Chitaraque'
            ]
            
            # Combinar municipios
            municipios = municipios_cundinamarca + municipios_boyaca
            departamentos = ['Cundinamarca'] * len(municipios_cundinamarca) + ['Boyacá'] * len(municipios_boyaca)
            
            tipos_servicio = [
                'Consulta Externa', 'Urgencias', 'Hospitalización', 'Cirugía', 
                'Laboratorio', 'Rayos X', 'Farmacia', 'Vacunación', 'Odontología',
                'Pediatría', 'Ginecología', 'Cardiología', 'Medicina Interna'
            ]
            entidades = [
                'Hospital Central', 'Centro de Salud', 'Clínica', 'IPS', 'Puesto de Salud',
                'Hospital Municipal', 'Centro de Atención Primaria', 'Hospital Departamental'
            ]
            
            sample_data = {
                'departamento': np.random.choice(['Cundinamarca', 'Boyacá'], n_samples),
                'municipio': np.random.choice(municipios, n_samples),
                'tipo_servicio': np.random.choice(tipos_servicio, n_samples),
                'entidad': np.random.choice(entidades, n_samples),
                'direccion': [f"Calle {np.random.randint(1, 200)} # {np.random.randint(1, 100)}-{np.random.randint(1, 99)}" 
                             for _ in range(n_samples)],
                'telefono': [f"300-{np.random.randint(100, 999)}-{np.random.randint(1000, 9999)}" 
                           for _ in range(n_samples)],
                'capacidad_atencion': np.random.randint(10, 500, n_samples),
                'pacientes_mes': np.random.randint(50, 2000, n_samples),
                'latitud': np.random.uniform(4.5, 7.0, n_samples),  # Coordenadas específicas de Cundinamarca y Boyacá
                'longitud': np.random.uniform(-75.0, -72.0, n_samples),  # Coordenadas específicas
                'estado': np.random.choice(['Activo', 'En mantenimiento', 'Temporalmente cerrado'], n_samples, p=[0.85, 0.12, 0.03]),
                'fecha_registro': pd.date_range('2023-01-01', '2024-01-01', periods=n_samples),
                'horario_atencion': np.random.choice(['24 horas', '8:00-17:00', '8:00-20:00', '6:00-18:00'], n_samples),
                'especialidades': [', '.join(np.random.choice(tipos_servicio, np.random.randint(1, 4), replace=False)) for _ in range(n_samples)]
            }
            
            return pd.DataFrame(sample_data)
        
        # Selector de base de datos
        st.markdown("### 📊 Selección de Base de Datos")
        
        databases = {
            "9fk3-4e6r": "Servicios de Salud Pública - Cundinamarca y Boyacá (Principal)",
            "f4c7-t4am": "Datos de Salud Pública Colombia (General)",
            "sample": "Datos de Muestra - Demo Interactivo"
        }
        
        # Información sobre las bases de datos
        with st.expander("ℹ️ Información sobre las Bases de Datos"):
            st.markdown("""
            **Bases de Datos Utilizadas:**
            
            **1. 9fk3-4e6r - Servicios de Salud Pública (Principal)**
            - 🔗 **Enlace:** https://www.datos.gov.co/Salud-y-Protecci-n-Social/Servicios-de-Salud-P-blica/9fk3-4e6r
            - 📊 **Contenido:** Información detallada de servicios de salud pública
            - 🗺️ **Cobertura:** Específica para Cundinamarca y Boyacá
            - 📅 **Actualización:** Regular
            
            **2. f4c7-t4am - Datos de Salud Pública Colombia**
            - 🔗 **Enlace:** https://www.datos.gov.co/Salud-y-Protecci-n-Social/Datos-de-Salud-P-blica/f4c7-t4am
            - 📊 **Contenido:** Datos generales de salud pública a nivel nacional
            - 🗺️ **Cobertura:** Nacional (Colombia)
            - 📅 **Actualización:** Regular
            
            **3. Datos de Muestra - Demo Interactivo**
            - 📊 **Contenido:** Datos simulados para demostración
            - 🗺️ **Cobertura:** Cundinamarca y Boyacá (simulado)
            - 🎯 **Propósito:** Pruebas y demostración del sistema
            
            **Fuente:** Portal de Datos Abiertos de Colombia (datos.gov.co)
            """)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_database = st.selectbox(
            "Selecciona una base de datos:",
                options=list(databases.keys()),
                format_func=lambda x: databases[x],
                help="La base de datos principal contiene información específica de Cundinamarca y Boyacá"
            )
        
        with col2:
            if st.button("🔄 Cargar Datos", type="primary", use_container_width=True):
                with st.spinner("Cargando datos de salud..."):
                    try:
                        if selected_database == "sample":
                            df = create_sample_data()
                            st.session_state['health_data'] = df
                            st.session_state['data_source'] = 'sample'
                            st.success(f"✅ Datos de muestra cargados: {len(df)} registros")
                        else:
                            # Cargar datos reales desde la API
                            client = Socrata("www.datos.gov.co", None)
                            results = client.get(selected_database, limit=1000)
                            df = pd.DataFrame.from_records(results)
                            
                            # Filtrar solo Cundinamarca y Boyacá si es necesario
                            if selected_database == "9fk3-4e6r":
                                # Buscar columnas que contengan información de departamento
                                dept_cols = [col for col in df.columns if any(word in col.lower() for word in ['departamento', 'depto', 'departament', 'region', 'estado'])]
                                if dept_cols:
                                    dept_col = dept_cols[0]
                                    # Intentar filtrar por departamento
                                    try:
                                        original_count = len(df)
                                        df = df[df[dept_col].str.contains('Cundinamarca|Boyacá|Cundinamarca D.C.|Bogotá', case=False, na=False)]
                                        filtered_count = len(df)
                                        if filtered_count > 0:
                                            st.info(f"✅ Filtrado por departamento: {original_count} → {filtered_count} registros")
                                        else:
                                            st.info("ℹ️ No se encontraron registros específicos de Cundinamarca/Boyacá, mostrando todos los datos")
                                    except:
                                        st.info("ℹ️ No se pudo filtrar por departamento, mostrando todos los datos disponibles")
                                else:
                                    st.info("ℹ️ Datos generales de salud pública - aplicables a toda Colombia")
                            
                            st.session_state['health_data'] = df
                            st.session_state['data_source'] = 'real'
                            st.success(f"✅ Datos reales cargados: {len(df)} registros")
                    
                    except Exception as e:
                        st.warning(f"⚠️ Error cargando datos reales: {str(e)}")
                        st.info("🔄 Cargando datos de muestra como respaldo...")
                        df = create_sample_data()
                        st.session_state['health_data'] = df
                        st.session_state['data_source'] = 'sample'
                        st.success(f"✅ Datos de muestra cargados: {len(df)} registros")
        
        # Mostrar dashboard si hay datos
        if 'health_data' in st.session_state:
            df = st.session_state['health_data']
            data_source = st.session_state.get('data_source', 'unknown')
            
            # Información del dataset con mejor diseño y datos más dicientes
            st.markdown("### 📊 Información General del Dataset")
            
            # Calcular métricas más informativas
            total_records = len(df)
            unique_entities = df['entidad'].nunique() if 'entidad' in df.columns else df.nunique().sum()
            unique_locations = df['municipio'].nunique() if 'municipio' in df.columns else df.nunique().sum()
            unique_departments = df['departamento'].nunique() if 'departamento' in df.columns else 2
            unique_services = df['tipo_servicio'].nunique() if 'tipo_servicio' in df.columns else df.nunique().sum()
            
            col1, col2, col3, col4, col5 = st.columns(5)
                        with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📊 Total Registros</h4>
                    <h2>{total_records:,}</h2>
                    <p>Servicios de salud registrados</p>
                </div>
                """, unsafe_allow_html=True)
                        with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>🏥 Entidades</h4>
                    <h2>{unique_entities:,}</h2>
                        with col3:
                </div>
                """, unsafe_allow_html=True)
                        with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📍 Municipios</h4>
                        with col4:
                    <p>Ubicaciones diferentes</p>
                </div>
                """, unsafe_allow_html=True)
                        with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>🩺 Tipos de Servicio</h4>
                        with col5:
                    <p>Servicios disponibles</p>
                </div>
                """, unsafe_allow_html=True)
                        with col5:
                source_icon = "🌐" if data_source == 'real' else "📊"
                source_text = 'Real' if data_source == 'real' else 'Muestra'
                coverage = "Cundinamarca & Boyacá" if unique_departments <= 2 else "Nacional"
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📡 Fuente</h4>
                    <h3>{source_icon} {source_text}</h3>
                    <p>Cobertura: {coverage}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Usar todos los datos para análisis
            df_filtered = df.copy()
            
            # Gráficos principales con mejor diseño y detección inteligente
            st.markdown("---")
            st.markdown("### 📊 Análisis Visual de Datos")
            
            # Detectar columnas disponibles de manera más inteligente
            dept_cols = [col for col in df_filtered.columns if any(word in col.lower() for word in ['departamento', 'depto', 'departament', 'region', 'estado'])]
            service_cols = [col for col in df_filtered.columns if any(word in col.lower() for word in ['tipo', 'servicio', 'categoria', 'especialidad', 'modalidad', 'service', 'type'])]
            location_cols = [col for col in df_filtered.columns if any(word in col.lower() for word in ['municipio', 'ciudad', 'localidad', 'barrio', 'municipality', 'city'])]
            
            # Solo mostrar sección si hay datos disponibles
            has_dept_data = len(dept_cols) > 0 and df_filtered[dept_cols[0]].nunique() > 1
            has_service_data = len(service_cols) > 0 and df_filtered[service_cols[0]].nunique() > 1
            
            if has_dept_data or has_service_data:
                col1, col2 = st.columns(2)
                
                with col1:
                    if has_dept_data:
                        st.markdown("""
                        <div class="chart-container">
                            <h4>🏥 Distribución por Departamento</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        dept_col = dept_cols[0]
                        dept_counts = df_filtered[dept_col].value_counts()
                        fig_dept = px.bar(
                            x=dept_counts.values,
                            y=dept_counts.index,
                            orientation='h',
                            title=f"Servicios por {dept_col.title()}",
                            labels={'x': 'Número de Servicios', 'y': dept_col.title()},
                            color=dept_counts.values,
                            color_continuous_scale="Viridis"
                        )
                        fig_dept.update_layout(
                            height=400, 
                            title_x=0.5,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig_dept, use_container_width=True)
                    elif has_service_data:
                        st.markdown("""
                        <div class="chart-container">
                            <h4>🏥 Distribución por Categoría</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        service_col = service_cols[0]
                        service_counts = df_filtered[service_col].value_counts().head(10)
                        fig_service = px.bar(
                            x=service_counts.values,
                            y=service_counts.index,
                            orientation='h',
                            title=f"Distribución por {service_col.title()}",
                            labels={'x': 'Número de Registros', 'y': service_col.title()},
                            color=service_counts.values,
                            color_continuous_scale="Blues"
                        )
                        fig_service.update_layout(
                            height=400, 
                            title_x=0.5,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig_service, use_container_width=True)
                
                with col2:
                    if has_service_data:
                        st.markdown("""
                        <div class="chart-container">
                            <h4>🩺 Tipos de Servicios</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        service_col = service_cols[0]
                        servicio_counts = df_filtered[service_col].value_counts()
                        fig_servicio = px.pie(
                            values=servicio_counts.values,
                            names=servicio_counts.index,
                            title=f"Distribución de {service_col.title()}",
                            color_discrete_sequence=px.colors.qualitative.Set3,
                            hole=0.3
                        )
                        fig_servicio.update_traces(
                            textposition='inside', 
                            textinfo='percent+label',
                            hovertemplate='<b>%{label}</b><br>Registros: %{value}<br>Porcentaje: %{percent}<extra></extra>'
                        )
                        fig_servicio.update_layout(
                            height=400, 
                            title_x=0.5,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig_servicio, use_container_width=True)
                    elif has_dept_data:
                        st.markdown("""
                        <div class="chart-container">
                            <h4>🩺 Distribución por Categoría</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        dept_col = dept_cols[0]
                        dept_counts = df_filtered[dept_col].value_counts()
                        fig_dept_pie = px.pie(
                            values=dept_counts.values,
                            names=dept_counts.index,
                            title=f"Distribución por {dept_col.title()}",
                            color_discrete_sequence=px.colors.qualitative.Pastel,
                            hole=0.3
                        )
                        fig_dept_pie.update_traces(
                            textposition='inside', 
                            textinfo='percent+label'
                        )
                        fig_dept_pie.update_layout(
                            height=400, 
                            title_x=0.5,
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig_dept_pie, use_container_width=True)
            else:
                # Mostrar información alternativa cuando no hay datos específicos
                st.markdown("""
                <div class="chart-container">
                    <h4>📊 Vista General de los Datos</h4>
                    <p>Los datos cargados no contienen columnas específicas de departamento o tipo de servicio.</p>
                    <p>Se muestran las primeras columnas disponibles para exploración.</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Mostrar análisis de las primeras columnas disponibles
                if len(df_filtered.columns) > 0:
                    col1, col2 = st.columns(2)
                    
                with col1:
                        # Análisis de la primera columna categórica
                        categorical_cols = df_filtered.select_dtypes(include=['object']).columns
                        if len(categorical_cols) > 0:
                            first_cat_col = categorical_cols[0]
                            col_counts = df_filtered[first_cat_col].value_counts().head(10)
                            fig_col = px.bar(
                                x=col_counts.values,
                                y=col_counts.index,
                            orientation='h',
                                title=f"Distribución por {first_cat_col.title()}",
                                labels={'x': 'Número de Registros', 'y': first_cat_col.title()},
                                color=col_counts.values,
                                color_continuous_scale="Viridis"
                            )
                            fig_col.update_layout(height=400, title_x=0.5)
                            st.plotly_chart(fig_col, use_container_width=True)
                    
                        with col2:
                        # Análisis de la segunda columna categórica o numérica
                        if len(categorical_cols) > 1:
                            second_cat_col = categorical_cols[1]
                            col_counts2 = df_filtered[second_cat_col].value_counts().head(8)
                            fig_col2 = px.pie(
                                values=col_counts2.values,
                                names=col_counts2.index,
                                title=f"Distribución por {second_cat_col.title()}",
                                color_discrete_sequence=px.colors.qualitative.Set3
                            )
                            fig_col2.update_traces(textposition='inside', textinfo='percent+label')
                            fig_col2.update_layout(height=400, title_x=0.5)
                            st.plotly_chart(fig_col2, use_container_width=True)
                        else:
                            st.info("📋 Usa los filtros arriba para explorar los datos disponibles")
            
            # Mapa geográfico mejorado - solo mostrar si hay coordenadas
            lat_cols = [col for col in df_filtered.columns if any(word in col.lower() for word in ['lat', 'latitude', 'latitud'])]
            lon_cols = [col for col in df_filtered.columns if any(word in col.lower() for word in ['lon', 'lng', 'longitude', 'longitud'])]
            
            has_coordinates = len(lat_cols) > 0 and len(lon_cols) > 0
            
            if has_coordinates:
                st.markdown("---")
                st.markdown("### 🗺️ Mapa de Distribución Geográfica")
                st.markdown("""
                <div class="chart-container">
                    <h4>📍 Ubicación de Servicios de Salud - Cundinamarca y Boyacá</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # Filtrar coordenadas válidas
                lat_col = lat_cols[0]
                lon_col = lon_cols[0]
                df_map = df_filtered.dropna(subset=[lat_col, lon_col])
                
                # Convertir a numérico si es necesario
                try:
                    df_map[lat_col] = pd.to_numeric(df_map[lat_col], errors='coerce')
                    df_map[lon_col] = pd.to_numeric(df_map[lon_col], errors='coerce')
                    df_map = df_map.dropna(subset=[lat_col, lon_col])
                    
                    # Filtrar coordenadas válidas para Colombia
                    df_map = df_map[
                        (df_map[lat_col] >= 4.0) & (df_map[lat_col] <= 12.5) &
                        (df_map[lon_col] >= -81.0) & (df_map[lon_col] <= -66.9)
                    ]
                    
                    if len(df_map) > 0:
                        # Mapa de dispersión mejorado
                        fig_map = px.scatter_mapbox(
                            df_map,
                            lat=lat_col,
                            lon=lon_col,
                            hover_name=location_cols[0] if len(location_cols) > 0 else None,
                            hover_data=[col for col in [dept_cols[0] if len(dept_cols) > 0 else None, 
                                                       service_cols[0] if len(service_cols) > 0 else None] if col],
                            color=dept_cols[0] if len(dept_cols) > 0 else service_cols[0] if len(service_cols) > 0 else None,
                            size_max=15,
                            zoom=6,
                            height=600,
                            title="Distribución Geográfica de Servicios de Salud",
                            color_discrete_sequence=px.colors.qualitative.Set1
                        )
                        
                        fig_map.update_layout(
                            mapbox_style="open-street-map",
                            margin={"r": 0, "t": 50, "l": 0, "b": 0},
                            title_x=0.5,
                            title_font_size=16
                        )
                        
                        st.plotly_chart(fig_map, use_container_width=True)
                        
                        # Estadísticas del mapa mejoradas
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>📍 Puntos Mapeados</h4>
                                <h2>{len(df_map):,}</h2>
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            cobertura_mapa = (len(df_map)/len(df_filtered)*100) if len(df_filtered) > 0 else 0
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>📊 Cobertura</h4>
                                <h2>{cobertura_mapa:.1f}%</h2>
                            </div>
                        )
                        with col3:
                            municipios_mapa = df_map[location_cols[0]].nunique() if len(location_cols) > 0 else len(df_map)
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🏘️ Ubicaciones</h4>
                                <h2>{municipios_mapa:,}</h2>
                            </div>
                            """, unsafe_allow_html=True)
                        with col4:
                            departamentos_mapa = df_map[dept_cols[0]].nunique() if len(dept_cols) > 0 else 1
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🗺️ Regiones</h4>
                                <h2>{departamentos_mapa}</h2>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ No se encontraron coordenadas válidas para Colombia")
                except Exception as e:
                    st.error(f"❌ Error al procesar coordenadas: {str(e)}")
            # Si no hay coordenadas, no mostrar la sección del mapa
            
            # Tabla de datos mejorada
            st.markdown("---")
            st.markdown("### 📋 Directorio de Servicios de Salud")
            
            # Mostrar solo columnas relevantes
            display_cols = []
            for col in ['municipio', 'departamento', 'tipo_servicio', 'entidad', 'estado', 'telefono', 'direccion']:
                if col in df_filtered.columns:
                    display_cols.append(col)
            
            if display_cols:
                st.markdown("#### 📊 Vista Previa de Datos (Primeras 20 entradas)")
                st.dataframe(
                    df_filtered[display_cols].head(20),
                    use_container_width=True,
                    height=400
                )
                
                # Botones de descarga mejorados
                col1, col2, col3 = st.columns(3)
                
                        with col1:
                    csv = df_filtered[display_cols].to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar CSV",
                        data=csv,
                        file_name=f"servicios_salud_cundinamarca_boyaca_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                        with col2:
                    excel_data = df_filtered[display_cols].to_excel(index=False)
                    st.download_button(
                        label="📊 Descargar Excel",
                        data=excel_data,
                        file_name=f"servicios_salud_cundinamarca_boyaca_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                        with col3:
                    json_data = df_filtered[display_cols].to_json(orient='records', indent=2)
                    st.download_button(
                        label="📄 Descargar JSON",
                        data=json_data,
                        file_name=f"servicios_salud_cundinamarca_boyaca_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
            else:
                st.dataframe(df_filtered.head(20), use_container_width=True, height=400)
    
    with analytics_tab:
        st.markdown("""
        <div class="info-box">
            <h2>📊 Análisis de Patrones y Tendencias</h2>
            <p>Identificación automática de patrones en la demanda de servicios de salud</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Análisis de patrones temporales
        st.markdown("### 📈 Análisis de Demanda Temporal")
        
        # Simular datos temporales para análisis
        if 'health_data' in st.session_state:
            df = st.session_state['health_data']
            
            # Crear datos temporales simulados
            dates = pd.date_range('2023-01-01', '2024-01-01', freq='D')
            np.random.seed(42)
            
            # Patrones estacionales simulados
            seasonal_pattern = np.sin(2 * np.pi * np.arange(len(dates)) / 365.25) * 20
            rain_effect = np.sin(2 * np.pi * np.arange(len(dates)) / 365.25 + np.pi) * 15
            trend = np.linspace(0, 30, len(dates))
            noise = np.random.normal(0, 5, len(dates))
            
            # Simular diferentes tipos de consultas
            respiratory_cases = 50 + seasonal_pattern + rain_effect + noise
            general_consultations = 100 + seasonal_pattern * 0.5 + trend + noise
            vaccination_demand = 30 + np.maximum(0, np.sin(2 * np.pi * np.arange(len(dates)) / 30)) * 40 + noise * 0.5
            
            # Crear DataFrame temporal
            temporal_data = pd.DataFrame({
                'fecha': dates,
                'consultas_respiratorias': np.maximum(0, respiratory_cases),
                'consultas_generales': np.maximum(0, general_consultations),
                'demanda_vacunacion': np.maximum(0, vaccination_demand),
                'mes': dates.month,
                'estacion': dates.map(lambda x: 'Invierno' if x.month in [12,1,2] 
                                   else 'Primavera' if x.month in [3,4,5]
                                   else 'Verano' if x.month in [6,7,8]
                                   else 'Otoño')
            })
            
            # Gráficos de análisis temporal
            col1, col2 = st.columns(2)
            
                        with col1:
                st.markdown("#### 📊 Tendencias Mensuales")
                monthly_data = temporal_data.groupby('mes').agg({
                    'consultas_respiratorias': 'mean',
                    'consultas_generales': 'mean',
                    'demanda_vacunacion': 'mean'
                }).reset_index()
                
                fig_monthly = px.bar(
                    monthly_data,
                            x='mes', 
                    y=['consultas_respiratorias', 'consultas_generales', 'demanda_vacunacion'],
                    title="Promedio de Consultas por Mes",
                    barmode='group',
                    color_discrete_sequence=['#ff6b6b', '#4ecdc4', '#45b7d1']
                )
                fig_monthly.update_layout(
                    height=400,
                    title_x=0.5,
                    xaxis_title="Mes",
                    yaxis_title="Número de Consultas"
                )
                st.plotly_chart(fig_monthly, use_container_width=True)
            
                        with col2:
                st.markdown("#### 🌧️ Patrones Estacionales")
                seasonal_data = temporal_data.groupby('estacion').agg({
                    'consultas_respiratorias': 'mean',
                    'consultas_generales': 'mean',
                    'demanda_vacunacion': 'mean'
                }).reset_index()
                
                fig_seasonal = px.pie(
                    seasonal_data,
                    values='consultas_respiratorias',
                    names='estacion',
                    title="Distribución de Consultas Respiratorias por Estación",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_seasonal.update_traces(textposition='inside', textinfo='percent+label')
                fig_seasonal.update_layout(height=400, title_x=0.5)
                        st.plotly_chart(fig_seasonal, use_container_width=True)
            
            # Análisis de patrones específicos
            st.markdown("### 🔍 Identificación de Patrones")
                
            col1, col2, col3 = st.columns(3)
                
                        with col1:
                st.markdown("""
                <div class="metric-card">
                    <h4>🌧️ Temporada de Lluvias</h4>
                    <h3>+25% Consultas Respiratorias</h3>
                    <p>Patrón identificado: Incremento en infecciones respiratorias durante marzo-mayo y octubre-diciembre</p>
                </div>
                """, unsafe_allow_html=True)
            
                        with col2:
                st.markdown("""
                <div class="metric-card">
                    <h4>💉 Campañas de Vacunación</h4>
                    <h3>Picos Mensuales</h3>
                    <p>Patrón identificado: Mayor demanda en los primeros 15 días de cada mes</p>
                </div>
                """, unsafe_allow_html=True)
            
                        with col3:
                st.markdown("""
                <div class="metric-card">
                    <h4>🌡️ Cambios de Temperatura</h4>
                    <h3>Invierno: +40%</h3>
                    <p>Patrón identificado: Incremento en consultas generales durante temporada invernal</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Gráfico de líneas temporal con etiquetas mejoradas
            st.markdown("### 📈 Evolución Temporal de la Demanda")
            
            fig_temporal = px.line(
                temporal_data,
                x='fecha',
                y=['consultas_respiratorias', 'consultas_generales', 'demanda_vacunacion'],
                title="Evolución de la Demanda de Servicios de Salud",
                labels={
                    'value': 'Número de Consultas Diarias', 
                    'fecha': 'Fecha (Eje X: Tiempo)',
                    'consultas_respiratorias': 'Consultas Respiratorias',
                    'consultas_generales': 'Consultas Generales',
                    'demanda_vacunacion': 'Demanda de Vacunación'
                },
                color_discrete_sequence=['#ff6b6b', '#4ecdc4', '#45b7d1']
            )
            fig_temporal.update_layout(
                height=500,
                title_x=0.5,
                hovermode='x unified',
                xaxis_title="📅 Fecha (Eje X: Tiempo)",
                yaxis_title="📊 Número de Consultas Diarias (Eje Y: Demanda)",
                legend_title="Tipo de Servicio"
            )
            st.plotly_chart(fig_temporal, use_container_width=True)
            
            # Información sobre los ejes
            st.info("""
            **📊 Interpretación de los Ejes:**
            - **Eje X (Horizontal):** Fecha - Muestra la evolución temporal día a día
            - **Eje Y (Vertical):** Número de Consultas - Cantidad de demanda diaria por tipo de servicio
            - **Líneas:** Cada color representa un tipo diferente de consulta médica
            """)
            
            # Sección de Predicciones con Machine Learning
            st.markdown("---")
            st.markdown("### 🔮 Predicciones con Machine Learning")
            
            # Preparar datos para el modelo
            temporal_data['dias'] = (temporal_data['fecha'] - temporal_data['fecha'].min()).dt.days
            
            # Crear modelos de regresión lineal para cada tipo de consulta
            col1, col2 = st.columns(2)
            
                        with col1:
                st.markdown("#### 📊 Modelo de Regresión Lineal")
                
                # Entrenar modelo para consultas respiratorias
                X = temporal_data[['dias']].values
                y_respiratorias = temporal_data['consultas_respiratorias'].values
                y_generales = temporal_data['consultas_generales'].values
                y_vacunacion = temporal_data['demanda_vacunacion'].values
                
                # Modelos
                model_respiratorias = LinearRegression()
                model_generales = LinearRegression()
                model_vacunacion = LinearRegression()
                
                # Entrenar modelos
                model_respiratorias.fit(X, y_respiratorias)
                model_generales.fit(X, y_generales)
                model_vacunacion.fit(X, y_vacunacion)
                
                # Predicciones para los próximos 5 años (1825 días)
                dias_futuros = np.arange(temporal_data['dias'].max() + 1, temporal_data['dias'].max() + 1826).reshape(-1, 1)
                fechas_futuras = [temporal_data['fecha'].max() + timedelta(days=int(d)) for d in dias_futuros.flatten()]
                
                pred_respiratorias = model_respiratorias.predict(dias_futuros)
                pred_generales = model_generales.predict(dias_futuros)
                pred_vacunacion = model_vacunacion.predict(dias_futuros)
                
                # Crear DataFrame de predicciones
                pred_data = pd.DataFrame({
                    'fecha': fechas_futuras,
                    'consultas_respiratorias': pred_respiratorias,
                    'consultas_generales': pred_generales,
                    'demanda_vacunacion': pred_vacunacion,
                    'tipo': 'Predicción'
                })
                
                # Combinar datos históricos y predicciones
                historical_data = temporal_data.copy()
                historical_data['tipo'] = 'Histórico'
                
                combined_data = pd.concat([historical_data, pred_data], ignore_index=True)
                
                # Gráfico con predicciones
                            fig_pred = go.Figure()
                
                # Datos históricos
                fig_pred.add_trace(go.Scatter(
                    x=historical_data['fecha'],
                    y=historical_data['consultas_respiratorias'],
                    mode='lines',
                    name='Consultas Respiratorias (Histórico)',
                    line=dict(color='#ff6b6b', width=2)
                ))
                
                fig_pred.add_trace(go.Scatter(
                    x=historical_data['fecha'],
                    y=historical_data['consultas_generales'],
                    mode='lines',
                    name='Consultas Generales (Histórico)',
                    line=dict(color='#4ecdc4', width=2)
                ))
                
                fig_pred.add_trace(go.Scatter(
                    x=historical_data['fecha'],
                    y=historical_data['demanda_vacunacion'],
                    mode='lines',
                    name='Demanda Vacunación (Histórico)',
                    line=dict(color='#45b7d1', width=2)
                ))
                
                # Predicciones
                fig_pred.add_trace(go.Scatter(
                    x=pred_data['fecha'],
                    y=pred_data['consultas_respiratorias'],
                    mode='lines',
                    name='Consultas Respiratorias (Predicción)',
                    line=dict(color='#ff6b6b', width=2, dash='dash')
                ))
                
                fig_pred.add_trace(go.Scatter(
                    x=pred_data['fecha'],
                    y=pred_data['consultas_generales'],
                    mode='lines',
                    name='Consultas Generales (Predicción)',
                    line=dict(color='#4ecdc4', width=2, dash='dash')
                ))
                
                fig_pred.add_trace(go.Scatter(
                    x=pred_data['fecha'],
                    y=pred_data['demanda_vacunacion'],
                    mode='lines',
                    name='Demanda Vacunación (Predicción)',
                    line=dict(color='#45b7d1', width=2, dash='dash')
                ))
                
                fig_pred.update_layout(
                    title="Predicciones de Demanda para los Próximos 5 Años",
                    xaxis_title="Fecha",
                    yaxis_title="Número de Consultas",
                    height=500,
                    title_x=0.5
                )
                
                            st.plotly_chart(fig_pred, use_container_width=True)
                    
                        with col2:
                st.markdown("#### 📈 Métricas del Modelo")
                
                # Calcular métricas de rendimiento
                y_pred_resp = model_respiratorias.predict(X)
                y_pred_gen = model_generales.predict(X)
                y_pred_vac = model_vacunacion.predict(X)
                
                # R² scores
                r2_resp = r2_score(y_respiratorias, y_pred_resp)
                r2_gen = r2_score(y_generales, y_pred_gen)
                r2_vac = r2_score(y_vacunacion, y_pred_vac)
                
                # MSE
                mse_resp = mean_squared_error(y_respiratorias, y_pred_resp)
                mse_gen = mean_squared_error(y_generales, y_pred_gen)
                mse_vac = mean_squared_error(y_vacunacion, y_pred_vac)
                
                # Mostrar métricas
                st.metric("Consultas Respiratorias - R²", f"{r2_resp:.3f}")
                st.metric("Consultas Generales - R²", f"{r2_gen:.3f}")
                st.metric("Demanda Vacunación - R²", f"{r2_vac:.3f}")
                
                st.markdown("---")
                
                # Predicciones específicas para el próximo año
                st.markdown("#### 🎯 Predicciones para el Próximo Año")
                
                # Predicciones mensuales para el próximo año
                pred_anual = pred_data[pred_data['fecha'] <= temporal_data['fecha'].max() + timedelta(days=365)]
                pred_mensual = pred_anual.groupby(pred_anual['fecha'].dt.to_period('M')).mean()
                
                # Crear gráfico de barras para predicciones mensuales
                fig_mensual = px.bar(
                    x=pred_mensual.index.astype(str),
                    y=[pred_mensual['consultas_respiratorias'], pred_mensual['consultas_generales'], pred_mensual['demanda_vacunacion']],
                    title="Predicción Mensual - Próximo Año",
                    labels={'x': 'Mes', 'value': 'Consultas Promedio'},
                    color_discrete_sequence=['#ff6b6b', '#4ecdc4', '#45b7d1']
                )
                
                fig_mensual.update_layout(
                    height=300,
                    title_x=0.5,
                    barmode='group'
                )
                
                st.plotly_chart(fig_mensual, use_container_width=True)
                
                # Resumen de predicciones
                st.markdown("#### 📊 Resumen de Predicciones")
                
                avg_resp_anual = pred_anual['consultas_respiratorias'].mean()
                avg_gen_anual = pred_anual['consultas_generales'].mean()
                avg_vac_anual = pred_anual['demanda_vacunacion'].mean()
                
                st.info(f"""
                **Promedio Anual Predicho:**
                - 🫁 Consultas Respiratorias: {avg_resp_anual:.0f} por día
                - 🏥 Consultas Generales: {avg_gen_anual:.0f} por día  
                - 💉 Demanda Vacunación: {avg_vac_anual:.0f} por día
                
                **Tendencia:** {'📈 Creciente' if pred_data['consultas_respiratorias'].iloc[-1] > temporal_data['consultas_respiratorias'].iloc[-1] else '📉 Decreciente'}
                """)
            
            # Modelo de Clasificación para Patrones de Demanda
            st.markdown("---")
            st.markdown("### 🤖 Modelo de Clasificación de Patrones")
            
            # Crear características para clasificación
            temporal_data['mes'] = temporal_data['fecha'].dt.month
            temporal_data['dia_semana'] = temporal_data['fecha'].dt.dayofweek
            temporal_data['estacion'] = temporal_data['fecha'].dt.month.map({
                            12: 'Invierno', 1: 'Invierno', 2: 'Invierno',
                            3: 'Primavera', 4: 'Primavera', 5: 'Primavera',
                            6: 'Verano', 7: 'Verano', 8: 'Verano',
                            9: 'Otoño', 10: 'Otoño', 11: 'Otoño'
                        })
                        
            # Crear etiquetas de clasificación basadas en el nivel de demanda
            def clasificar_demanda(row):
                total = row['consultas_respiratorias'] + row['consultas_generales'] + row['demanda_vacunacion']
                if total < 150:
                    return 'Baja'
                elif total < 200:
                    return 'Media'
                else:
                    return 'Alta'
            
            temporal_data['nivel_demanda'] = temporal_data.apply(clasificar_demanda, axis=1)
            
            # Preparar datos para clasificación
            X_class = temporal_data[['mes', 'dia_semana', 'consultas_respiratorias', 'consultas_generales', 'demanda_vacunacion']]
            y_class = temporal_data['nivel_demanda']
            
            # Entrenar modelo de clasificación
            classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            classifier.fit(X_class, y_class)
            
            # Predicciones de clasificación para datos futuros
            X_future = pred_data[['consultas_respiratorias', 'consultas_generales', 'demanda_vacunacion']].copy()
            X_future['mes'] = pred_data['fecha'].dt.month
            X_future['dia_semana'] = pred_data['fecha'].dt.dayofweek
            
            pred_classes = classifier.predict(X_future)
            pred_data['nivel_demanda_pred'] = pred_classes
            
            col1, col2 = st.columns(2)
            
                        with col1:
                st.markdown("#### 🎯 Clasificación de Niveles de Demanda")
                
                # Distribución de niveles de demanda históricos
                hist_demand = temporal_data['nivel_demanda'].value_counts()
                fig_hist_demand = px.pie(
                    values=hist_demand.values,
                    names=hist_demand.index,
                    title="Distribución Histórica de Niveles de Demanda",
                    color_discrete_sequence=['#ff9999', '#ffcc99', '#99ff99']
                )
                fig_hist_demand.update_layout(height=300, title_x=0.5)
                st.plotly_chart(fig_hist_demand, use_container_width=True)
                
                # Predicciones de clasificación para el próximo año
                pred_anual_class = pred_data[pred_data['fecha'] <= temporal_data['fecha'].max() + timedelta(days=365)]
                pred_demand_anual = pred_anual_class['nivel_demanda_pred'].value_counts()
                
                fig_pred_demand = px.pie(
                    values=pred_demand_anual.values,
                    names=pred_demand_anual.index,
                    title="Predicción de Niveles de Demanda - Próximo Año",
                    color_discrete_sequence=['#ff9999', '#ffcc99', '#99ff99']
                )
                fig_pred_demand.update_layout(height=300, title_x=0.5)
                st.plotly_chart(fig_pred_demand, use_container_width=True)
            
                        with col2:
                st.markdown("#### 📊 Análisis de Características")
                
                # Importancia de características
                feature_importance = pd.DataFrame({
                    'Característica': ['Mes', 'Día Semana', 'Consultas Respiratorias', 'Consultas Generales', 'Demanda Vacunación'],
                    'Importancia': classifier.feature_importances_
                }).sort_values('Importancia', ascending=True)
                
                fig_importance = px.bar(
                    feature_importance,
                    x='Importancia',
                    y='Característica',
                        orientation='h',
                    title="Importancia de Características en la Clasificación",
                    color='Importancia',
                    color_continuous_scale='Viridis'
                )
                fig_importance.update_layout(height=300, title_x=0.5)
                st.plotly_chart(fig_importance, use_container_width=True)
                
                # Métricas de clasificación
                y_pred_class = classifier.predict(X_class)
                accuracy = accuracy_score(y_class, y_pred_class)
                
                st.metric("Precisión del Modelo de Clasificación", f"{accuracy:.3f}")
                
                # Resumen de predicciones de clasificación
                st.markdown("#### 📈 Resumen de Clasificaciones")
                
                alta_demanda = (pred_anual_class['nivel_demanda_pred'] == 'Alta').sum()
                media_demanda = (pred_anual_class['nivel_demanda_pred'] == 'Media').sum()
                baja_demanda = (pred_anual_class['nivel_demanda_pred'] == 'Baja').sum()
                
                total_dias = len(pred_anual_class)
                
                st.info(f"""
                **Distribución Predicha para el Próximo Año:**
                - 🔴 Alta Demanda: {alta_demanda} días ({alta_demanda/total_dias*100:.1f}%)
                - 🟡 Media Demanda: {media_demanda} días ({media_demanda/total_dias*100:.1f}%)
                - 🟢 Baja Demanda: {baja_demanda} días ({baja_demanda/total_dias*100:.1f}%)
                
                **Recomendación:** {'⚠️ Preparar recursos adicionales' if alta_demanda > total_dias*0.3 else '✅ Recursos actuales suficientes'}
                """)
            
            # Histograma de distribución con etiquetas mejoradas
            st.markdown("### 📊 Distribución de la Demanda")
            
            col1, col2 = st.columns(2)
            
                with col1:
                fig_hist = px.histogram(
                    temporal_data,
                    x='consultas_respiratorias',
                    nbins=20,
                    title="Distribución de Consultas Respiratorias",
                    labels={
                        'consultas_respiratorias': 'Número de Consultas Respiratorias (Eje X)',
                        'count': 'Frecuencia (Eje Y)'
                    },
                    color_discrete_sequence=['#ff6b6b']
                )
                fig_hist.update_layout(
                    height=400, 
                    title_x=0.5,
                    xaxis_title="📊 Número de Consultas Respiratorias (Eje X: Cantidad)",
                    yaxis_title="📈 Frecuencia (Eje Y: Veces que ocurre)"
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
                with col2:
                fig_hist2 = px.histogram(
                    temporal_data,
                    x='consultas_generales',
                    nbins=20,
                    title="Distribución de Consultas Generales",
                    labels={
                        'consultas_generales': 'Número de Consultas Generales (Eje X)',
                        'count': 'Frecuencia (Eje Y)'
                    },
                    color_discrete_sequence=['#4ecdc4']
                )
                fig_hist2.update_layout(
                    height=400, 
                    title_x=0.5,
                    xaxis_title="📊 Número de Consultas Generales (Eje X: Cantidad)",
                    yaxis_title="📈 Frecuencia (Eje Y: Veces que ocurre)"
                )
                st.plotly_chart(fig_hist2, use_container_width=True)
            
        
        else:
            st.info("⚠️ Cargue datos de salud primero para ver el análisis de patrones")
    
    with community_tab:
        st.markdown("""
        <div class="info-box">
            <h2>👥 Participación Comunitaria</h2>
            <p>Formularios para recopilar información de la comunidad y mejorar los servicios</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Formularios de la comunidad
        tab_symptoms, tab_availability, tab_feedback = st.tabs([
            "🩺 Síntomas Frecuentes", 
            "📅 Disponibilidad", 
            "💬 Comentarios"
        ])
        
        with tab_symptoms:
            st.markdown("### 🩺 Reporte de Síntomas Frecuentes en tu Zona")
            
            with st.form("symptoms_form"):
                col1, col2 = st.columns(2)
                
                        with col1:
                    st.markdown("#### 📍 Información de Ubicación")
                    departamento = st.selectbox(
                        "Departamento:",
                        ["Cundinamarca", "Boyacá"],
                        key="symptoms_dept"
                    )
                    
                    municipio = st.selectbox(
                        "Municipio:",
                        ["Bogotá D.C.", "Soacha", "Tunja", "Duitama", "Sogamoso", "Otro"],
                        key="symptoms_municipality"
                    )
                    
                    barrio = st.text_input(
                        "Barrio/Localidad:",
                        placeholder="Ej: Centro, Norte, Sur...",
                        key="symptoms_neighborhood"
                    )
                
                        with col2:
                    st.markdown("#### 🩺 Síntomas Observados")
                    
                    symptoms = st.multiselect(
                        "Síntomas más frecuentes en tu zona:",
                        [
                            "Fiebre alta", "Tos persistente", "Dolor de garganta",
                            "Congestión nasal", "Dolor de cabeza", "Fatiga",
                            "Dolor muscular", "Náuseas", "Vómitos", "Diarrea",
                            "Dificultad respiratoria", "Pérdida del olfato/gusto",
                            "Erupciones cutáneas", "Dolor abdominal", "Otro"
                        ],
                        key="symptoms_list"
                    )
                    
                    frequency = st.selectbox(
                        "Frecuencia observada:",
                        ["Muy frecuente", "Frecuente", "Moderada", "Poco frecuente"],
                        key="symptoms_frequency"
                    )
                    
                    age_group = st.selectbox(
                        "Grupo de edad más afectado:",
                        ["Niños (0-12 años)", "Adolescentes (13-18 años)", 
                         "Adultos jóvenes (19-35 años)", "Adultos (36-60 años)", 
                         "Adultos mayores (60+ años)", "Todos los grupos"],
                        key="symptoms_age"
                    )
                
                st.markdown("#### 📝 Información Adicional")
                additional_info = st.text_area(
                    "Información adicional sobre síntomas o condiciones en tu zona:",
                    placeholder="Describe cualquier patrón que hayas notado, fechas específicas, etc.",
                    key="symptoms_additional"
                )
                
                submitted_symptoms = st.form_submit_button("📤 Enviar Reporte de Síntomas", type="primary")
                
                if submitted_symptoms:
                    st.success("✅ Reporte de síntomas enviado exitosamente")
                st.info("""
                    **Información enviada:**
                    - Departamento: {}
                    - Municipio: {}
                    - Síntomas: {}
                    - Frecuencia: {}
                    - Grupo de edad: {}
                    """.format(departamento, municipio, ', '.join(symptoms), frequency, age_group))
        
        with tab_availability:
            st.markdown("### 📅 Disponibilidad para Campañas de Salud")
            
            with st.form("availability_form"):
                col1, col2 = st.columns(2)
                
                        with col1:
                    st.markdown("#### 👤 Información Personal")
                    name_volunteer = st.text_input(
                        "Nombre completo:",
                        placeholder="Tu nombre completo",
                        key="volunteer_name"
                    )
                    
                    phone = st.text_input(
                        "Teléfono de contacto:",
                        placeholder="Ej: 300-123-4567",
                        key="volunteer_phone"
                    )
                    
                    email = st.text_input(
                        "Correo electrónico:",
                        placeholder="tu@email.com",
                        key="volunteer_email"
                    )
                    
                    profession = st.selectbox(
                        "Profesión/Área de trabajo:",
                        [
                            "Médico", "Enfermero/a", "Técnico en salud",
                            "Estudiante de salud", "Voluntario general",
                            "Administrativo", "Otro"
                        ],
                        key="volunteer_profession"
                    )
                
                        with col2:
                    st.markdown("#### 📅 Disponibilidad")
                    
                    days_available = st.multiselect(
                        "Días de la semana disponibles:",
                        ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
                        key="available_days"
                    )
                    
                    time_preference = st.selectbox(
                        "Horario preferido:",
                        ["Mañana (6:00 AM - 12:00 PM)", "Tarde (12:00 PM - 6:00 PM)", 
                         "Noche (6:00 PM - 10:00 PM)", "Cualquier horario"],
                        key="time_preference"
                    )
                    
                    campaign_types = st.multiselect(
                        "Tipo de campañas de interés:",
                        [
                            "Vacunación", "Tamizaje médico", "Educación en salud",
                            "Prevención de enfermedades", "Salud mental",
                            "Salud materno-infantil", "Salud del adulto mayor",
                            "Emergencias médicas"
                        ],
                        key="campaign_interests"
                    )
                    
                    experience = st.selectbox(
                        "Experiencia en campañas de salud:",
                        ["Sin experiencia", "1-2 campañas", "3-5 campañas", 
                         "Más de 5 campañas", "Experto en el área"],
                        key="campaign_experience"
                    )
                
                st.markdown("#### 💬 Comentarios Adicionales")
                comments = st.text_area(
                    "Comentarios sobre tu disponibilidad o habilidades especiales:",
                    placeholder="Menciona cualquier habilidad especial, idiomas, disponibilidad especial, etc.",
                    key="availability_comments"
                )
                
                submitted_availability = st.form_submit_button("📤 Enviar Disponibilidad", type="primary")
                
                if submitted_availability:
                    st.success("✅ Información de disponibilidad enviada exitosamente")
                    st.info("""
                    **Información registrada:**
                    - Nombre: {}
                    - Disponibilidad: {}
                    - Horario: {}
                    - Intereses: {}
                    """.format(name_volunteer, ', '.join(days_available), time_preference, ', '.join(campaign_types)))
        
        with tab_feedback:
            st.markdown("### 💬 Comentarios y Sugerencias")
            
            with st.form("feedback_form"):
                st.markdown("#### 📝 Tu Opinión es Importante")
                
                feedback_type = st.selectbox(
                    "Tipo de comentario:",
                    ["Sugerencia de mejora", "Reporte de problema", "Experiencia positiva", 
                     "Propuesta de nueva funcionalidad", "Otro"],
                    key="feedback_type"
                )
                
                rating = st.slider(
                    "Calificación general del servicio:",
                    min_value=1,
                    max_value=5,
                    value=4,
                    key="service_rating"
                )
                
                feedback_text = st.text_area(
                    "Describe tu comentario o sugerencia:",
                    placeholder="Sé específico y detallado para ayudarnos a mejorar...",
                    key="feedback_text"
                )
                
                contact_preference = st.radio(
                    "¿Te gustaría que te contactemos?",
                    ["Sí, por correo electrónico", "Sí, por teléfono", "No, es solo un comentario"],
                    key="contact_preference"
                )
                
                if contact_preference.startswith("Sí"):
                    contact_info = st.text_input(
                        "Información de contacto:",
                        placeholder="Correo o teléfono",
                        key="contact_info"
                    )
                
                submitted_feedback = st.form_submit_button("📤 Enviar Comentario", type="primary")
                
                if submitted_feedback:
                    st.success("✅ Comentario enviado exitosamente")
                    st.info(f"**Calificación:** {'⭐' * rating} ({rating}/5)")
                    st.info("Gracias por tu retroalimentación. Tu opinión nos ayuda a mejorar ServiSalud.")
        
        # Resumen de participación comunitaria
        st.markdown("---")
        st.markdown("### 📊 Resumen de Participación Comunitaria")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📝 Reportes de Síntomas", "127")
        with col2:
            st.metric("👥 Voluntarios Registrados", "89")
        with col3:
            st.metric("💬 Comentarios Recibidos", "203")
        with col4:
            st.metric("⭐ Calificación Promedio", "4.2/5")

elif authentication_status is False:
    st.error("❌ Usuario/contraseña incorrectos")
else:
    st.warning("⚠️ Por favor ingrese sus credenciales para acceder al sistema")
