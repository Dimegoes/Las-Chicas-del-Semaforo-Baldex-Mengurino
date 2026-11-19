"""Archivos de cada analisis. La prediccion automatica no se modifica; la revision humana y el calculo de UFC se guardan aparte.

Cada analisis vive en resultados/api/<id>/ (foto, conteo, revision.json, ufc.json). Ademas, historial.jsonl registra cada
calculo de UFC guardado, sin sobrescribir los anteriores, para poder auditar cambios."""
from datetime import datetime
from pathlib import Path
import csv,io,json,threading,uuid
from PIL import Image
from app.config import RESULT_FILES
from app.schemas.results import PlateUfc
from app.schemas.samples import Dilution,Plate,UfcInput
from app.services.ufc import calcular_ufc

class ResultNotFound(Exception):pass

THUMB_SIDE=360
HISTORY_LOG='historial.jsonl'
CSV_COLUMNS=(('fecha_analisis','analyzed_at'),('id_analisis','analysis_id'),('codigo_muestra','code'),('tipo_muestra','sample_type'),
    ('responsable','responsible'),('colonias_automatico','automatic_count'),('colonias_revisado','reviewed_count'),
    ('colonias_usadas','count'),('placa_duplicada','duplicate_count'),('dilucion','dilution'),('volumen_sembrado_ml','volume_ml'),
    ('unidad','unit'),('ufc','value'),('ufc_reportado','reported'),('log10_ufc','log10'),('en_rango_contable','in_range'),
    ('advertencias','warnings'),('observaciones','notes'),('ufc_guardado','saved_at'))

def _valid_id(analysis_id):
    return len(analysis_id)==32 and all(c in '0123456789abcdef' for c in analysis_id)

def _iso(timestamp):return datetime.fromtimestamp(timestamp).isoformat(timespec='seconds')

def _analyzed_at(original,path):
    """Fecha guardada en el resultado; los analisis anteriores a ese campo usan la fecha del archivo."""
    return original.get('analyzed_at') or _iso(path.stat().st_mtime)

