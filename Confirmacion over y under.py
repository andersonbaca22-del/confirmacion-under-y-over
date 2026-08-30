# ==============================================================
# AUDITORÍA INDEPENDIENTE: Under/Over y Dixon-Coles
# Ejecutar en consola: python poisson_under_over.py
# ==============================================================

import math

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

def verificar_consistencia(lam_h, lam_a, line=2.5, rho=0.0, tolerancia=0.01):
    matriz = under_over(lam_h, lam_a, line, rho)
    simple = under_over_simple(lam_h, lam_a, line)
    diff = abs(matriz["over"] - simple["over"])

    print(f"==================================================")
    print(f"🔎 AUDITORÍA DE PARTIDO (Línea: {line} | Rho: {rho})")
    print(f"==================================================")
    print(f"λ Local: {lam_h:.3f} | λ Visitante: {lam_a:.3f} | λ Total: {matriz['lambda_total']:.3f}")
    print(f"--------------------------------------------------")
    print(f"[Matriz] Under: {matriz['under']*100:.2f}%  |  Over: {matriz['over']*100:.2f}%")
    print(f"[Simple] Under: {simple['under']*100:.2f}%  |  Over: {simple['over']*100:.2f}%")
    print(f"Suma total de la matriz: {matriz['suma_probabilidades']*100:.4f}% (ideal ~100%)")
    print(f"Diferencia entre métodos: {diff*100:.4f}%")
    
    if diff > tolerancia:
        print(f"⚠️ ALERTA: Desviación notable detectada (>1%).")
    else:
        print(f"✅ Coherente (sin inflación anómala por matriz).")
    print("--------------------------------------------------")
    
    # Top 5 marcadores
    top_marcadores = sorted(matriz["grid"].items(), key=lambda x: -x[1])[:5]
    print("Top 5 Marcadores Probables:")
    for (i, j), p in top_marcadores:
        print(f"  {i} - {j}: {p*100:.2f}%")
    print("==================================================\n")

if __name__ == "__main__":
    # EJEMPLO DE CONSULTA RÁPIDA:
    # Simplemente cambia estos valores con los lambdas que te de Streamlit
    lam_local_ejemplo = 1.822
    lam_visitante_ejemplo = 1.043
    
    # Prueba sin corrección (Poisson puro)
    verificar_consistencia(lam_local_ejemplo, lam_visitante_ejemplo, line=2.5, rho=0.0)
    
    # Prueba con corrección Dixon-Coles
    verificar_consistencia(lam_local_ejemplo, lam_visitante_ejemplo, line=2.5, rho=-0.15)