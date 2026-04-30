"""
电磁场可视化 - 基于麦克斯韦方程组的科学展示
Electromagnetic Field Visualization based on Maxwell's Equations

物理基础:
  库仑定律:    E = kq/r²  (点电荷电场)
  毕奥-萨伐尔: dB = μ₀I dl×r̂ / 4πr²  (电流磁场)
  电磁波:      E⊥B⊥k, c=1/√(ε₀μ₀)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.font_manager as _fm
from matplotlib.patches import FancyArrowPatch
from matplotlib.colors import Normalize
from matplotlib import cm

# Register CJK font for Chinese character support
_cjk_font = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
try:
    _fm.fontManager.addfont(_cjk_font)
    _CJK_FAMILY = 'Noto Sans CJK JP'
except Exception:
    _CJK_FAMILY = 'DejaVu Sans'

# ── 物理常数 ──────────────────────────────────────────────────────────────────
K_E = 8.9875e9   # 库仑常数 [N·m²/C²]
MU_0 = 4e-7 * np.pi  # 真空磁导率 [T·m/A]
C_LIGHT = 3e8    # 光速 [m/s]

# ══════════════════════════════════════════════════════════════════════════════
#  1. 点电荷电场 (Coulomb's Law)
# ══════════════════════════════════════════════════════════════════════════════

def electric_field_2d(charges, x, y):
    """
    叠加原理: E_total = Σ kqᵢ(r - rᵢ) / |r - rᵢ|³
    charges: list of (x, y, q)  单位: 位置[m], 电荷[C]
    """
    Ex = np.zeros_like(x, dtype=float)
    Ey = np.zeros_like(y, dtype=float)
    for cx, cy, q in charges:
        dx = x - cx
        dy = y - cy
        r3 = (dx**2 + dy**2 + 1e-20) ** 1.5
        Ex += K_E * q * dx / r3
        Ey += K_E * q * dy / r3
    return Ex, Ey


def electric_potential_2d(charges, x, y):
    """标量电势 V = Σ kqᵢ / rᵢ"""
    V = np.zeros_like(x, dtype=float)
    for cx, cy, q in charges:
        r = np.sqrt((x - cx)**2 + (y - cy)**2 + 1e-20)
        V += K_E * q / r
    return V


def plot_electric_field(ax, charges, xlim=(-3, 3), ylim=(-3, 3), n=300, ns=20):
    x = np.linspace(*xlim, n)
    y = np.linspace(*ylim, n)
    X, Y = np.meshgrid(x, y)

    Ex, Ey = electric_field_2d(charges, X, Y)
    V = electric_potential_2d(charges, X, Y)
    E_mag = np.log1p(np.sqrt(Ex**2 + Ey**2))  # 对数压缩增强显示

    # 等势面
    v_levels = np.linspace(-5e10, 5e10, 30)
    ax.contour(X, Y, np.clip(V, -5e10, 5e10), levels=v_levels,
               colors='white', linewidths=0.4, alpha=0.35, linestyles='dashed')

    # 场强背景色
    ax.pcolormesh(X, Y, E_mag, cmap='inferno', shading='auto',
                  norm=Normalize(E_mag.min(), E_mag.max()), alpha=0.85)

    # 流线 (field lines via streamplot)
    xs = np.linspace(*xlim, ns)
    ys = np.linspace(*ylim, ns)
    Xs, Ys = np.meshgrid(xs, ys)
    Exs, Eys = electric_field_2d(charges, Xs, Ys)
    speed = np.sqrt(Exs**2 + Eys**2)
    ax.streamplot(xs, ys, Exs, Eys,
                  color='cyan', linewidth=0.7, density=1.2,
                  arrowsize=0.9, arrowstyle='->', minlength=0.2,
                  norm=Normalize(speed.min(), speed.max()))

    # 绘制电荷
    for cx, cy, q in charges:
        color = '#ff4444' if q > 0 else '#4488ff'
        label = f'+{abs(q):.0e}C' if q > 0 else f'-{abs(q):.0e}C'
        ax.plot(cx, cy, 'o', ms=14, color=color,
                markeredgecolor='white', markeredgewidth=1.5, zorder=5)
        ax.text(cx, cy + 0.22, label, ha='center', va='bottom',
                fontsize=7, color='white', fontweight='bold', zorder=6)

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_facecolor('#0a0a1a')
    ax.set_xlabel('x [m]', color='#aaaacc')
    ax.set_ylabel('y [m]', color='#aaaacc')
    ax.tick_params(colors='#aaaacc')
    for spine in ax.spines.values():
        spine.set_edgecolor('#334466')


# ══════════════════════════════════════════════════════════════════════════════
#  2. 无限长直导线磁场 (Biot-Savart, 2-D 截面)
# ══════════════════════════════════════════════════════════════════════════════

def magnetic_field_wire_2d(wires, x, y):
    """
    无限长直导线: B = μ₀I / (2πρ)  方向: φ̂ (柱坐标)
    wires: list of (x, y, I)  I>0 向外, I<0 向内
    """
    Bx = np.zeros_like(x, dtype=float)
    By = np.zeros_like(y, dtype=float)
    for wx, wy, I in wires:
        dx = x - wx
        dy = y - wy
        r2 = dx**2 + dy**2 + 1e-20
        # B ∝ (-dy, dx) / r²  (右手定则)
        Bx += -MU_0 * I * dy / (2 * np.pi * r2)
        By +=  MU_0 * I * dx / (2 * np.pi * r2)
    return Bx, By


def plot_magnetic_field(ax, wires, xlim=(-3, 3), ylim=(-3, 3), n=200, ns=18):
    x = np.linspace(*xlim, n)
    y = np.linspace(*ylim, n)
    X, Y = np.meshgrid(x, y)

    Bx, By = magnetic_field_wire_2d(wires, X, Y)
    B_mag = np.log1p(np.sqrt(Bx**2 + By**2))

    ax.pcolormesh(X, Y, B_mag, cmap='viridis', shading='auto', alpha=0.85)

    xs = np.linspace(*xlim, ns)
    ys = np.linspace(*ylim, ns)
    Xs, Ys = np.meshgrid(xs, ys)
    Bxs, Bys = magnetic_field_wire_2d(wires, Xs, Ys)
    speed = np.sqrt(Bxs**2 + Bys**2) + 1e-20
    ax.streamplot(xs, ys, Bxs, Bys,
                  color='#00ffcc', linewidth=0.8, density=1.0,
                  arrowsize=0.9, arrowstyle='->', minlength=0.3,
                  norm=Normalize(speed.min(), speed.max()))

    # 绘制导线截面
    for wx, wy, I in wires:
        color = '#ff6600' if I > 0 else '#6600ff'
        marker = r'$\odot$' if I > 0 else r'$\otimes$'
        ax.plot(wx, wy, 'o', ms=18, color=color, zorder=5,
                markeredgecolor='white', markeredgewidth=1.5)
        ax.text(wx, wy, marker, ha='center', va='center', fontsize=14,
                color='white', zorder=6)
        label = f'I={abs(I):.0f}A {"↑" if I > 0 else "↓"}'
        ax.text(wx, wy + 0.35, label, ha='center', fontsize=7,
                color='white', fontweight='bold')

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_facecolor('#0a0a1a')
    ax.set_xlabel('x [m]', color='#aaaacc')
    ax.set_ylabel('y [m]', color='#aaaacc')
    ax.tick_params(colors='#aaaacc')
    for spine in ax.spines.values():
        spine.set_edgecolor('#334466')


# ══════════════════════════════════════════════════════════════════════════════
#  3. 平面电磁波 (E ⊥ B ⊥ k, 频率 f, 沿 z 轴传播)
# ══════════════════════════════════════════════════════════════════════════════

def plot_em_wave(ax, freq=1e9, n_lambda=2):
    """
    E(z,t=0) = E₀ sin(kz) x̂
    B(z,t=0) = (E₀/c) sin(kz) ŷ
    k = 2πf/c, λ = c/f
    """
    wavelength = C_LIGHT / freq
    k = 2 * np.pi / wavelength
    E0 = 1.0
    B0 = E0 / C_LIGHT

    z = np.linspace(0, n_lambda * wavelength, 800)
    E = E0 * np.sin(k * z)
    B = B0 * np.sin(k * z)

    # 箭头采样
    z_arr = np.linspace(0, n_lambda * wavelength, 40)
    E_arr = E0 * np.sin(k * z_arr)
    B_arr = B0 * np.sin(k * z_arr)

    ax.set_facecolor('#0a0a1a')

    # E 场 (x 方向, 红色系)
    ax.plot(z, E, color='#ff4466', lw=2.0, label=r'$\vec{E}$  (x̂)', zorder=3)
    ax.fill_between(z, 0, E, alpha=0.12, color='#ff4466')

    # B 场 (y 方向, 蓝色系)
    # 用虚线区分平面
    ax.plot(z, B * (C_LIGHT / E0),  # 归一化到同幅度显示
            color='#44aaff', lw=2.0, linestyle='--',
            label=r'$\vec{B}$  (ŷ, 归一化)', zorder=3)
    ax.fill_between(z, 0, B * (C_LIGHT / E0), alpha=0.12, color='#44aaff')

    # 传播方向箭头
    ax.annotate('', xy=(n_lambda * wavelength * 0.98, 0),
                xytext=(n_lambda * wavelength * 0.92, 0),
                arrowprops=dict(arrowstyle='->', color='#ffff00', lw=2))
    ax.text(n_lambda * wavelength * 0.95, 0.08, r'$\vec{k}$ (ẑ)',
            color='#ffff00', fontsize=9, ha='center')

    # 场矢量小箭头
    for z0, e, b in zip(z_arr, E_arr, B_arr * (C_LIGHT / E0)):
        if abs(e) > 0.05:
            ax.annotate('', xy=(z0, e), xytext=(z0, 0),
                        arrowprops=dict(arrowstyle='->', color='#ff4466',
                                        lw=0.8, alpha=0.7))
        if abs(b) > 0.05:
            ax.annotate('', xy=(z0, b), xytext=(z0, 0),
                        arrowprops=dict(arrowstyle='->', color='#44aaff',
                                        lw=0.8, alpha=0.7, linestyle='dashed'))

    # 标注波长
    ax.annotate('', xy=(wavelength, -1.15), xytext=(0, -1.15),
                arrowprops=dict(arrowstyle='<->', color='white', lw=1))
    ax.text(wavelength / 2, -1.28, f'λ = {wavelength*100:.1f} cm',
            ha='center', color='white', fontsize=8)

    ax.axhline(0, color='#445566', lw=0.8)
    ax.set_xlim(0, n_lambda * wavelength)
    ax.set_ylim(-1.5, 1.5)
    ax.set_xlabel('z [m]', color='#aaaacc')
    ax.set_ylabel('归一化振幅', color='#aaaacc')
    ax.tick_params(colors='#aaaacc')
    for spine in ax.spines.values():
        spine.set_edgecolor('#334466')
    legend = ax.legend(loc='upper right', framealpha=0.3,
                       labelcolor='white', fontsize=9)
    legend.get_frame().set_facecolor('#1a1a2e')


# ══════════════════════════════════════════════════════════════════════════════
#  4. 偶极子辐射场 (远场近似)
# ══════════════════════════════════════════════════════════════════════════════

def plot_dipole_radiation(ax, xlim=(-4, 4), ylim=(-4, 4), n=250):
    """
    振荡电偶极子辐射:  E_θ ∝ sin(θ)/r  (远场)
    辐射功率角分布:    dP/dΩ ∝ sin²(θ)
    """
    x = np.linspace(*xlim, n)
    y = np.linspace(*ylim, n)
    X, Y = np.meshgrid(x, y)
    r = np.sqrt(X**2 + Y**2) + 1e-10
    theta = np.arctan2(X, Y)   # 偶极子沿 y 轴

    # 辐射场强 |E| ∝ sin(θ)/r
    E_rad = np.abs(np.sin(theta)) / r
    # 叠加近场 coulomb 项 ∝ 1/r²
    E_near = 0.15 / r**2
    E_total = np.log1p(E_rad + E_near)

    pcm = ax.pcolormesh(X, Y, E_total, cmap='plasma', shading='auto',
                        alpha=0.9)

    # 极坐标辐射图案叠加
    theta_p = np.linspace(0, 2 * np.pi, 500)
    r_pattern = 2.5 * np.sin(theta_p)**2
    ax.plot(r_pattern * np.sin(theta_p), r_pattern * np.cos(theta_p),
            color='#00ff88', lw=1.5, label=r'$dP/d\Omega \propto \sin^2\theta$',
            alpha=0.85)

    # 偶极子
    ax.annotate('', xy=(0, 0.5), xytext=(0, -0.5),
                arrowprops=dict(arrowstyle='<->', color='#ffff00', lw=2.5))
    ax.text(0.15, 0, r'$\vec{p}$', color='#ffff00', fontsize=12,
            va='center', fontweight='bold')

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_facecolor('#0a0a1a')
    ax.set_xlabel('x [m]', color='#aaaacc')
    ax.set_ylabel('y [m]', color='#aaaacc')
    ax.tick_params(colors='#aaaacc')
    for spine in ax.spines.values():
        spine.set_edgecolor('#334466')
    legend = ax.legend(loc='lower right', framealpha=0.3,
                       labelcolor='white', fontsize=8)
    legend.get_frame().set_facecolor('#1a1a2e')


# ══════════════════════════════════════════════════════════════════════════════
#  主图布局
# ══════════════════════════════════════════════════════════════════════════════

def main():
    plt.rcParams.update({
        'figure.facecolor': '#060612',
        'axes.facecolor': '#0a0a1a',
        'text.color': 'white',
        'axes.titlecolor': 'white',
        'font.family': [_CJK_FAMILY, 'DejaVu Sans'],
        'axes.titlesize': 11,
        'axes.titlepad': 8,
    })

    fig = plt.figure(figsize=(18, 12))
    fig.suptitle(
        '电磁场可视化  |  Electromagnetic Field Visualization\n'
        r'基于麦克斯韦方程组 $\nabla\cdot\mathbf{E}=\rho/\varepsilon_0,\;'
        r'\nabla\times\mathbf{B}=\mu_0\mathbf{J}+\mu_0\varepsilon_0\partial\mathbf{E}/\partial t$',
        fontsize=13, color='white', y=0.99
    )

    gs = gridspec.GridSpec(2, 2, hspace=0.38, wspace=0.28,
                           left=0.06, right=0.97, top=0.91, bottom=0.07)

    # ── 子图 1: 电偶极子电场 ─────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    charges_dipole = [(-1.0, 0, -1e-9), (1.0, 0, +1e-9)]
    plot_electric_field(ax1, charges_dipole)
    ax1.set_title('① 电偶极子电场  (库仑叠加原理)', fontsize=10)
    ax1.text(0.01, 0.01,
             r'$\mathbf{E}=\sum_i\frac{kq_i(\mathbf{r}-\mathbf{r}_i)}{|\mathbf{r}-\mathbf{r}_i|^3}$',
             transform=ax1.transAxes, color='#88bbff', fontsize=9,
             bbox=dict(facecolor='#0a0a2a', alpha=0.7, edgecolor='none'))

    # ── 子图 2: 平行导线磁场 ─────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    wires = [(-1.5, 0, 3000), (1.5, 0, -3000)]
    plot_magnetic_field(ax2, wires)
    ax2.set_title('② 平行载流导线磁场  (安培定律)', fontsize=10)
    ax2.text(0.01, 0.01,
             r'$B=\frac{\mu_0 I}{2\pi\rho}$',
             transform=ax2.transAxes, color='#88ffcc', fontsize=9,
             bbox=dict(facecolor='#0a0a2a', alpha=0.7, edgecolor='none'))

    # ── 子图 3: 平面电磁波 ───────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    plot_em_wave(ax3, freq=3e9, n_lambda=2)
    ax3.set_title('③ 平面电磁波  (f = 3 GHz, 微波段)', fontsize=10)
    ax3.text(0.01, 0.93,
             r'$c = \frac{1}{\sqrt{\mu_0\varepsilon_0}} \approx 3\times10^8\ \mathrm{m/s}$',
             transform=ax3.transAxes, color='#ffaaaa', fontsize=9,
             bbox=dict(facecolor='#0a0a2a', alpha=0.7, edgecolor='none'))

    # ── 子图 4: 偶极子辐射 ───────────────────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    plot_dipole_radiation(ax4)
    ax4.set_title('④ 振荡电偶极子辐射场  (远场近似)', fontsize=10)
    ax4.text(0.01, 0.01,
             r'$\frac{dP}{d\Omega}=\frac{\mu_0\omega^4p_0^2}{32\pi^2 c}\sin^2\theta$',
             transform=ax4.transAxes, color='#ffccaa', fontsize=9,
             bbox=dict(facecolor='#0a0a2a', alpha=0.7, edgecolor='none'))

    plt.savefig('em_field_visualization.png', dpi=180, bbox_inches='tight',
                facecolor=fig.get_facecolor())
    print("已保存: em_field_visualization.png")
    plt.show()


if __name__ == '__main__':
    main()