class ResultStore:
    def __init__(self,root):
        self.root=Path(root);self._lock=threading.Lock()

    def new_folder(self):
        ident=uuid.uuid4().hex
        return ident,self.root/ident

    def path(self,analysis_id,name):
        if not _valid_id(analysis_id) or name not in RESULT_FILES:raise ResultNotFound
        path=self.root/analysis_id/name
        if name=='miniatura.jpg' and not path.is_file():self._make_thumbnail(analysis_id,path)
        if not path.is_file():raise ResultNotFound
        return path

    def _make_thumbnail(self,analysis_id,path):
        """Miniatura para el historial: la foto original puede pesar varios MB."""
        original=self.root/analysis_id/'foto_original.jpg'
        with self._lock:
            if path.is_file() or not original.is_file():return
            with Image.open(original) as image:
                image.thumbnail((THUMB_SIDE,THUMB_SIDE))
                image.convert('RGB').save(path,'JPEG',quality=82)

    def _read(self,analysis_id,name):
        return json.loads(self.path(analysis_id,name).read_text(encoding='utf-8'))

    def _read_optional(self,analysis_id,name):
        try:return self._read(analysis_id,name)
        except ResultNotFound:return None

    def save_review(self,analysis_id,review):
        original=self._read(analysis_id,'foto_resultado.json')
        w=original['image_size']['width'];h=original['image_size']['height']
        if any(p.x>=w or p.y>=h for p in review.centers):raise ValueError('Centro fuera de imagen')
        record={'automatic_count':original['count'],'reviewed_count':len(review.centers),**review.model_dump(),
                'review_type':'human_submitted_centers_not_model_prediction'}
        (self.root/analysis_id/'revision.json').write_text(json.dumps(record,indent=2,ensure_ascii=False),encoding='utf-8')
        return record

    def save_ufc(self,analysis_id,data:PlateUfc):
        """Calcula UFC con el conteo guardado de esta placa (revisado si existe) y lo deja junto a la foto y en el historial."""
        original=self._read(analysis_id,'foto_resultado.json')
        review=self._read_optional(analysis_id,'revision.json')
        count=review['reviewed_count'] if review else original['count']
        dilution=Dilution(exponent=data.exponent,volume_ml=data.volume_ml,
                          plate_a=Plate(count=count,analysis_id=analysis_id),plate_b=Plate(count=data.duplicate_count))
        result=calcular_ufc(UfcInput(dilutions=[dilution],unit=data.unit,count_min=data.count_min,count_max=data.count_max))
        record={'analysis_id':analysis_id,'saved_at':datetime.now().isoformat(timespec='seconds'),
                'analyzed_at':_analyzed_at(original,self.path(analysis_id,'foto_resultado.json')),
                'count':count,'count_source':'revisado' if review else 'automatico','automatic_count':original['count'],
                'reviewed_count':review['reviewed_count'] if review else None,**data.model_dump(),
                'formula':f'UFC/{data.unit} = promedio de colonias x 10^{data.exponent} / {data.volume_ml:g} mL','result':result}
        with self._lock:
            (self.root/analysis_id/'ufc.json').write_text(json.dumps(record,indent=2,ensure_ascii=False),encoding='utf-8')
            with open(self.root/HISTORY_LOG,'a',encoding='utf-8') as log:log.write(json.dumps(record,ensure_ascii=False)+'\n')
        return record

    def history(self,limit=500):
        """Todos los analisis guardados, del mas reciente al mas antiguo, con su revision y su UFC si existen."""
        if not self.root.is_dir():return []
        out=[]
        for path in self.root.glob('*/foto_resultado.json'):
            ident=path.parent.name
            if not _valid_id(ident):continue
            try:
                original=self._read(ident,'foto_resultado.json')
                review=self._read_optional(ident,'revision.json')
                ufc=self._read_optional(ident,'ufc.json')
                summary=ufc and {'value':ufc['result']['value'],'reported':ufc['result'].get('reported'),
                                 'unit':ufc['result']['unit'],'in_range':ufc['result']['in_range'],'exponent':ufc['exponent'],
                                 'volume_ml':ufc['volume_ml'],'count':ufc['count'],'count_source':ufc['count_source'],
                                 'duplicate_count':ufc['duplicate_count'],'detection_limit':ufc['result'].get('detection_limit'),
                                 'log10':ufc['result'].get('log10'),'warnings':ufc['result']['warnings'],
                                 'sample':ufc['sample'],'saved_at':ufc['saved_at']}
                analyzed_at=_analyzed_at(original,path)
            except (OSError,ResultNotFound,ValueError,KeyError,TypeError):continue  # archivo borrado, corrupto o a medio escribir
            out.append({'analysis_id':ident,'analyzed_at':analyzed_at,'automatic_count':original.get('count'),
                        'reviewed_count':review['reviewed_count'] if review else None,'ufc':summary})
        out.sort(key=lambda item:item['analyzed_at'],reverse=True)
        return out[:limit]

    def history_csv(self):
        """Historial como CSV (UTF-8 con BOM para que Excel respete las tildes)."""
        buffer=io.StringIO()
        writer=csv.writer(buffer)
        writer.writerow([name for name,_ in CSV_COLUMNS])
        for item in self.history(limit=100000):
            ufc=item['ufc'] or {}
            sample=ufc.get('sample') or {}
            row={**item,**{k:v for k,v in ufc.items() if k!='sample'},**sample,
                 'dilution':f"10^-{ufc['exponent']}" if ufc else '','warnings':' | '.join(ufc.get('warnings') or []),
                 'in_range':('si' if ufc.get('in_range') else 'no') if ufc else ''}
            writer.writerow(['' if row.get(key) is None else row.get(key) for _,key in CSV_COLUMNS])
        return '﻿'+buffer.getvalue()
