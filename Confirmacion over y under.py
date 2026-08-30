import streamlit as st
import math

# Configuración de la página
st.set_page_config(page_title="Auditoría Under/Over & Dixon-Coles", layout="centered")
st.title("🔎 Auditoría Independiente: Under/Over & Dixon-Coles")
st.caption("Herramienta consultiva para verificar probabilidades de Poisson sin modificar tu modelo principal.")

# --------------------------------------------------------------
# FUNCIONES MATEMÁTICAS
# --------------------------------------------------------------

def poisson_pmf(k, lam):
    """P(X = k) para X ~ Poisson(lam)"""
    return math.exp(-lam) * (lam ** k) / math.factorial(k)

def dixon_coles_tau(i, j, lam_h, lam_a, rho=0.0):
    if i == 0 and j == 0:
        return 1 - (lam_h * lam_a * rho)
    elif i == 0 and j == 1:
        return 1 + (lam_h * rho)
    elif i == 1 and j == 0:
        return 1 + (lam_a * rho)
    elif i == 1 and j == 1:
        return 1 - rho
    else:
        return 1.0

def score_matrix(lam_h, lam_a, max_goals=10, rho=0.0):
    grid = {}
    total_prob = 0.0
    for i in range(max_goals):
        for j in range(max_goals):
            p = poisson_pmf(i, lam_h) * poisson_pmf(j, lam_a)
            p *= dixon_coles_tau(i, j, lam_h, lam_a, rho)
            grid[(i, j)] = p
            total_prob += p
    return grid, total_prob

def under_over(lam_h, lam_a, line=2.5, rho=0.0, max_goals=10):
    grid, total_prob = score_matrix(lam_h, lam_a, max_goals, rho)
    under = sum(p for (i, j), p in grid.items() if i + j < line)
    over = sum(p for (i, j), p in grid.items() if i + j > line)
    return {
        "lambda_total": lam_h + lam_a,
        "under": under,
        "over": over,
        "suma_probabilidades": total_prob,
        "grid": grid,
    }

def under_over_simple(lam_h, lam_a, line=2.5):
    lam_total = lam_h + lam_a
    k_max = int(line)
    under = sum(poisson_pmf(k, lam_total) for k in range(k_max + 1))
    over = 1 - under
    return {"lambda_total": lam_total, "under": under, "over": over}


# --------------------------------------------------------------
# INTERFAZ DE USUARIO (STREAMLIT)
# --------------------------------------------------------------

with st.form("form_auditoria"):
    st.subheader("Parámetros del Partido")
    
    col1, col2 = st.columns(2)
    with col1:
        lam_local = st.number_input("Lambda (λ) Local", min_value=0.1, value=1.50, step=0.01)
    with col2:
        lam_visitante = st.number_input("Lambda (λ) Visitante", min_value=0.1, value=1.20, step=0.01)
        
    col3, col4 = st.columns(2)
    with col3:
        linea_goles = st.selectbox("Línea de Goles", [1.5, 2.5, 3.5, 4.5], index=1)
    with col4:
        rho_val = st.slider("Parámetro Rho (Dixon-Coles)", min_value=-0.3, max_value=0.0, value=-0.15, step=0.01)
        
    submitted = st.form_submit_button("Ejecutar Auditoría", type="primary")

if submitted:
    # Calcular resultados
    matriz = under_over(lam_local, lam_visitante, line=linea_goles, rho=rho_val)
    simple = under_over_simple(lam_local, lam_visitante, line=linea_goles)
    diff = abs(matriz["over"] - simple["over"])

    st.divider()
    st.subheader("📊 Resultados de la Auditoría")
    
    # Métricas principales de Under / Over
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("λ Total", f"{matriz['lambda_total']:.3f}")
    col_b.metric(f"Under {linea_goles}", f"{matriz['under']*100:.2f}%", f"Simple: {simple['under']*100:.2f}%")
    col_c.metric(f"Over {linea_goles}", f"{matriz['over']*100:.2f}%", f"Simple: {simple['over']*100:.2f}%")

    # Validación de sanidad
    if diff > 0.01:
        st.warning(f"⚠️ Alerta: Desviación notable de {diff*100:.2f}% entre la matriz y el método simple.")
    else:
        st.success(f"✅ Coherente: Diferencia mínima de {diff*100:.4f}% entre métodos. Suma total de matriz: {matriz['suma_probabilidades']*100:.2f}%")

    # Top marcadores
    st.subheader("🎯 Top 5 Marcadores Más Probables")
    top_marcadores = sorted(matriz["grid"].items(), key=lambda x: -x[1])[:5]
    
    tabla_datos = []
    for (i, j), p in top_marcadores:
        tabla_datos.append({"Marcador": f"{i} - {j}", "Probabilidad": f"{p*100:.2f}%"})
    
    st.table(tabla_datos)
    verificar_consistencia(lam_local_ejemplo, lam_visitante_ejemplo, line=2.5, rho=0.0)
    
    # Prueba con corrección Dixon-Coles
    verificar_consistencia(lam_local_ejemplo, lam_visitante_ejemplo, line=2.5, rho=-0.15)
