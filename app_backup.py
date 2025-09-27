import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from sodapy import Socrata
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
# Importaciones de sklearn removidas - no se usan en la versión simplificada

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
    # Temporalmente, establecer como autenticado para mostrar el contenido
    st.session_state["authentication_status"] = True
    st.session_state["name"] = "Usuario Demo"
    st.session_state["username"] = "demo"
    st.session_state["roles"] = ["user"]
    
    # Mostrar mensaje informativo
    st.success("🔓 Acceso en modo demo - Para funcionalidad completa, inicia sesión")
    
    # Pestañas de acceso (mantener para futura autenticación)
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
            
            # Métricas principales simplificadas
                col1, col2, col3 = st.columns(3)
            
                with col1:
                st.metric("📊 Total Registros", f"{total_records:,}")
            
                with col2:
                st.metric("🏥 Entidades", f"{unique_entities:,}")
            
                with col3:
                st.metric("📍 Municipios", f"{unique_locations:,}")
            
            # Usar todos los datos para análisis
            df_filtered = df.copy()
            
            # Gráficos principales
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
                
                # Gráficos simples
                if len(df_filtered.columns) > 0:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        categorical_cols = df_filtered.select_dtypes(include=['object']).columns
                        if len(categorical_cols) > 0:
                            first_cat_col = categorical_cols[0]
                            col_counts = df_filtered[first_cat_col].value_counts().head(10)
                            fig_col = px.bar(
                                x=col_counts.values,
                                y=col_counts.index,
                                orientation='h',
                                title=f"Distribución por {first_cat_col.title()}",
                                color=col_counts.values,
                                color_continuous_scale="Viridis"
                            )
                            fig_col.update_layout(height=400, title_x=0.5)
                            st.plotly_chart(fig_col, use_container_width=True)
                    
                    with col2:
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
                            st.info("📋 No hay más columnas categóricas disponibles")
                else:
                    st.info("📋 No hay datos disponibles para mostrar gráficos")
            
            # Mapa geográfico mejorado - solo mostrar si hay coordenadas
            
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
            
            st.info("📊 Análisis temporal disponible")
            
            # Tabla de datos
            st.markdown("### 📋 Datos")
            st.dataframe(df_filtered.head(100))
    
    with community_tab:
        st.markdown("### 👥 Comunidad y Reportes")
        st.info("Esta sección está en desarrollo")
