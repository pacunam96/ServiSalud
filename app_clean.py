import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from sodapy import Socrata
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

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

# Si no está autenticado, mostrar pestañas de acceso
if not st.session_state.get("authentication_status"):
    tab_login, tab_register, tab_forgot_pwd, tab_forgot_user = st.tabs([
        "Iniciar sesión", "Registrarse", "Olvidé mi contraseña", "Olvidé mi usuario"
    ])

    with tab_login:
        authenticator.login(location="main", key="Login", clear_on_submit=False)

    with tab_register:
        st.caption("Use un email de dominio permitido: " + ", ".join(ALLOWED_DOMAINS))
        st.info(
            "Requisitos de contraseña: 8-20 caracteres, 1 minúscula, 1 mayúscula, "
            "1 caracter especial (@$!%*?&). Ejemplo: Abcd@1234"
        )
        selected_roles = st.multiselect("Roles", options=AVAILABLE_ROLES, default=["paciente"])
        email, new_username, full_name = authenticator.register_user(
            location="main",
            captcha=False,
            key="Register user",
            domains=ALLOWED_DOMAINS,
            roles=selected_roles,
            merge_username_email=True,
        )
        if email and new_username and full_name:
            st.success("Usuario registrado correctamente. Ahora puede iniciar sesión.")

    with tab_forgot_pwd:
        username, email, new_password = authenticator.forgot_password(
            location="main",
            captcha=False,
            key="Forgot password",
        )
        if username and email and new_password:
            st.info("Se ha generado una nueva contraseña temporal. Revise su correo o úsela para entrar.")

    with tab_forgot_user:
        username, email = authenticator.forgot_username(
            location="main",
            captcha=False,
            key="Forgot username",
        )
        if username and email:
            st.info(f"Su usuario es: {username}")

# Lee el estado de autenticación desde la sesión
authentication_status = st.session_state.get("authentication_status")
name = st.session_state.get("name")
username = st.session_state.get("username")
roles = st.session_state.get("roles")

