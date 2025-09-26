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
        st.subheader("Bases de Datos de Salud de Colombia")
        st.caption("Fuente: datos.gov.co (Socrata)")
        
        # Selector de dataset
        datasets = {
            "i3fe-nzem": "Dataset de Salud 1",
            "fm7q-3ytn": "Dataset de Salud 2", 
            "y42m-qq7z": "Dataset de Salud 3",
            "f4c7-t4am": "Dataset de Salud 4",
            "tz38-fg9k": "Dataset de Salud 5",
            "x395-2tbn": "Dataset de Salud 6"
        }
        
        selected_dataset = st.selectbox(
            "Selecciona una base de datos:",
            options=list(datasets.keys()),
            format_func=lambda x: datasets[x],
            key="dataset_selector"
        )
        
        # Botón para cargar datos
        if st.button("Cargar Datos de Salud", key="load_health_data"):
            with st.spinner(f"Cargando {datasets[selected_dataset]}..."):
                try:
                    # Cliente Socrata sin autenticación para datasets públicos
                    client = Socrata("www.datos.gov.co", None)
                    # Obtener datos (primeros 2000 registros)
                    results = client.get(selected_dataset, limit=2000)
                    # Convertir a DataFrame
                    results_df = pd.DataFrame.from_records(results)
                    
                    # Guardar en session state para evitar recargas
                    st.session_state['health_data'] = results_df
                    st.session_state['selected_dataset'] = selected_dataset
                    
                    st.success(f"✅ {datasets[selected_dataset]} cargado exitosamente: {len(results_df)} registros")
                    
                except Exception as e:
                    st.error(f"❌ Error al cargar datos: {str(e)}")
        
        # Mostrar datos si están disponibles
        if 'health_data' in st.session_state and not st.session_state['health_data'].empty:
            df = st.session_state['health_data']
            
            # Dashboard principal con pestañas
            tab_data, tab_availability, tab_prediction, tab_community = st.tabs([
                "📊 Datos", "🏥 Disponibilidad", "📈 Predicción", "👥 Comunidad"
            ])
            
            with tab_data:
                st.subheader("Vista de Datos")
                
                # Mostrar información básica
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Registros", len(df))
                with col2:
                    st.metric("Columnas", len(df.columns))
                with col3:
                    st.metric("Memoria", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
                
                # Mostrar columnas disponibles
                st.subheader("Columnas Disponibles")
                st.write(df.columns.tolist())
                
                # Filtros básicos
                st.subheader("Filtros")
                if len(df) > 0:
                    # Mostrar primeras filas
                    st.subheader("Primeras 10 filas")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    # Búsqueda en datos
                    search_term = st.text_input("Buscar en datos", placeholder="Ingrese término de búsqueda")
                    if search_term:
                        # Buscar en todas las columnas de texto
                        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
                        filtered_df = df[mask]
                        st.write(f"Resultados encontrados: {len(filtered_df)}")
                        if len(filtered_df) > 0:
                            st.dataframe(filtered_df.head(20), use_container_width=True)
                
                # Descargar datos
                csv = df.to_csv(index=False)
                dataset_name = st.session_state.get('selected_dataset', 'datos_salud')
                st.download_button(
                    label="📥 Descargar datos como CSV",
                    data=csv,
                    file_name=f"{dataset_name}_colombia.csv",
                    mime="text/csv"
                )
            
            with tab_availability:
                st.subheader("🏥 Disponibilidad de Servicios de Salud")
                
                # Análisis de disponibilidad
                st.write("### Mapeo de Servicios de Salud")
                
                # Buscar columnas relacionadas con ubicación
                location_cols = [col for col in df.columns if any(word in col.lower() for word in ['ubicacion', 'direccion', 'municipio', 'departamento', 'ciudad', 'lat', 'lon', 'coordenada'])]
                
                if location_cols:
                    st.write(f"**Columnas de ubicación encontradas:** {location_cols}")
                    
                    # Gráfico de barras por ubicación
                    if len(location_cols) > 0:
                        location_col = st.selectbox("Selecciona columna de ubicación:", location_cols)
                        location_counts = df[location_col].value_counts().head(20)
                        
                        fig = px.bar(
                            x=location_counts.values, 
                            y=location_counts.index,
                            orientation='h',
                            title=f"Servicios por {location_col}",
                            labels={'x': 'Número de Servicios', 'y': location_col}
                        )
                        fig.update_layout(height=600)
                        st.plotly_chart(fig, use_container_width=True)
                
                # Análisis de tipos de servicios
                service_cols = [col for col in df.columns if any(word in col.lower() for word in ['tipo', 'servicio', 'categoria', 'especialidad', 'modalidad'])]
                
                if service_cols:
                    st.write("### Tipos de Servicios Disponibles")
                    service_col = st.selectbox("Selecciona columna de tipo de servicio:", service_cols)
                    service_counts = df[service_col].value_counts()
                    
                    fig = px.pie(
                        values=service_counts.values,
                        names=service_counts.index,
                        title=f"Distribución de {service_col}"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Resumen de disponibilidad
                st.write("### Resumen de Disponibilidad")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Servicios", len(df))
                with col2:
                    st.metric("Ubicaciones Únicas", df[location_cols[0]].nunique() if location_cols else "N/A")
                with col3:
                    st.metric("Tipos de Servicio", df[service_cols[0]].nunique() if service_cols else "N/A")
            
            with tab_prediction:
                st.subheader("📈 Predicción de Demanda")
                
                # Análisis temporal si hay fechas
                date_cols = [col for col in df.columns if any(word in col.lower() for word in ['fecha', 'date', 'año', 'mes', 'dia', 'tiempo'])]
                
                if date_cols:
                    st.write("### Análisis Temporal de Demanda")
                    date_col = st.selectbox("Selecciona columna de fecha:", date_cols)
                    
                    try:
                        # Convertir a datetime
                        df_temp = df.copy()
                        df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
                        df_temp = df_temp.dropna(subset=[date_col])
                        
                        # Agrupar por mes
                        df_temp['mes'] = df_temp[date_col].dt.to_period('M')
                        monthly_counts = df_temp.groupby('mes').size().reset_index(name='demanda')
                        
                        # Gráfico de tendencia
                        fig = px.line(
                            monthly_counts, 
                            x='mes', 
                            y='demanda',
                            title="Tendencia de Demanda Mensual",
                            labels={'demanda': 'Número de Consultas', 'mes': 'Mes'}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Predicción simple (promedio móvil)
                        if len(monthly_counts) > 3:
                            st.write("### Predicción Simple (Promedio Móvil)")
                            monthly_counts['prediccion'] = monthly_counts['demanda'].rolling(window=3, min_periods=1).mean()
                            
                            fig_pred = go.Figure()
                            fig_pred.add_trace(go.Scatter(x=monthly_counts['mes'], y=monthly_counts['demanda'], 
                                                        name='Datos Reales', mode='lines+markers'))
                            fig_pred.add_trace(go.Scatter(x=monthly_counts['mes'], y=monthly_counts['prediccion'], 
                                                        name='Predicción', mode='lines+markers', line=dict(dash='dash')))
                            fig_pred.update_layout(title="Demanda Real vs Predicción", 
                                                 xaxis_title="Mes", yaxis_title="Demanda")
                            st.plotly_chart(fig_pred, use_container_width=True)
                    
                    except Exception as e:
                        st.warning(f"No se pudo procesar la columna de fecha: {e}")
                
                # Análisis estacional
                st.write("### Análisis Estacional")
                if date_cols:
                    try:
                        df_temp = df.copy()
                        df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
                        df_temp = df_temp.dropna(subset=[date_col])
                        df_temp['mes_num'] = df_temp[date_col].dt.month
                        df_temp['estacion'] = df_temp['mes_num'].map({
                            12: 'Invierno', 1: 'Invierno', 2: 'Invierno',
                            3: 'Primavera', 4: 'Primavera', 5: 'Primavera',
                            6: 'Verano', 7: 'Verano', 8: 'Verano',
                            9: 'Otoño', 10: 'Otoño', 11: 'Otoño'
                        })
                        
                        seasonal_counts = df_temp['estacion'].value_counts()
                        fig_seasonal = px.bar(
                            x=seasonal_counts.index,
                            y=seasonal_counts.values,
                            title="Demanda por Estación del Año",
                            labels={'x': 'Estación', 'y': 'Número de Consultas'}
                        )
                        st.plotly_chart(fig_seasonal, use_container_width=True)
                    except:
                        st.info("No se pudo generar análisis estacional")
            
            with tab_community:
                st.subheader("👥 Dashboard para la Comunidad")
                
                # Métricas clave para la comunidad
                st.write("### Información General para la Comunidad")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏥 Servicios Disponibles", len(df))
                with col2:
                    st.metric("📍 Ubicaciones", df[location_cols[0]].nunique() if location_cols else "N/A")
                with col3:
                    st.metric("🩺 Tipos de Servicio", df[service_cols[0]].nunique() if service_cols else "N/A")
                with col4:
                    st.metric("📅 Última Actualización", datetime.now().strftime("%d/%m/%Y"))
                
                # Gráfico de distribución geográfica
                if location_cols:
                    st.write("### Distribución Geográfica de Servicios")
                    location_col = st.selectbox("Selecciona ubicación para el mapa:", location_cols, key="community_location")
                    location_summary = df[location_col].value_counts().head(10)
                    
                    fig_map = px.bar(
                        x=location_summary.values,
                        y=location_summary.index,
                        orientation='h',
                        title=f"Top 10 {location_col} con más servicios",
                        labels={'x': 'Número de Servicios', 'y': location_col}
                    )
                    fig_map.update_layout(height=500)
                    st.plotly_chart(fig_map, use_container_width=True)
                
                # Información para jornadas de salud
                st.write("### 📋 Información para Jornadas de Salud")
                
                # Simular datos de jornadas (basado en los datos reales)
                if len(df) > 0:
                    # Estimación de pacientes atendidos
                    estimated_patients = len(df) * np.random.randint(10, 50)  # Simulación
                    st.metric("👥 Pacientes Estimados Atendidos", f"{estimated_patients:,}")
                    
                    # Recursos proyectados
                    st.write("#### Recursos Básicos Proyectados:")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("💉 Vacunas Disponibles", f"{estimated_patients * 1.2:,.0f}")
                    with col2:
                        st.metric("🩹 Material Médico", f"{estimated_patients * 0.8:,.0f}")
                    with col3:
                        st.metric("👨‍⚕️ Personal Requerido", f"{len(df) * 2:,.0f}")
                
                # Calendario de próximas actividades
                st.write("### 📅 Próximas Actividades de Salud")
                
                # Simular fechas de próximas jornadas
                today = datetime.now()
                upcoming_dates = [today + timedelta(days=i*7) for i in range(1, 5)]
                
                for i, date in enumerate(upcoming_dates):
                    with st.expander(f"Jornada de Salud - {date.strftime('%d/%m/%Y')}"):
                        st.write(f"**Ubicación:** {location_cols[0] if location_cols else 'Por definir'}")
                        st.write(f"**Servicios:** Consulta general, vacunación, medicina preventiva")
                        st.write(f"**Horario:** 8:00 AM - 4:00 PM")
                        st.write(f"**Capacidad estimada:** {np.random.randint(50, 200)} personas")
                
                # Información de contacto
                st.write("### 📞 Información de Contacto")
                st.info("""
                **Para más información sobre servicios de salud:**
                - 📞 Línea de atención: 123
                - 🌐 Portal web: www.salud.gov.co
                - 📧 Email: salud@colombia.gov.co
                - 📱 WhatsApp: +57 300 123 4567
                """)

    authenticator.logout(button_name="Logout", location="sidebar", key="Logout")
elif authentication_status is False:
    st.error("Usuario/contraseña incorrectos")
else:
    st.warning("Por favor ingrese sus credenciales")