import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from sodapy import Socrata
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

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
    
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .info-box h2 {
        margin: 0 0 0.5rem 0;
        font-size: 1.8rem;
        font-weight: bold;
    }
    
    .info-box p {
        margin: 0.3rem 0;
        opacity: 0.9;
        font-size: 1rem;
    }
    
    .welcome-banner {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    .welcome-banner h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: bold;
    }
    
    .profile-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    
    .profile-card h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1.2rem;
    }
    
    .profile-card p {
        margin: 0.2rem 0;
        font-size: 0.9rem;
        opacity: 0.9;
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
        },
        "user": {
            "name": "Usuario",
            "password": "1234",
            "roles": ["user"],
        }
    }
}

# Configurar el autenticador
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

# Header principal
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
        st.markdown("**Dominios permitidos:** gmail.com, hotmail.com, yahoo.com")
        
        col1, col2 = st.columns(2)
        with col1:
            new_username = st.text_input("Usuario", key="new_username")
            new_name = st.text_input("Nombre completo", key="new_name")
        with col2:
            new_email = st.text_input("Correo electrónico", key="new_email")
            new_password = st.text_input("Contraseña", type="password", key="new_password")
        
        if st.button("Registrarse"):
            if new_username and new_name and new_email and new_password:
                st.success("✅ Usuario registrado exitosamente")
            else:
                st.error("❌ Por favor completa todos los campos")

    with tab_forgot_pwd:
        st.markdown("#### Recuperar Contraseña")
        username = st.text_input("Usuario", key="forgot_pwd_username")
        if st.button("Enviar enlace de recuperación"):
            if username:
                st.info(f"🔑 Se ha enviado un enlace de recuperación para: **{username}**")
            else:
                st.error("❌ Por favor ingresa tu usuario")

    with tab_forgot_user:
        st.markdown("#### Recuperar Usuario")
        email = st.text_input("Correo electrónico", key="forgot_user_email")
        if st.button("Buscar usuario"):
            if email:
                st.info(f"👤 Se ha enviado información del usuario a: **{email}**")
            else:
                st.error("❌ Por favor ingresa tu correo electrónico")

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
        <div class="profile-card">
            <h4>👤 Perfil de Usuario</h4>
            <p><strong>Nombre:</strong> {}</p>
            <p><strong>Usuario:</strong> {}</p>
            <p><strong>Roles:</strong> {}</p>
            <p><strong>Último acceso:</strong> {}</p>
        </div>
        """.format(
            name, username, ", ".join(roles), 
            datetime.now().strftime("%d/%m/%Y %H:%M")
        ), unsafe_allow_html=True)
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state["authentication_status"] = False
            st.rerun()

    # Banner de bienvenida
    st.markdown(f"""
    <div class="welcome-banner">
        <h1>🎉 ¡Bienvenido a ServiSalud, {name}!</h1>
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
        
        st.markdown("#### 🔑 Cambiar Contraseña")
        st.markdown("Actualiza tu contraseña para mantener la seguridad de tu cuenta.")
        
        st.markdown("#### ℹ️ Información de la Cuenta")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **👤 Usuario:** {username}
            **📝 Nombre:** {name}
            **🔐 Roles:** {', '.join(roles)}
            **✅ Estado:** Activo
            **📅 Última actualización:** {datetime.now().strftime("%d/%m/%Y")}
            """)
        
        with col2:
            st.markdown("#### 📊 Estadísticas de Uso")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("📊 Consultas Realizadas", "47")
                st.metric("🗺️ Mapas Visualizados", "23")
            with col_b:
                st.metric("📥 Descargas", "12")
                st.metric("💬 Reportes Enviados", "5")
        
        # Reset password
        st.markdown("#### 🔄 Reset password")
        authenticator.reset_password(username, "Reset password")

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
                'Guasca', 'Guatavita', 'Junín', 'La Palma', 'La Peña', 'La Vega',
                'Machetá', 'Manta', 'Medina', 'Nemocón', 'Nilo', 'Nimaima',
                'Nocaima', 'Pacho', 'Paime', 'Pandi', 'Paratebueno', 'Pasca',
                'Puerto Salgar', 'Pulí', 'Quebradanegra', 'Quetame', 'Quipile',
                'Ricaurte', 'San Antonio del Tequendama', 'San Bernardo',
                'San Cayetano', 'San Francisco', 'San Juan de Río Seco'
            ]
            
            municipios_boyaca = [
                'Tunja', 'Duitama', 'Sogamoso', 'Chiquinquirá', 'Paipa', 'Villa de Leyva',
                'Barbosa', 'Moniquirá', 'Puerto Boyacá', 'Garagoa', 'Málaga', 'Socotá',
                'Aquitania', 'Arcabuco', 'Belén', 'Berbeo', 'Betéitiva', 'Boavita',
                'Boyacá', 'Briceño', 'Buenavista', 'Busbanzá', 'Caldas', 'Campohermoso',
                'Cerinza', 'Chinavita', 'Chiquiza', 'Chiscas', 'Chita', 'Chitaraque',
                'Chivatá', 'Ciénega', 'Cómbita', 'Coper', 'Corrales', 'Covarachía',
                'Cubará', 'Cucaita', 'Cuítiva', 'Chíquiza', 'Chivor', 'Duitama',
                'El Cocuy', 'El Espino', 'Firavitoba', 'Floresta', 'Gachantivá',
                'Gámeza', 'Garagoa', 'Guacamayas', 'Guateque', 'Guayatá', 'Güicán',
                'Iza', 'Jenesano', 'Jericó', 'Labranzagrande', 'La Capilla',
                'La Victoria', 'La Uvita', 'Villa de Leyva', 'Macanal', 'Maripí',
                'Miraflores', 'Mongua', 'Monguí', 'Moniquirá', 'Motavita', 'Muzo',
                'Nobsa', 'Nuevo Colón', 'Oicatá', 'Otanche', 'Pachavita', 'Páez',
                'Paipa', 'Pajarito', 'Panqueba', 'Pauna', 'Paya', 'Paz de Río',
                'Pesca', 'Pisba', 'Puerto Boyacá', 'Quípama', 'Ramiriquí', 'Ráquira',
                'Rondón', 'Saboyá', 'Sáchica', 'Samacá', 'San Eduardo', 'San José de Pare',
                'San Luis de Gaceno', 'San Mateo', 'San Miguel de Sema', 'San Pablo de Borbur',
                'Santana', 'Santa María', 'Santa Rosa de Viterbo', 'Santa Sofía',
                'Sativanorte', 'Sativasur', 'Siachoque', 'Soatá', 'Socotá', 'Sogamoso',
                'Somondoco', 'Sora', 'Sotaquirá', 'Soracá', 'Súsacón', 'Sutamarchán',
                'Sutatenza', 'Tasco', 'Tenza', 'Tibaná', 'Tibasosa', 'Tinjacá',
                'Tipacoque', 'Toca', 'Togüí', 'Tópaga', 'Tota', 'Tunja', 'Tununguá',
                'Turmequé', 'Tuta', 'Tutazá', 'Úmbita', 'Ventaquemada', 'Viracachá',
                'Zetaquira'
            ]
            
            # Combinar municipios
            municipios = municipios_cundinamarca + municipios_boyaca
            
            # Entidades de salud
            entidades = [
                'Hospital Departamental', 'Centro de Salud', 'Puesto de Salud', 
                'Hospital Municipal', 'IPS', 'Clínica', 'Hospital Universitario',
                'Hospital San Rafael', 'Hospital San José', 'Hospital Santa Clara',
                'Hospital San Vicente', 'Hospital San Pedro', 'Hospital San Juan',
                'Centro Médico', 'Consultorio', 'Laboratorio Clínico'
            ]
            
            # Tipos de servicios
            tipos_servicios = [
                'Consulta Externa', 'Urgencias', 'Hospitalización', 'Cirugía',
                'Laboratorio', 'Imágenes Diagnósticas', 'Farmacia', 'Vacunación',
                'Control Prenatal', 'Pediatría', 'Medicina General', 'Especialidades'
            ]
            
            # Generar datos
            data = []
            for i in range(n_samples):
                municipio = np.random.choice(municipios)
                if municipio in municipios_cundinamarca:
                    departamento = 'Cundinamarca'
                else:
                    departamento = 'Boyacá'
                
                # Coordenadas aproximadas según el municipio
                if municipio == 'Bogotá D.C.':
                    lat, lon = 4.6097, -74.0817
                elif municipio == 'Tunja':
                    lat, lon = 5.5403, -73.3614
                elif municipio == 'Duitama':
                    lat, lon = 5.8242, -73.0347
                else:
                    # Coordenadas aproximadas para otros municipios
                    base_lat = 4.5 if departamento == 'Cundinamarca' else 5.5
                    base_lon = -74.0 if departamento == 'Cundinamarca' else -73.0
                    lat = base_lat + np.random.uniform(-0.5, 0.5)
                    lon = base_lon + np.random.uniform(-0.5, 0.5)
                
                data.append({
                    'municipio': municipio,
                    'departamento': departamento,
                    'entidad': np.random.choice(entidades),
                    'tipo_servicio': np.random.choice(tipos_servicios),
                    'latitud': lat,
                    'longitud': lon,
                    'consultas_mes': np.random.randint(10, 500),
                    'capacidad': np.random.randint(50, 1000),
                    'ocupacion': np.random.randint(30, 95),
                    'calidad_atencion': np.random.randint(3, 6),
                    'satisfaccion_usuario': np.random.randint(3, 5),
                    'tiempo_espera': np.random.randint(5, 120),
                    'personal_medico': np.random.randint(2, 50),
                    'personal_enfermeria': np.random.randint(5, 100)
                })
            
            return pd.DataFrame(data)

        # Selección de base de datos
        st.markdown("### 📊 Selección de Base de Datos")
        databases = {
            "9fk3-4e6r": "Datos de Salud Pública Colombia (Principal)",
            "f4c7-t4am": "Datos de Salud Pública Colombia (General)", 
            "sample": "Datos de Muestra (Cundinamarca y Boyacá)"
        }
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_database = st.selectbox(
                "Selecciona la base de datos:",
                options=list(databases.keys()),
                format_func=lambda x: databases[x],
                index=0
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
            
            st.markdown(f"### 📊 Vista General de los Datos")
            
            # Calcular métricas básicas
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
            st.markdown("### 📈 Análisis Visual de Datos")
            
            # Verificar si tenemos datos adecuados para gráficos
            if len(df) > 0:
                # Buscar columnas categóricas para gráficos
                categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
                
                if categorical_cols:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Gráfico de barras para la primera columna categórica
                        first_col = categorical_cols[0]
                        if len(df[first_col].unique()) <= 20:  # Solo si no hay demasiadas categorías
                            fig_bar = px.bar(
                                df[first_col].value_counts().head(10),
                                title=f"Distribución por {first_col}",
                                labels={'index': first_col, 'value': 'Número de Registros'}
                            )
                            st.plotly_chart(fig_bar, use_container_width=True)
                        else:
                            st.info(f"La columna {first_col} tiene demasiadas categorías para mostrar")
                    
                    with col2:
                        # Gráfico de pastel para la segunda columna categórica
                        if len(categorical_cols) > 1:
                            second_col = categorical_cols[1]
                            if len(df[second_col].unique()) <= 10:  # Solo si no hay demasiadas categorías
                                fig_pie = px.pie(
                                    df[second_col].value_counts(),
                                    title=f"Distribución por {second_col}",
                                    names=df[second_col].value_counts().index
                                )
                                st.plotly_chart(fig_pie, use_container_width=True)
                            else:
                                st.info(f"La columna {second_col} tiene demasiadas categorías para mostrar")
                        else:
                            st.info("No hay suficientes columnas categóricas para el gráfico de pastel")
                else:
                    st.info("Los datos cargados no contienen columnas categóricas adecuadas para gráficos")
            
            # Tabla de datos
            st.markdown("### 📋 Datos")
            st.dataframe(df_filtered.head(100))
    
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
            consultas_respiratorias = 50 + seasonal_pattern + rain_effect + noise
            consultas_generales = 60 + trend + noise * 0.5
            demanda_vacunacion = 80 + seasonal_pattern * 0.5 + noise * 0.3
            
            # Crear DataFrame temporal
            temporal_df = pd.DataFrame({
                'fecha': dates,
                'consultas_respiratorias': consultas_respiratorias,
                'consultas_generales': consultas_generales,
                'demanda_vacunacion': demanda_vacunacion
            })
            
            # Gráfico de evolución temporal
            st.markdown("#### 📅 Evolución de la Demanda de Servicios de Salud")
            fig_temporal = go.Figure()
            
            fig_temporal.add_trace(go.Scatter(
                x=temporal_df['fecha'],
                y=temporal_df['consultas_respiratorias'],
                mode='lines',
                name='Consultas Respiratorias',
                line=dict(color='red', width=2)
            ))
            
            fig_temporal.add_trace(go.Scatter(
                x=temporal_df['fecha'],
                y=temporal_df['consultas_generales'],
                mode='lines',
                name='Consultas Generales',
                line=dict(color='green', width=2)
            ))
            
            fig_temporal.add_trace(go.Scatter(
                x=temporal_df['fecha'],
                y=temporal_df['demanda_vacunacion'],
                mode='lines',
                name='Demanda Vacunación',
                line=dict(color='blue', width=2)
            ))
            
            fig_temporal.update_layout(
                title="Evolución Temporal de la Demanda",
                xaxis_title="Fecha",
                yaxis_title="Número de Consultas Diarias",
                hovermode='x unified',
                template='plotly_white'
            )
            
            st.plotly_chart(fig_temporal, use_container_width=True)
            
            # Interpretación de los ejes
            st.markdown("#### 📊 Interpretación de los Ejes")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info("**Eje X (Horizontal):** Fecha - Muestra la evolución temporal día a día")
            
            with col2:
                st.info("**Eje Y (Vertical):** Número de Consultas - Cantidad de demanda diaria por tipo de servicio")
            
            with col3:
                st.info("**Líneas:** Cada color representa un tipo diferente de consulta médica")
            
            # Distribución de la demanda
            st.markdown("#### 📊 Distribución de la Demanda")
            col1, col2 = st.columns(2)
            
            with col1:
                # Histograma de consultas respiratorias
                fig_hist1 = px.histogram(
                    temporal_df, 
                    x='consultas_respiratorias',
                    title="Distribución de Consultas Respiratorias",
                    labels={'consultas_respiratorias': 'Número de Consultas', 'count': 'Frecuencia'}
                )
                st.plotly_chart(fig_hist1, use_container_width=True)
            
            with col2:
                # Histograma de consultas generales
                fig_hist2 = px.histogram(
                    temporal_df, 
                    x='consultas_generales',
                    title="Distribución de Consultas Generales",
                    labels={'consultas_generales': 'Número de Consultas', 'count': 'Frecuencia'}
                )
                st.plotly_chart(fig_hist2, use_container_width=True)
        else:
            st.info("📊 Carga datos en el Dashboard de Salud Pública para ver análisis de patrones")

    with community_tab:
        st.markdown("""
        <div class="info-box">
            <h2>👥 Participación Comunitaria</h2>
            <p>Formularios para recopilar información de la comunidad y mejorar los servicios</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Pestañas para diferentes tipos de formularios
        tab_symptoms, tab_availability, tab_comments = st.tabs([
            "🤒 Síntomas Frecuentes", "📅 Disponibilidad", "💬 Comentarios"
        ])
        
        with tab_symptoms:
            st.markdown("### 🤒 Reporte de Síntomas Frecuentes en tu Zona")
            
            with st.form("symptom_report"):
                st.markdown("#### 📍 Información de Ubicación")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    departamento = st.selectbox(
                        "Departamento",
                        ["Cundinamarca", "Boyacá"],
                        key="symptom_dept"
                    )
                
                with col2:
                    municipio = st.text_input(
                        "Municipio",
                        placeholder="Ej: Bogotá, Tunja, Soacha...",
                        key="symptom_municipio"
                    )
                
                with col3:
                    barrio = st.text_input(
                        "Barrio/Localidad",
                        placeholder="Ej: Centro, Norte, Sur...",
                        key="symptom_barrio"
                    )
                
                st.markdown("#### 🤒 Síntomas Observados")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    sintomas = st.multiselect(
                        "Síntomas más frecuentes en tu zona",
                        ["Fiebre", "Tos", "Dolor de cabeza", "Dolor de garganta", 
                         "Congestión nasal", "Fatiga", "Dolor muscular", "Náuseas",
                         "Diarrea", "Dolor abdominal", "Dificultad respiratoria"],
                        key="symptom_sintomas"
                    )
                
                with col2:
                    frecuencia = st.selectbox(
                        "Frecuencia observada",
                        ["Muy frecuente", "Frecuente", "Moderada", "Poco frecuente"],
                        key="symptom_frecuencia"
                    )
                
                with col3:
                    grupo_edad = st.selectbox(
                        "Grupo de edad más afectado",
                        ["Niños (0-12 años)", "Adolescentes (13-17 años)", 
                         "Adultos jóvenes (18-35 años)", "Adultos (36-65 años)", 
                         "Adultos mayores (65+ años)"],
                        key="symptom_edad"
                    )
                
                st.markdown("#### 📝 Información Adicional")
                info_adicional = st.text_area(
                    "Información adicional sobre síntomas o condiciones en tu zona:",
                    placeholder="Describe cualquier patrón que hayas notado, fechas específicas, etc.",
                    key="symptom_info"
                )
                
                submitted = st.form_submit_button("📤 Enviar Reporte de Síntomas", type="primary")
                
                if submitted:
                    st.success("✅ Reporte de síntomas enviado exitosamente")
                    st.markdown("#### 📋 Información enviada:")
                    st.markdown(f"- **Departamento:** {departamento}")
                    st.markdown(f"- **Municipio:** {municipio}")
                    st.markdown(f"- **Síntomas:** {', '.join(sintomas) if sintomas else 'No especificados'}")
                    st.markdown(f"- **Frecuencia:** {frecuencia}")
                    st.markdown(f"- **Grupo de edad más afectado:** {grupo_edad}")
        
        with tab_availability:
            st.markdown("### 📅 Disponibilidad para Campañas de Salud")
            
            with st.form("availability_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 👤 Información Personal")
                    nombre_completo = st.text_input(
                        "Nombre completo:",
                        placeholder="Tu nombre completo",
                        key="avail_nombre"
                    )
                    
                    telefono = st.text_input(
                        "Teléfono de contacto:",
                        placeholder="Ej: 300-123-4567",
                        key="avail_telefono"
                    )
                    
                    email = st.text_input(
                        "Correo electrónico:",
                        placeholder="tu@email.com",
                        key="avail_email"
                    )
                    
                    profesion = st.selectbox(
                        "Profesión/Área de trabajo:",
                        ["Médico", "Enfermero", "Técnico en salud", "Voluntario", "Estudiante", "Otro"],
                        key="avail_profesion"
                    )
                
                with col2:
                    st.markdown("#### 📅 Disponibilidad")
                    dias_disponibles = st.multiselect(
                        "Días de la semana disponibles:",
                        ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
                        key="avail_dias"
                    )
                    
                    horario = st.selectbox(
                        "Horario preferido:",
                        ["Mañana (6:00 AM - 12:00 PM)", "Tarde (12:00 PM - 6:00 PM)", 
                         "Noche (6:00 PM - 10:00 PM)", "Todo el día", "Fines de semana"],
                        key="avail_horario"
                    )
                    
                    tipo_campanas = st.multiselect(
                        "Tipo de campañas de interés:",
                        ["Vacunación", "Prevención de enfermedades", "Educación sanitaria", 
                         "Tamizaje médico", "Campañas de donación", "Emergencias"],
                        key="avail_campanas"
                    )
                    
                    experiencia = st.selectbox(
                        "Experiencia en campañas de salud:",
                        ["Sin experiencia", "1-2 campañas", "3-5 campañas", "Más de 5 campañas"],
                        key="avail_experiencia"
                    )
                
                st.markdown("#### 💬 Comentarios Adicionales")
                comentarios = st.text_area(
                    "Comentarios sobre tu disponibilidad o habilidades especiales:",
                    placeholder="Menciona cualquier habilidad especial, idiomas, disponibilidad especial, etc.",
                    key="avail_comentarios"
                )
                
                submitted = st.form_submit_button("📤 Enviar Disponibilidad", type="primary")
                
                if submitted:
                    st.success("✅ Información de disponibilidad enviada exitosamente")
        
        with tab_comments:
            st.markdown("### 💬 Comentarios y Sugerencias")
            
            st.markdown("#### 💭 Tu Opinión es Importante")
            
            with st.form("comments_form"):
                tipo_comentario = st.selectbox(
                    "Tipo de comentario:",
                    ["Sugerencia de mejora", "Reporte de problema", "Elogio", "Consulta general"],
                    key="comment_tipo"
                )
                
                calificacion = st.slider(
                    "Calificación general del servicio:",
                    min_value=1, max_value=5, value=4,
                    format="⭐ %d",
                    key="comment_calificacion"
                )
                
                comentario_texto = st.text_area(
                    "Describe tu comentario o sugerencia:",
                    placeholder="Sé específico y detallado para ayudarnos a mejorar...",
                    key="comment_texto"
                )
                
                contacto = st.radio(
                    "¿Te gustaría que te contactemos?",
                    ["Sí, por correo electrónico", "Sí, por teléfono", "No, es solo un comentario"],
                    key="comment_contacto"
                )
                
                if contacto != "No, es solo un comentario":
                    info_contacto = st.text_input(
                        "Información de contacto:",
                        placeholder="Correo o teléfono",
                        key="comment_info_contacto"
                    )
                
                submitted = st.form_submit_button("📤 Enviar Comentario", type="primary")
                
                if submitted:
                    st.success("✅ Comentario enviado exitosamente")
                    st.balloons()

# La aplicación Streamlit se ejecuta automáticamente