# Si está autenticado, mostrar contenido y opciones de cuenta
if authentication_status:
    st.success(f"Bienvenido {name}")
    if roles:
        st.write("Roles asignados:", roles)

    # Pestañas para usuarios autenticados
    acct_tab, health_tab = st.tabs(["Cuenta", "Base de Datos de Salud"])
    
    with acct_tab:
        st.subheader("Restablecer contraseña")
        reset_ok = authenticator.reset_password(
            username=username,
            location="main",
            key="Reset password",
        )
        if reset_ok:
            st.success("Contraseña actualizada correctamente.")
    
    with health_tab:
        st.subheader("🏥 Dashboard de Salud Pública Colombia")
        st.caption("Fuente: datos.gov.co (Socrata) - Dashboard Interactivo")
        
        # Función para crear datos de muestra si falla la API
        def create_sample_data():
            """Crear datos de muestra para demostración"""
            np.random.seed(42)
            n_samples = 150
            
            # Crear datos de muestra realistas
            departamentos = ['Bogotá D.C.', 'Antioquia', 'Valle del Cauca', 'Atlántico', 'Santander', 
                           'Bolívar', 'Cundinamarca', 'Nariño', 'Córdoba', 'Boyacá']
            municipios = ['Bogotá', 'Medellín', 'Cali', 'Barranquilla', 'Cartagena', 'Bucaramanga',
                         'Pereira', 'Santa Marta', 'Ibagué', 'Pasto', 'Manizales', 'Neiva']
            tipos_servicio = ['Consulta Externa', 'Urgencias', 'Hospitalización', 'Cirugía', 
                            'Laboratorio', 'Rayos X', 'Farmacia', 'Vacunación']
            entidades = ['Hospital Central', 'Centro de Salud', 'Clínica', 'IPS', 'Puesto de Salud']
            
            sample_data = {
                'departamento': np.random.choice(departamentos, n_samples),
                'municipio': np.random.choice(municipios, n_samples),
                'tipo_servicio': np.random.choice(tipos_servicio, n_samples),
                'entidad': np.random.choice(entidades, n_samples),
                'direccion': [f"Calle {np.random.randint(1, 200)} # {np.random.randint(1, 100)}-{np.random.randint(1, 99)}" 
                             for _ in range(n_samples)],
                'telefono': [f"300-{np.random.randint(100, 999)}-{np.random.randint(1000, 9999)}" 
                           for _ in range(n_samples)],
                'capacidad_atencion': np.random.randint(10, 500, n_samples),
                'pacientes_mes': np.random.randint(50, 2000, n_samples),
                'latitud': np.random.uniform(4.0, 12.5, n_samples),  # Colombia
                'longitud': np.random.uniform(-81.0, -66.9, n_samples),  # Colombia
                'estado': np.random.choice(['Activo', 'En mantenimiento', 'Temporalmente cerrado'], n_samples, p=[0.8, 0.15, 0.05]),
                'fecha_registro': pd.date_range('2023-01-01', '2024-01-01', periods=n_samples)
            }
            
            return pd.DataFrame(sample_data)
        
        # Cargar datos
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write("**Selecciona una fuente de datos:**")
            data_source = st.radio(
                "Fuente de datos:",
                ["🌐 Datos en vivo (API)", "📊 Datos de muestra (Demo)"],
                horizontal=True
            )
        
        with col2:
            if st.button("🔄 Cargar Datos", type="primary"):
                with st.spinner("Cargando datos..."):
                    if data_source == "🌐 Datos en vivo (API)":
                        try:
                            # Intentar cargar datos reales
                            client = Socrata("www.datos.gov.co", None)
                            results = client.get("f4c7-t4am", limit=500)
                            df = pd.DataFrame.from_records(results)
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
                    else:
                        df = create_sample_data()
                        st.session_state['health_data'] = df
                        st.session_state['data_source'] = 'sample'
                        st.success(f"✅ Datos de muestra cargados: {len(df)} registros")
        
        # Mostrar dashboard si hay datos
        if 'health_data' in st.session_state:
            df = st.session_state['health_data']
            data_source = st.session_state.get('data_source', 'unknown')
            
            # Información del dataset
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Total Registros", len(df))
            with col2:
                st.metric("🏥 Entidades", df['entidad'].nunique() if 'entidad' in df.columns else len(df))
            with col3:
                st.metric("📍 Ubicaciones", df['municipio'].nunique() if 'municipio' in df.columns else len(df))
            with col4:
                source_icon = "🌐" if data_source == 'real' else "📊"
                st.metric("Fuente", f"{source_icon} {'Real' if data_source == 'real' else 'Muestra'}")
            
            # Dashboard unificado - Todo en una vista
            st.markdown("---")
            st.subheader("📊 Dashboard Interactivo de Salud Pública")
            
            # Filtros principales
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if 'departamento' in df.columns:
                    departamento_selected = st.multiselect(
                        "Seleccionar Departamentos:",
                        options=df['departamento'].unique(),
                        default=df['departamento'].unique()[:3]
                    )
                    df_filtered = df[df['departamento'].isin(departamento_selected)]
                else:
                    df_filtered = df
            
            with col2:
                if 'tipo_servicio' in df.columns:
                    tipo_selected = st.multiselect(
                        "Seleccionar Tipos de Servicio:",
                        options=df['tipo_servicio'].unique(),
                        default=df['tipo_servicio'].unique()[:4]
                    )
                    df_filtered = df_filtered[df_filtered['tipo_servicio'].isin(tipo_selected)]
            
            with col3:
                if 'estado' in df.columns:
                    estado_selected = st.multiselect(
                        "Seleccionar Estado:",
                        options=df['estado'].unique(),
                        default=['Activo']
                    )
                    df_filtered = df_filtered[df_filtered['estado'].isin(estado_selected)]
            
            # Métricas principales
            st.markdown("### 📈 Métricas Principales")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_servicios = len(df_filtered)
                st.metric("🏥 Total Servicios", total_servicios)
            
            with col2:
                if 'pacientes_mes' in df_filtered.columns:
                    total_pacientes = df_filtered['pacientes_mes'].sum()
                    st.metric("👥 Pacientes/Mes", f"{total_pacientes:,}")
                else:
                    st.metric("👥 Entidades", df_filtered['entidad'].nunique() if 'entidad' in df_filtered.columns else total_servicios)
            
            with col3:
                if 'capacidad_atencion' in df_filtered.columns:
                    capacidad_total = df_filtered['capacidad_atencion'].sum()
                    st.metric("🛏️ Capacidad Total", f"{capacidad_total:,}")
                else:
                    ubicaciones = df_filtered['municipio'].nunique() if 'municipio' in df_filtered.columns else total_servicios
                    st.metric("📍 Ubicaciones", ubicaciones)
            
            with col4:
                if 'fecha_registro' in df_filtered.columns:
                    ultima_fecha = df_filtered['fecha_registro'].max()
                    st.metric("📅 Última Actualización", ultima_fecha.strftime('%d/%m/%Y') if pd.notna(ultima_fecha) else 'N/A')
                else:
                    st.metric("📊 Datos Cargados", len(df))
            
            # Gráficos principales
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🏥 Distribución por Departamento")
                if 'departamento' in df_filtered.columns:
                    dept_counts = df_filtered['departamento'].value_counts()
                    fig_dept = px.bar(
                        x=dept_counts.values,
                        y=dept_counts.index,
                        orientation='h',
                        title="Servicios por Departamento",
                        labels={'x': 'Número de Servicios', 'y': 'Departamento'},
                        color=dept_counts.values,
                        color_continuous_scale="Blues"
                    )
                    fig_dept.update_layout(height=400, title_x=0.5)
                    st.plotly_chart(fig_dept, use_container_width=True)
                else:
                    st.info("No hay datos de departamentos disponibles")
            
            with col2:
                st.markdown("### 🩺 Tipos de Servicios")
                if 'tipo_servicio' in df_filtered.columns:
                    servicio_counts = df_filtered['tipo_servicio'].value_counts()
                    fig_servicio = px.pie(
                        values=servicio_counts.values,
                        names=servicio_counts.index,
                        title="Distribución de Servicios",
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig_servicio.update_traces(textposition='inside', textinfo='percent+label')
                    fig_servicio.update_layout(height=400, title_x=0.5)
                    st.plotly_chart(fig_servicio, use_container_width=True)
                else:
                    st.info("No hay datos de tipos de servicio disponibles")
            
            # Mapa geográfico
            st.markdown("### 🗺️ Mapa de Distribución Geográfica")
            
            if 'latitud' in df_filtered.columns and 'longitud' in df_filtered.columns:
                # Filtrar coordenadas válidas
                df_map = df_filtered.dropna(subset=['latitud', 'longitud'])
                df_map = df_map[
                    (df_map['latitud'] >= 4.0) & (df_map['latitud'] <= 12.5) &
                    (df_map['longitud'] >= -81.0) & (df_map['longitud'] <= -66.9)
                ]
                
                if len(df_map) > 0:
                    # Mapa de dispersión
                    fig_map = px.scatter_mapbox(
                        df_map,
                        lat='latitud',
                        lon='longitud',
                        hover_name='municipio' if 'municipio' in df_map.columns else 'entidad',
                        hover_data=['tipo_servicio', 'estado'] if 'tipo_servicio' in df_map.columns else ['estado'],
                        color='tipo_servicio' if 'tipo_servicio' in df_map.columns else None,
                        zoom=5,
                        height=500,
                        title="Distribución Geográfica de Servicios de Salud"
                    )
                    
                    fig_map.update_layout(
                        mapbox_style="open-street-map",
                        margin={"r": 0, "t": 50, "l": 0, "b": 0},
                        title_x=0.5
                    )
                    
                    st.plotly_chart(fig_map, use_container_width=True)
                    
                    # Estadísticas del mapa
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📍 Puntos Mapeados", len(df_map))
                    with col2:
                        st.metric("📊 Cobertura", f"{len(df_map)/len(df_filtered)*100:.1f}%")
                    with col3:
                        st.metric("🗺️ Regiones", df_map['municipio'].nunique() if 'municipio' in df_map.columns else len(df_map))
                else:
                    st.warning("No se encontraron coordenadas válidas para el mapeo")
            else:
                st.info("No hay datos de coordenadas disponibles para el mapeo")
            
            # Tabla de datos
            st.markdown("### 📋 Datos Detallados")
            
            # Mostrar solo columnas relevantes
            display_cols = []
            for col in ['municipio', 'departamento', 'tipo_servicio', 'entidad', 'estado', 'telefono']:
                if col in df_filtered.columns:
                    display_cols.append(col)
            
            if display_cols:
                st.dataframe(
                    df_filtered[display_cols].head(20),
                    use_container_width=True,
                    height=400
                )
                
                # Botón de descarga
                csv = df_filtered[display_cols].to_csv(index=False)
                st.download_button(
                    label="📥 Descargar datos filtrados",
                    data=csv,
                    file_name="datos_salud_filtrados.csv",
                    mime="text/csv"
                )
            else:
                st.dataframe(df_filtered.head(20), use_container_width=True, height=400)

    authenticator.logout(button_name="Logout", location="sidebar", key="Logout")
elif authentication_status is False:
    st.error("Usuario/contraseña incorrectos")
else:
    st.warning("Por favor ingrese sus credenciales")
