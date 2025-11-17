"""
Dieses Skript generiert Konzentrations-Plots mit Plotly.
Outputs:
    'liga1.html'
    'liga2.html'
    'nullkonzentration.html'
    'totalekonzentration.html'

Alle Outputfiles werden über lorenz_demo.html zusammen gerendert.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.io as pio
import numpy as np


def plot_konzentration(urliste, my_title):
    # ------------------- statistische Kennzahlen -------------------
    aj, h_aj = np.unique(urliste, return_counts=True) # aj, h(aj) 
    n = len(urliste) # Stichprobenumfang n
    V = np.sum(urliste) # Gesamtsumme
    k = len(aj) # Anzahl der Ausprägungen k
    axhdivV = (aj * h_aj) / V 
    f_aj = h_aj/n # f(aj) 

    uj = np.cumsum(f_aj) # f(aj) kumulierte -> u_j = F
    vj = np.cumsum(axhdivV) # (aj*h_aj) / V kumuliert -> v_j

    # my_colors = ['#EF8FB0', '#6666FF', "#B4B6FD"] 
    main_color = "#1a48b2" # "#243b38"
    palette = px.colors.qualitative.Plotly
    colors_list = [palette[i % len(palette)] for i in range(k)]
    color_mapping = {a: c for a, c in zip(aj, colors_list)}
    my_colors = [color_mapping[a] for a in aj]


    # ------------------- Plot Initialisierung -------------------
    fig = make_subplots(
        rows=2, cols=4,
        #specs=[[{"type": "scene", "rowspan": 2}, {"type": "xy"}, {"type": "xy"}, {"type": "xy", "rowspan": 2}],
        #      [None, {"type": "xy"}, {"type": "xy"}, None]],
        specs=[[{"type": "scene"}, {"type": "xy"}, {"type": "xy"}, {"type": "xy", "rowspan": 2}],
            [{"type": "scene"}, {"type": "xy"}, {"type": "xy"}, None]],
        column_widths=[0.3, 0.2, 0.2, 0.3],
        row_heights=[0.5, 0.5],
        vertical_spacing=0.2, horizontal_spacing=0.05)

    fig.update_layout(
        plot_bgcolor='white', paper_bgcolor='white',
        height=600, width=1300,
        title_text = my_title,
        margin=dict(t=130, b=80, l=50, r=50), 
        showlegend=False)

    fig.update_yaxes(
        tick0=0,
        range=[0, 1.05], 
        dtick=0.2,
        gridcolor='lightgray',
        gridwidth=1,
        zeroline=True,
        zerolinewidth=1,
        zerolinecolor='gray')

    fig.update_xaxes(tickvals= aj)


    # ------------------- Hilfsfunktionen -------------------
    # ticks 
    def ticks(values, additional_ticks = [1]): 
        ticks = np.round(values, 3).tolist()
        all_ticks = sorted(set(ticks + additional_ticks))
        return all_ticks

    # Zähldichte 
    def plot_zähldichte(x_values, P_values, my_colors, row, col):
        # Linien 
        for x, y, c in zip(x_values, P_values, my_colors):
            fig.add_trace(
                go.Scatter(
                    x=[x, x],
                    y=[0, y],
                    mode='lines',
                    line=dict(color=c, width=3),
                    showlegend=False),
                row=row, col=col)
        # Punkte
        fig.add_trace(
            go.Scatter(x=x_values, y=P_values, mode='markers', marker=dict(color=my_colors, size=7), showlegend=False),
            row=row, col=col)
        return fig

    # CDF für diskret 
    def plot_disrete_cdf(x_values, y_values, row, col):
        # Startlinie links
        y_start=0.01
        fig.add_trace(go.Scatter(
            x=[0, x_values[0] - 0.05],
            y=[y_start, y_start],
            mode='lines',
            line=dict(color=main_color, width=3),
            showlegend=False), 
            row=row, col=col)
        # Punkt rechts
        fig.add_trace(go.Scatter(
            x=[x_values[0]],
            y=[y_start],
            mode='markers',
            marker=dict(color=main_color, size=7, symbol='circle-open'),
            showlegend=False), 
            row=row, col=col)
        for i in range(len(x_values)):
            x_left = x_values[i]
            x_right = x_values[i + 1] if i < len(x_values) - 1 else (x_values[i] + (x_values[i] - x_values[i - 1]) * 0.5 if i > 0 else x_values[i] + 0.2)
            y_val = y_values[i]
            # Punkt links
            fig.add_trace(go.Scatter(
                x=[x_left],
                y=[y_val],
                mode='markers',
                marker=dict(color=main_color, size=7, symbol='circle'),
                showlegend=False), 
                row=row, col=col)
            # horizontale Linie
            fig.add_trace(go.Scatter(
                x=[x_left, x_right - 0.05],
                y=[y_val, y_val],
                mode='lines',
                line=dict(color=main_color, width=3),
                showlegend=False), 
                row=row, col=col)
            # Punkt rechts, falls y < 1
            if y_val < 1.0:
                fig.add_trace(go.Scatter(
                    x=[x_right],
                    y=[y_val],
                    mode='markers',
                    marker=dict(color=main_color, size=7, symbol='circle-open'),
                    showlegend=False), 
                    row=row, col=col)
        return fig

    # 3d- Pie-Chart
    def create_3d_piechart(start_angle, end_angle, height, color, resolution=30):
        theta = np.linspace(start_angle, end_angle, resolution)
        x_base = np.cos(theta)
        y_base = np.sin(theta)
        z_base = np.zeros_like(theta)
        x_top = x_base
        y_top = y_base
        z_top = np.ones_like(theta) * height
        # Mittelpunkt unten und oben
        x_center = [0]
        y_center = [0]
        z_bottom_center = [0]
        z_top_center = [height]
        # alle Punkte
        x = list(x_base) + x_center + list(x_top) + x_center
        y = list(y_base) + y_center + list(y_top) + y_center
        z = list(z_base) + z_bottom_center + list(z_top) + z_top_center
        n = resolution
        indices = []
        for i in range(n-1):
            indices.append((i, i+1, n))           # Boden
            indices.append((i+n+1, i+n+2, 2*n+1)) # Decke
        # Seiten entlang Kreislinie
        for i in range(n-1):
            indices.append((i, i+1, i+n+2))
            indices.append((i, i+n+2, i+n+1))
        # Seiten von der Mitte nach außen 
        # Startkante
        indices.append((n, 0, n+n+1))   # Boden -> Spitze
        indices.append((0, n+1, n+n+1)) # Spitze oben
        # Endkante
        indices.append((n, n-1, 2*n+1))
        indices.append((n-1, 2*n, 2*n+1))

        i, j, k = zip(*indices)

        return go.Mesh3d( x=x, y=y, z=z, i=i, j=j, k=k, color=color, opacity=1, flatshading=True)


    # ------------------- (1,1) Pie-Chart -------------------
    pie_trace = go.Pie(
        values=f_aj,
        labels=aj,
        marker=dict(colors=my_colors),
        textinfo='label+value',
        texttemplate='%{value:.3f}',
        domain=dict(x=[0, 0.3], y=[0.7, 1.0]))
    fig.add_trace(pie_trace)
    
    
    # ------------------- (2,1) 3d-Pie-Chart -------------------
    current_bogenmaß = 0  # Startwinkel in Bogenmaß
    r = 0.7  # Abstand vom Mittelpunkt
    for i in range(k):
        sektor_bogenmaß = f_aj[i] * 2 * np.pi  # b = alpha / 360 * 2pi = f_aj * 2pi
        start = current_bogenmaß
        end = current_bogenmaß + sektor_bogenmaß
        height = aj[i]
        color = my_colors[i]
        fig.add_trace(create_3d_piechart(start, end, height, color))

        # für Text über den Sektoren: 
        angle = (start + end) / 2     # Mittelpunkt 
        x_text = r * np.cos(angle)
        y_text = r * np.sin(angle)
        z_text = aj[i] 
        fig.add_trace(go.Scatter3d(
            x=[x_text],
            y=[y_text],
            z=[z_text],
            mode='text',
            text=[f"{np.round(axhdivV, 3)[i]}"],
            textposition='top center',
            textfont=dict(size=10),
            showlegend=False)), 
        current_bogenmaß = end  

    fig.update_layout(
        scene=dict(
            domain=dict(x=[0, 0.3], y=[0, 0.6]), 
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(
                title='V',
                title_font=dict(size=12),
                #range=[0, max(aj) + 2],
                tickvals=aj,
                showgrid=True,
                gridcolor='lightgray',
                zeroline=True,
                zerolinecolor='gray'),
            aspectratio=dict(x=1.2, y=1.2, z=1.2),
            camera=dict(eye=dict(x=0, y=2.5, z=0))))


    # ------------------- (1,2) f(aj) -------------------
    plot_zähldichte(aj, f_aj, my_colors, row=1 , col = 2)
    '''
    # Titel: 
    fig.add_annotation( row=1, col=2, align="left", xref="x domain", yref="y domain",
        text="Anteil stat. Einheiten mit Merkmal aⱼ<br>an Gesamtstichprobe n<br>(Wahrscheinlichkeitsfkt.)",
        font=dict(size=10), 
        x=0.5, y=1.4, showarrow=False)
    '''
    fig.add_annotation(row=1, col=2, xref="x domain", yref="y domain",
                    text=r"$f(a_j)$", font=dict(size=12),
                    x=0, y=1.2, showarrow=False)
    fig.update_yaxes(row=1, col=2, tickvals=ticks(f_aj))


    # ------------------- (1,3) F(aj) -------------------
    '''
    # Titel: 
    fig.add_annotation( row=1, col=3, align="left", xref="x domain", yref="y domain",
        text="kumulierter Anteil stat. Einheiten mit<br>Merkmal aⱼ an Gesamtstichprobe n<br>(Verteilungsfkt.)",
        font=dict(size=10), 
        x=0.5, y=1.4, showarrow=False)
    '''
    plot_disrete_cdf(aj, uj, row = 1, col=3)
    fig.add_annotation(row=1, col=3, xref="x domain", yref="y domain",
                    text=r"$\sum f(a_j)$", font=dict(size=12), 
                    x=0, y=1.2, showarrow=False)
    fig.update_yaxes(row=1, col=3, tickvals=ticks(uj))


    # ------------------- (2,2) (aj*h_aj)/V -------------------
    '''
    # Titel: 
    fig.add_annotation( row=2, col=2, align="left", xref="x domain", yref="y domain",
        text="Anteil von Merkmalswert aⱼ<br>am Gesamt(markt)gewinn V",
        font=dict(size=10), 
        x=0.5, y=1.3, showarrow=False)
    '''
    plot_zähldichte(aj, axhdivV, my_colors, row=2 , col = 2)
    fig.add_annotation(row=2, col=2, xref="x domain", yref="y domain",
                    text=r"$ \frac{a_j\cdot h(a_j) }{V}$", font=dict(size=12), 
                    x=0, y=1.2, showarrow=False)
    fig.update_yaxes(row=2, col=2, tickvals=ticks(axhdivV))


    # ------------------- (2,3) vj ---------------------------
    '''
    # Titel: 
    fig.add_annotation( row=2, col=3, align="left", xref="x domain", yref="y domain",
        text="kumulierter Anteil von Merkmalswert a_j<br>an Gesamt(markt)gewinn V",
        font=dict(size=10), 
        x=0.5, y=1.3, showarrow=False)
    '''
    plot_disrete_cdf(aj, vj, row = 2, col=3)
    fig.add_annotation(row=2, col=3, align="left", xref="x domain", yref="y domain",
                    text=r"$\sum \frac{a_j \cdot h(a_j)}{V}$",  font=dict(size=12),
                    x=0, y=1.2, showarrow=False)
    fig.update_yaxes(row=2, col=3, tickvals=ticks(vj))


    # ------------------- (1,4) Lorenzkurve -------------------
    fig.add_trace(go.Scatter(
        x=np.insert(uj, 0, 0),
        y=np.insert(vj, 0, 0),
        mode='lines+markers',
        name='Lorenzkurve',
        line=dict(color=main_color, width=3)), row=1, col=4)
    fig.add_annotation(row=1, col=4, align="left", xref="x domain", yref="y domain",
                    text="Lorenzkurve",  font=dict(size=14),
                    x=0.5, y=1.1, showarrow=False)
    fig.update_xaxes(row=1, col=4, tick0=0, range=[0, 1.05], dtick=0.2, tickvals= np.arange(0, 1.0001, 0.2))
    # Winkelhalbierende
    fig.add_trace(go.Scatter(x=[0, 1], y=[0, 1], mode='lines', line=dict(dash='solid', color='gray'), showlegend=False), row=1, col=4)


    # ------------------- Ausgabe -----------------------
    # fig.show()
    return fig
    # ---------------------------------------------------

# urliste = np.array([1,1,1,6,6,6,6,6,6,6,6,6,6,6,6,11,11,11]) # Urliste
# my_title = "Mit Annahme der Einpunktverteilung: Urliste für Liga 1 (" + ", ".join(map(str, urliste)) + ")"
# plot_konzentration(urliste, my_titel=my_title)


urliste = np.array([1,1,1,6,6,6,6,6,6,6,6,6,6,6,6,11,11,11])
my_title = "Urliste unter Annahme der Einpunktverteilung (" + ", ".join(map(str, urliste)) + ")"
fig = plot_konzentration(urliste, my_title)  
pio.write_html(fig,"liga1.html")

urliste = np.array([1,1,1,1,1,1,1,1,1,1,3,3,3,3,3,3,3,3,3,3])
my_title = "Urliste unter Annahme der Einpunktverteilung (" + ", ".join(map(str, urliste)) + ")"
fig = plot_konzentration(urliste, my_title)  
pio.write_html(fig, "liga2.html")

urliste = np.array([4,4,4,4,4])
my_title = "Urliste (" + ", ".join(map(str, urliste)) + ")"
fig = plot_konzentration(urliste, my_title) 
pio.write_html(fig, "nullkonzentration.html")

urliste = np.array([4,0,0,0,0])
my_title = "Urliste (" + ", ".join(map(str, urliste)) + ")"
fig = plot_konzentration(urliste, my_title) 
pio.write_html(fig, "totalekonzentration.html")

# HINWEIS: 
# Damit LaTeX Output richtig angezeigt wird, muss in den den html files, die entstehen, die Zeile 
'''<head><meta charset="utf-8" /></head> '''
# ersetzt werden durch: 
'''
<head>
  <meta charset="utf-8" />
  <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
</head>
'''

