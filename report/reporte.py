import json
from datetime import datetime

from jinja2 import Template


def generate_reporte(ruta):
    # Leer el JSON
    with open(ruta, 'r') as f:
        data = json.load(f)

    # Procesar los datos para el reporte
    history_entries = data['history']
    formatted_entries = []

    for entry in history_entries:
        # Formatear fechas
        start_time = datetime.fromtimestamp(entry['metadata']['step_start_time']).strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.fromtimestamp(entry['metadata']['step_end_time']).strftime('%Y-%m-%d %H:%M:%S')
        duration = round(entry['metadata']['step_end_time'] - entry['metadata']['step_start_time'], 2)

        # Procesar la imagen base64
        screenshot = entry['state']['screenshot']
        img_tag = f'<img src="data:image/png;base64,{screenshot}" style="max-width: 600px; border: 1px solid #ddd; margin-top: 10px;">' if screenshot else 'No hay captura de pantalla'

        formatted_entries.append({
            'step_number': entry['metadata']['step_number'],
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            'current_state': entry['model_output']['current_state'],
            'action': entry['model_output']['action'],
            'result': entry['result'],
            'url': entry['state']['url'],
            'screenshot': img_tag
        })

    # Plantilla HTML
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reporte de Navegación Automatizada</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #2c3e50; }
            .entry { border: 1px solid #ddd; margin-bottom: 20px; padding: 15px; border-radius: 5px; }
            .step-header { background-color: #f8f9fa; padding: 10px; margin-bottom: 10px; }
            .state { margin-bottom: 10px; }
            .action { margin-bottom: 10px; padding-left: 15px; border-left: 3px solid #3498db; }
            .result { margin-bottom: 10px; padding-left: 15px; border-left: 3px solid #2ecc71; }
            .metadata { font-size: 0.9em; color: #7f8c8d; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .screenshot-container { margin-top: 15px; }
            .screenshot { max-width: 100%; border: 1px solid #ddd; }
            .expand-btn { 
                background-color: #3498db; 
                color: white; 
                border: none; 
                padding: 5px 10px; 
                cursor: pointer; 
                margin-top: 5px;
                border-radius: 3px;
            }
        </style>
        <script>
            function toggleScreenshot(imgId) {
                var img = document.getElementById(imgId);
                if (img.style.maxWidth === '600px') {
                    img.style.maxWidth = '100%';
                } else {
                    img.style.maxWidth = '600px';
                }
            }
        </script>
    </head>
    <body>
        <h1>Reporte de Navegación Automatizada</h1>
        <p>Resumen de las acciones realizadas durante la sesión de navegación.</p>
        
        <table>
            <tr>
                <th>Paso</th>
                <th>URL</th>
                <th>Inicio</th>
                <th>Fin</th>
                <th>Duración (s)</th>
            </tr>
            {% for entry in entries %}
            <tr>
                <td>{{ entry.step_number }}</td>
                <td>{{ entry.url }}</td>
                <td>{{ entry.start_time }}</td>
                <td>{{ entry.end_time }}</td>
                <td>{{ entry.duration }}</td>
            </tr>
            {% endfor %}
        </table>
        
        <h2>Detalle por Paso</h2>
        {% for entry in entries %}
        <div class="entry">
            <div class="step-header">
                <h3>Paso {{ entry.step_number }} - {{ entry.url }}</h3>
                <div class="metadata">
                    Inicio: {{ entry.start_time }} | Fin: {{ entry.end_time }} | Duración: {{ entry.duration }}s
                </div>
            </div>
            
            <div class="state">
                <h4>Estado Actual:</h4>
                <ul>
                    <li>Evaluación objetivo anterior: {{ entry.current_state.evaluation_previous_goal }}</li>
                    <li>Memoria: {{ entry.current_state.memory }}</li>
                    <li>Siguiente objetivo: {{ entry.current_state.next_goal }}</li>
                </ul>
            </div>
            
            <div class="action">
                <h4>Acciones:</h4>
                <ul>
                    {% for action in entry.action %}
                    <li>{{ action }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="result">
                <h4>Resultados:</h4>
                <ul>
                    {% for result in entry.result %}
                    <li>{{ result.extracted_content }}</li>
                    {% endfor %}
                </ul>
            </div>
            
            <div class="screenshot-container">
                <h4>Captura de pantalla:</h4>
                {{ entry.screenshot }}
            </div>
        </div>
        {% endfor %}
    </body>
    </html>
    """

    # Renderizar HTML
    template = Template(html_template)
    html_output = template.render(entries=formatted_entries)

    # Guardar HTML
    try:
        with open('./report/result/report.html', 'w', encoding='utf-8') as f:
            f.write(html_output)
            print("Reporte HTML generado exitosamente!")
            # Abrir el reporte automáticamente en el navegador
    #            os.system('start reporte_navegacion.html' if os.name == 'nt' else 'open reporte_navegacion.html')
    except Exception as e:
        print(f"Error al generar el Reporte HTML: {e}")
