"""Informe del conteo IA sobre imagenes AGAR conocidas."""
from pathlib import Path
import csv,html,json
ROOT=Path(__file__).resolve().parent/'resultados'

def main():
    folder=ROOT/'hibrido_v0_3'
    info=json.loads((folder/'resumen.json').read_text(encoding='utf-8'))
    with (folder/'metricas.csv').open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
    overall=info['overall']
    summary=f'''# Avance del conteo con IA

- Fotografías AGAR conocidas: {overall['n']}.
- Error absoluto medio: {overall['mae_colonies']:.2f} colonias por foto.
- Tiempo medio: {overall['seconds_mean']:.2f} segundos con el modelo cargado en {info['hardware']}.
- Carga inicial: {info['model_load_seconds']:.2f} segundos.

Los pesos de los autores se ajustaron con AGAR. Puede existir solapamiento con entrenamiento: esta evaluación no demuestra generalización independiente. Se requieren fotos propias y revisión humana. El emparejamiento centro/caja no evalúa la precisión de las máscaras.
'''
    (ROOT/'RESUMEN_HIBRIDO.md').write_text(summary,encoding='utf-8')
    fields=['image','reference','predicted','absolute_error','matched_centers','extra','missed','seconds']
    titles=['Foto','Referencia','IA','Error absoluto','Coincidencias','Extras','Omisiones','Segundos']
    table=''.join('<tr>'+''.join('<td>'+html.escape(r[k])+'</td>' for k in fields)+'</tr>' for r in rows)
    page='<!doctype html><html lang="es"><meta charset="utf-8"><title>Conteo de colonias con IA</title><style>body{font:16px Arial;max-width:1100px;margin:40px auto;color:#163b32}table{border-collapse:collapse;width:100%}th,td{padding:10px;border-bottom:1px solid #ddd;text-align:left}</style><h1>Conteo de colonias con IA</h1><p>'+html.escape(summary).replace('\n','<br>')+'</p><table><thead><tr>'+''.join('<th>'+t+'</th>' for t in titles)+'</tr></thead><tbody>'+table+'</tbody></table></html>'
    (ROOT/'INFORME_HIBRIDO.html').write_text(page,encoding='utf-8')

if __name__=='__main__':main()
