import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# ============================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Simulador de Troceadores (Clase B y Clase C)",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Simulador de Troceadores de Potencia")

# ============================================================
# BARRA LATERAL: SELECCIÓN DE CLASE
# ============================================================

st.sidebar.header("🎛️ Selección de Topología")
tipo_troceador = st.sidebar.selectbox(
    "Elige el tipo de troceador:",
    ["Troceador Clase B (2do Cuadrante)", "Troceador Clase C (Dos Cuadrantes)"]
)

st.sidebar.markdown("---")

# ============================================================
# 1. LÓGICA Y DIBUJO DEL TROCEADOR CLASE B
# ============================================================
if tipo_troceador == "Troceador Clase B (2do Cuadrante)":
    st.subheader("⚡ Troceador Clase B (Segundo Cuadrante)")
    st.caption("Modelo sincronizado con rizado exponencial (aleta de tiburón).")

    st.sidebar.header("⚙️ Parámetros Clase B")
    D_pct = st.sidebar.slider("Ciclo de trabajo D (%) [Clase B]", 1.0, 99.0, 15.0, 0.5)
    D = D_pct / 100.0
    frecuencia = st.sidebar.number_input("Frecuencia (Hz) [Clase B]", 100, 20000, 1000, 50, key="f_b")
    Vi = st.sidebar.number_input("Tensión de fuente Vi (V) [Clase B]", 1.0, 500.0, 100.0, 5.0, key="vi_b")
    V_fem = st.sidebar.number_input("FEM de carga V (V) [Clase B]", 0.0, 500.0, 100.0, 5.0, key="fem_b")
    R = st.sidebar.number_input("Resistencia R (Ω) [Clase B]", 0.01, 100.0, 5.0, 0.1, key="r_b")
    L_mH = st.sidebar.number_input("Inductancia L (mH) [Clase B]", 0.1, 500.0, 10.0, 0.5, key="l_b")
    L = L_mH / 1000.0

    modo_switch = st.sidebar.radio("Modo de operación", ["Automático (PWM)", "Forzar ON", "Forzar OFF"], key="modo_b")

    def dibujar_bateria_vertical(ax, x, y1, y2, nombre, valor):
        ym = (y1 + y2) / 2
        ax.plot([x, x], [y1, ym - 0.2], lw=2, color="black")
        ax.plot([x, x], [ym + 0.2, y2], lw=2, color="black")
        ax.plot([x - 0.3, x + 0.3], [ym + 0.1, ym + 0.1], lw=3, color="black")
        ax.plot([x - 0.15, x + 0.15], [ym - 0.1, ym - 0.1], lw=2, color="black")
        ax.text(x - 0.7, ym, f"{nombre}\n{valor:.1f}V", ha="center", va="center", fontsize=10, fontweight="bold")

    def dibujar_resistencia_vertical(ax, x, y1, y2, valor):
        n = 6
        ys = np.linspace(y1, y2, n + 1)
        xs = [x]
        for i in range(1, len(ys) - 1):
            xs.append(x + 0.12 if i % 2 else x - 0.12)
        xs.append(x)
        ax.plot(xs, ys, lw=2, color="black")
        ax.text(x + 0.45, (y1 + y2) / 2, f"R = {valor:.1f}Ω", fontsize=10, fontweight="bold", va="center")

    def dibujar_bobina_vertical(ax, x, y1, y2, valor):
        y = np.linspace(y1, y2, 150)
        xcoil = x + 0.1 * np.sin(np.linspace(0, 4 * np.pi, len(y)))
        ax.plot(xcoil, y, lw=2, color="black")
        ax.text(x + 0.45, (y1 + y2) / 2, f"L = {valor:.1f}mH", fontsize=10, fontweight="bold", va="center")

    def dibujar_diodo_horizontal(ax, x1, x2, y, nombre):
        xm = (x1 + x2) / 2
        ax.plot([x1, xm - 0.15], [y, y], lw=2, color="black")
        ax.plot([xm + 0.15, x2], [y, y], lw=2, color="black")
        tri = Polygon([[xm - 0.15, y + 0.2], [xm - 0.15, y - 0.2], [xm + 0.15, y]], closed=True, fill=False, lw=2, edgecolor="black")
        ax.add_patch(tri)
        ax.plot([xm + 0.15, xm + 0.15], [y - 0.2, y + 0.2], lw=2, color="black")
        ax.text(xm, y + 0.35, nombre, ha="center", fontsize=10, fontweight="bold")

    def dibujar_switch_vertical(ax, x, y1, y2, nombre, encendido):
        ym = (y1 + y2) / 2
        ax.plot([x, x], [y1, ym - 0.2], lw=2, color="black")
        ax.plot([x, x], [ym + 0.2, y2], lw=2, color="black")
        color_sw = "green" if encendido else "red"
        if encendido:
            ax.plot([x, x], [ym - 0.2, ym + 0.2], lw=3, color=color_sw)
        else:
            ax.plot([x - 0.15, x + 0.15], [ym - 0.15, ym + 0.15], lw=3, color=color_sw)
        ax.text(x + 0.35, ym, f"{nombre}\n({'ON' if encendido else 'OFF'})", fontsize=10, fontweight="bold", va="center")

    def circuito_clase_b_topologia(Vi, V_fem, R, L_mH, switch_on):
        fig, ax = plt.subplots(figsize=(7, 4.5))
        ax.set_xlim(-0.5, 7.5)
        ax.set_ylim(-0.5, 5.5)
        ax.axis("off")

        x_fuente = 0.5
        x_switch = 3.0
        x_carga = 6.0
        y_inf = 0.5
        y_sup = 4.5

        ax.plot([x_fuente, x_fuente], [y_inf, 2.0], lw=2, color="black")
        ax.plot([x_fuente, x_fuente], [3.0, y_sup], lw=2, color="black")
        dibujar_bateria_vertical(ax, x_fuente, y_inf, y_sup, "Vi", Vi)

        ax.plot([x_fuente, 1.8], [y_sup, y_sup], lw=2, color="black")
        dibujar_diodo_horizontal(ax, 1.8, x_switch, y_sup, "Dn")
        ax.plot([x_switch, x_carga], [y_sup, y_sup], lw=2, color="black")

        dibujar_switch_vertical(ax, x_switch, y_inf, y_sup, "S", switch_on)

        y_res_inf = 3.5
        y_bob_sup = 3.5
        y_bob_inf = 2.0
        y_fem_sup = 2.0
        
        ax.plot([x_carga, x_carga], [y_sup, y_res_inf], lw=2, color="black")
        dibujar_resistencia_vertical(ax, x_carga, y_res_inf, 3.8, R)
        ax.plot([x_carga, x_carga], [3.2, y_bob_sup], lw=2, color="black")
        
        dibujar_bobina_vertical(ax, x_carga, 1.8, 3.2, L_mH)
        ax.plot([x_carga, x_carga], [1.8, y_fem_sup], lw=2, color="black")
        dibujar_bateria_vertical(ax, x_carga, y_inf, 1.8, "V", V_fem)

        ax.plot([x_carga, x_switch], [y_inf, y_inf], lw=2, color="black")
        ax.plot([x_switch, x_fuente], [y_inf, y_inf], lw=2, color="black")

        ax.set_title("Troceador Clase B (Segundo Cuadrante)", fontsize=12, fontweight="bold")
        return fig

    T = 1.0 / frecuencia
    num_periodos = 3
    N_pts = 4000
    t_vec = np.linspace(0, num_periodos * T, N_pts)
    i_vec = np.zeros_like(t_vec)
    v_vec = np.zeros_like(t_vec)
    tau = L / R

    if modo_switch == "Forzar ON":
        D_eff = 1.0
        switch_est_on = True
    elif modo_switch == "Forzar OFF":
        D_eff = 0.0
        switch_est_on = False
    else:
        D_eff = D
        switch_est_on = None

    Ton = D_eff * T
    Toff = T - Ton

    if D_eff == 1.0:
        i_steady = -V_fem / R
        i_vec = i_steady + (-5.0 - i_steady) * np.exp(-t_vec / tau)
        v_vec = np.zeros_like(t_vec)
        I0, I1 = i_vec[-1], i_vec[0]
    elif D_eff == 0.0:
        i_steady = (Vi - V_fem) / R
        i_vec = i_steady + (-5.0 - i_steady) * np.exp(-t_vec / tau)
        v_vec = np.full_like(t_vec, Vi)
        I0, I1 = i_vec[-1], i_vec[0]
    else:
        A1 = -V_fem / R
        B1 = np.exp(-Ton / tau)
        A2 = (Vi - V_fem) / R
        B2 = np.exp(-Toff / tau)

        den = 1.0 - (B1 * B2)
        if den != 0:
            I0 = (A2 * (1.0 - B2) + A1 * (1.0 - B1) * B2) / den
        else:
            I0 = -5.0
        I1 = A1 * (1.0 - B1) + I0 * B1

        for idx, t_val in enumerate(t_vec):
            t_mod = t_val % T
            if t_mod <= Ton:
                t_on = t_mod
                i_vec[idx] = A1 + (I0 - A1) * np.exp(-t_on / tau)
                v_vec[idx] = 0.0
            else:
                t_off = t_mod - Ton
                i_vec[idx] = A2 + (I1 - A2) * np.exp(-t_off / tau)
                v_vec[idx] = Vi

        if switch_est_on is None:
            switch_est_on = (t_vec[100] % T) <= Ton

    Io_avg = np.mean(i_vec)
    Vo_avg = np.mean(v_vec)

    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("🔌 Topología del Circuito")
        fig_circ = circuito_clase_b_topologia(Vi, V_fem, R, L_mH, switch_est_on)
        st.pyplot(fig_circ, use_container_width=True)
        plt.close(fig_circ)

    with col2:
        st.subheader("📈 Formas de Onda Teóricas")
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

        ax1.plot(t_vec * 1000, v_vec, color="black", lw=2, label=r"$V_o(t)$")
        ax1.set_ylabel("Voltaje (V)", fontsize=10, fontweight="bold")
        ax1.set_title("Tensión de salida $V_o$", fontsize=11, fontweight="bold")
        ax1.set_ylim(-10, Vi + 25)
        ax1.grid(True, linestyle=":", alpha=0.5)

        t_ms = t_vec * 1000
        ax2.plot(t_ms, i_vec, color="black", lw=2, label=r"$I_o(t)$")
        ax2.fill_between(t_ms, i_vec, 0, color="gray", alpha=0.3)
        ax2.axhline(0, color="black", lw=1.2, linestyle="-")
        ax2.set_xlabel("Tiempo (ms)", fontsize=10, fontweight="bold")
        ax2.set_ylabel("Corriente (A)", fontsize=10, fontweight="bold")
        ax2.set_title("Corriente de carga $I_o$ (Rizado Exponencial)", fontsize=11, fontweight="bold")
        ax2.grid(True, linestyle=":", alpha=0.5)

        if D_eff not in [0.0, 1.0]:
            for k in range(num_periodos):
                t_ton_end = (k * T + Ton) * 1000
                t_per_end = (k + 1) * T * 1000
                ax1.axvline(t_ton_end, color="gray", linestyle="--", alpha=0.7)
                ax2.axvline(t_ton_end, color="gray", linestyle="--", alpha=0.7)
                ax1.axvline(t_per_end, color="gray", linestyle=":", alpha=0.5)
                ax2.axvline(t_per_end, color="gray", linestyle=":", alpha=0.5)

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    st.markdown("---")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Vo Promedio", f"{Vo_avg:.2f} V")
    m2.metric("Io Promedio", f"{Io_avg:.2f} A")
    m3.metric("I mínimo (I0)", f"{I0:.2f} A")
    m4.metric("I máximo (I1)", f"{I1:.2f} A")


# ============================================================
# 2. LÓGICA Y DIBUJO DEL TROCEADOR CLASE C (ACTUALIZADO CON 5 OPCIONES)
# ============================================================
else:
    st.subheader("⚡ Troceador Clase C (Dos Cuadrantes)")
    st.caption("Implementación con control independiente y total para S1 y S2.")

    st.sidebar.header("⚙️ Parámetros Clase C")
    D_pct_c = st.sidebar.slider("Ciclo de trabajo D (%) [Clase C]", 1.0, 99.0, 50.0, 0.5, key="d_c")
    D_c = D_pct_c / 100.0
    f_c = st.sidebar.number_input("Frecuencia (Hz) [Clase C]", 100, 20000, 1000, 50, key="f_c")
    E_c = st.sidebar.number_input("Tensión de fuente E (V) [Clase C]", 1.0, 500.0, 100.0, 5.0, key="e_c")
    V_fem_c = st.sidebar.number_input("Tensión de fuente V (V) [Clase C]", 0.0, 500.0, 50.0, 5.0, key="fem_c")
    R_c = st.sidebar.number_input("Resistencia R (Ω) [Clase C]", 0.01, 100.0, 5.0, 0.1, key="r_c")
    L_mc = st.sidebar.number_input("Inductancia L (mH) [Clase C]", 0.1, 500.0, 10.0, 0.5, key="l_c")
    Lc = L_mc / 1000.0

    modo_switch_c = st.sidebar.radio(
        "Modo de operación S1 y S2", 
        [
            "Automático (PWM)", 
            "Forzar S1 ON (S2 OFF)", 
            "Forzar S2 ON (S1 OFF)", 
            "Forzar S1 ON y S2 ON", 
            "Forzar S1 OFF y S2 OFF"
        ], 
        key="modo_c"
    )

    Tc = 1.0 / f_c
    Ton_c = D_c * Tc
    Toff_c = Tc - Ton_c
    tau_c = Lc / R_c

    den_c = 1.0 - np.exp(-Tc / tau_c)
    if den_c != 0:
        I_min = (E_c / R_c) * (np.exp(-Toff_c / tau_c) - np.exp(-Tc / tau_c)) / den_c - (V_fem_c / R_c)
        I_max = (E_c / R_c) * (1.0 - np.exp(-Ton_c / tau_c)) / den_c - (V_fem_c / R_c)
    else:
        I_min = 0.0
        I_max = 0.0

    num_periodos_c = 3
    N_pts_c = 4000
    t_vec_c = np.linspace(0, num_periodos_c * Tc, N_pts_c)
    i_vec_c = np.zeros_like(t_vec_c)
    v_vec_c = np.zeros_like(t_vec_c)

    # Lógica de simulación según el modo seleccionado
    if modo_switch_c == "Forzar S1 ON (S2 OFF)":
        s1_forced_on = True
        s2_forced_on = False
        i_steady = (E_c - V_fem_c) / R_c
        i_vec_c[:] = i_steady + (-5.0 - i_steady) * np.exp(-t_vec_c / tau_c)
        v_vec_c[:] = E_c
        I_min, I_max = i_vec_c[-1], i_vec_c[0]
    elif modo_switch_c == "Forzar S2 ON (S1 OFF)":
        s1_forced_on = False
        s2_forced_on = True
        i_steady = -V_fem_c / R_c
        i_vec_c[:] = i_steady + (-5.0 - i_steady) * np.exp(-t_vec_c / tau_c)
        v_vec_c[:] = 0.0
        I_min, I_max = i_vec_c[-1], i_vec_c[0]
    elif modo_switch_c == "Forzar S1 ON y S2 ON":
        s1_forced_on = True
        s2_forced_on = True
        # Cortocircuito en la rama superior/inferior
        i_vec_c[:] = E_c / R_c if R_c > 0 else 0.0
        v_vec_c[:] = E_c
        I_min, I_max = i_vec_c[0], i_vec_c[0]
    elif modo_switch_c == "Forzar S1 OFF y S2 OFF":
        s1_forced_on = False
        s2_forced_on = False
        i_steady = -V_fem_c / R_c
        i_vec_c[:] = i_steady
        v_vec_c[:] = 0.0
        I_min, I_max = 0.0, 0.0
    else:  # Automático (PWM)
        s1_forced_on = None
        s2_forced_on = None
        for idx, t_val in enumerate(t_vec_c):
            t_mod = t_val % Tc
            if t_mod <= Ton_c:
                t_on = t_mod
                i_vec_c[idx] = ((E_c - V_fem_c) / R_c) * (1.0 - np.exp(-t_on / tau_c)) + I_min * np.exp(-t_on / tau_c)
                v_vec_c[idx] = E_c
            else:
                t_off = t_mod - Ton_c
                i_vec_c[idx] = (-V_fem_c / R_c) * (1.0 - np.exp(-t_off / tau_c)) + I_max * np.exp(-t_off / tau_c)
                v_vec_c[idx] = 0.0

    # Estado visual estático para los switches en el gráfico del circuito
    if s1_forced_on is not None:
        s1_vis = s1_forced_on
        s2_vis = s2_forced_on
    else:
        s1_vis = (t_vec_c[100] % Tc) <= Ton_c
        s2_vis = not s1_vis

    Io_avg_c = np.mean(i_vec_c)
    Vo_avg_c = np.mean(v_vec_c)

    def dibujar_switch_vertical_c(ax, x, y1, y2, nombre, encendido):
        ym = (y1 + y2) / 2
        ax.plot([x, x], [y1, ym - 0.2], lw=2, color="black")
        ax.plot([x, x], [ym + 0.2, y2], lw=2, color="black")
        color_sw = "green" if encendido else "red"
        if encendido:
            ax.plot([x, x], [ym - 0.2, ym + 0.2], lw=3, color=color_sw)
        else:
            ax.plot([x - 0.15, x + 0.15], [ym - 0.15, ym + 0.15], lw=3, color=color_sw)
        ax.text(x - 0.4, ym, f"{nombre}\n({'ON' if encendido else 'OFF'})", fontsize=9, fontweight="bold", va="center", ha="right")

    def circuito_clase_c_topologia_completa(E, L_mH, R, V_fem, s1_encendido, s2_encendido):
        fig, ax = plt.subplots(figsize=(9.5, 5.0))
        ax.set_xlim(-0.5, 9.5)
        ax.set_ylim(-0.5, 5.5)
        ax.axis("off")

        # Fuente principal E izquierda
        ax.plot([0.5, 0.5], [0.5, 2.0], lw=2, color="black")
        ax.plot([0.5, 0.5], [3.0, 4.5], lw=2, color="black")
        ax.plot([0.2, 0.8], [3.0, 3.0], lw=3, color="black")
        ax.plot([0.35, 0.65], [2.0, 2.0], lw=2, color="black")
        ax.text(0.1, 3.7, "+", fontsize=11, fontweight="bold")
        ax.text(0.1, 1.2, "-", fontsize=11, fontweight="bold")
        ax.text(0.1, 2.5, f"E\n{E:.0f}V", ha="center", va="center", fontsize=9, fontweight="bold")

        # Rieles principales superior e inferior
        ax.plot([0.5, 2.5], [4.5, 4.5], lw=2, color="black")
        ax.plot([0.5, 8.2], [0.5, 0.5], lw=2, color="black")

        # Rama central de conmutación (S1 arriba, S2 abajo)
        dibujar_switch_vertical_c(ax, 2.5, 3.2, 4.5, "S1", s1_encendido)
        dibujar_switch_vertical_c(ax, 2.5, 0.5, 1.8, "S2", s2_encendido)
        ax.plot([2.5, 2.5], [1.8, 3.2], lw=2, color="black")

        # Nudo 1 entre S1 y S2
        ax.plot([2.5], [2.5], marker='o', markersize=5, color="black")

        # Conexión del Nudo 1 hacia la rama de diodos
        ax.plot([2.5, 4.2], [2.5, 2.5], lw=2, color="black")

        # Nudo 2 intermedio entre D1 y D2
        ax.plot([4.2], [2.5], marker='o', markersize=5, color="black")

        # D2 ubicado sobre S1, conectado al riel superior con línea horizontal completa
        ax.plot([4.2, 4.2], [4.5, 3.8], lw=2, color="black")
        tri2 = Polygon([[4.0, 3.2], [4.4, 3.2], [4.2, 3.8]], closed=True, fill=False, lw=2, edgecolor="black")
        ax.add_patch(tri2)
        ax.plot([4.0, 4.4], [3.2, 3.2], lw=2, color="black")
        ax.plot([4.2, 4.2], [3.2, 2.5], lw=2, color="black")
        ax.text(4.6, 3.5, "D2", fontsize=9, fontweight="bold", va="center")
        
        # Conexión superior completa de D2 al riel superior (y = 4.5)
        ax.plot([2.5, 4.2], [4.5, 4.5], lw=2, color="black")

        # D1 abajo (conectado al riel inferior)
        ax.plot([4.2, 4.2], [2.5, 1.8], lw=2, color="black")
        tri1 = Polygon([[4.0, 1.2], [4.4, 1.2], [4.2, 1.8]], closed=True, fill=False, lw=2, edgecolor="black")
        ax.add_patch(tri1)
        ax.plot([4.0, 4.4], [1.2, 1.2], lw=2, color="black")
        ax.plot([4.2, 4.2], [1.2, 0.5], lw=2, color="black")
        ax.text(4.6, 1.5, "D1", fontsize=9, fontweight="bold", va="center")

        # Rama de Carga en serie (L, luego R) saliendo del nudo de diodos
        ax.plot([4.2, 4.8], [2.5, 2.5], lw=2, color="black")
        
        # Inductancia L horizontal
        x_L = np.linspace(4.8, 5.6, 50)
        y_L = 2.5 + 0.08 * np.sin(np.linspace(0, 6 * np.pi, len(x_L)))
        ax.plot(x_L, y_L, lw=2, color="black")
        ax.text(5.2, 2.9, f"L={L_mH:.1f}mH", fontsize=8, fontweight="bold", ha="center")

        # Resistencia R horizontal
        rx = np.linspace(5.6, 6.4, 7)
        ry_h = np.array([2.5, 2.65, 2.35, 2.65, 2.35, 2.65, 2.5])
        ax.plot(rx, ry_h, lw=2, color="black")
        ax.text(6.0, 2.9, f"R={R:.1f}Ω", fontsize=8, fontweight="bold", ha="center")

        # Conexión hacia la fuente de voltaje V (en paralelo perfecto con D1)
        ax.plot([6.4, 8.2], [2.5, 2.5], lw=2, color="black")
        
        ax.plot([8.2, 8.2], [2.5, 3.1], lw=2, color="black")
        ax.plot([8.2, 8.2], [1.9, 0.5], lw=2, color="black")
        ax.plot([7.9, 8.5], [3.1, 3.1], lw=3, color="black") # (+) arriba
        ax.plot([8.05, 8.35], [1.9, 1.9], lw=2, color="black") # (-) abajo
        ax.text(8.7, 3.1, "+", fontsize=10, fontweight="bold")
        ax.text(8.7, 1.9, "-", fontsize=10, fontweight="bold")
        ax.text(8.7, 2.5, f"V\n{V_fem:.1f}V", fontsize=8, fontweight="bold", va="center")

        ax.set_title("Troceador Clase C (Dos Cuadrantes)", fontsize=12, fontweight="bold")
        return fig

    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.subheader("🔌 Topología del Circuito")
        fig_c = circuito_clase_c_topologia_completa(E_c, L_mc*1000.0, R_c, V_fem_c, s1_vis, s2_vis)
        st.pyplot(fig_c, use_container_width=True)
        plt.close(fig_c)

    with col2:
        st.subheader("📈 Formas de Onda Teóricas (Clase C)")
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

        ax1.plot(t_vec_c * 1000, v_vec_c, color="black", lw=2)
        ax1.set_ylabel("Voltaje (V)", fontsize=10, fontweight="bold")
        ax1.set_title("Tensión de salida $V_o$", fontsize=11, fontweight="bold")
        ax1.set_ylim(-10, E_c + 25)
        ax1.grid(True, linestyle=":", alpha=0.5)

        t_ms_c = t_vec_c * 1000
        ax2.plot(t_ms_c, i_vec_c, color="black", lw=2)
        ax2.fill_between(t_ms_c, i_vec_c, 0, color="gray", alpha=0.3)
        ax2.axhline(0, color="black", lw=1.2, linestyle="-")
        ax2.set_xlabel("Tiempo (ms)", fontsize=10, fontweight="bold")
        ax2.set_ylabel("Corriente (A)", fontsize=10, fontweight="bold")
        ax2.set_title("Corriente de carga $I_o$ (Rizado Exponencial)", fontsize=11, fontweight="bold")
        ax2.grid(True, linestyle=":", alpha=0.5)

        if modo_switch_c == "Automático (PWM)":
            for k in range(num_periodos_c):
                t_ton_end = (k * Tc + Ton_c) * 1000
                t_per_end = (k + 1) * Tc * 1000
                ax1.axvline(t_ton_end, color="gray", linestyle="--", alpha=0.7)
                ax2.axvline(t_ton_end, color="gray", linestyle="--", alpha=0.7)
                ax1.axvline(t_per_end, color="gray", linestyle=":", alpha=0.5)
                ax2.axvline(t_per_end, color="gray", linestyle=":", alpha=0.5)

        plt.tight_layout()
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    st.markdown("---")
    cm1, cm2, cm3, cm4 = st.columns(4)
    cm1.metric("Vo Promedio", f"{Vo_avg_c:.2f} V")
    cm2.metric("Io Promedio", f"{Io_avg_c:.2f} A")
    cm3.metric("I mínimo (Imin)", f"{I_min:.2f} A")
    cm4.metric("I máximo (Imax)", f"{I_max:.2f} A")