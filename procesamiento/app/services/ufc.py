"""Calculo de UFC/mL o UFC/g a partir de diluciones y conteos de placa."""
import math
from decimal import ROUND_HALF_UP,Decimal
from app.schemas.samples import UfcInput

def redondear(value):
    """Dos cifras significativas, como se informa un recuento en placa (FDA BAM, cap. 3); el 5 redondea hacia arriba
    (46 500 -> 47 000), no al par como hace Python por defecto."""
    if not value:return 0
    d=Decimal(repr(value))
    return float(d.quantize(Decimal(1).scaleb(d.adjusted()-1),rounding=ROUND_HALF_UP))

def calcular_ufc(data:UfcInput):
    """UFC por mL o g = promedio de placas x 10^exponente / volumen sembrado.
    Usa las diluciones cuyo promedio cae en el rango contable; si ninguna cae, estima con la mas cercana."""
    rows=[]
    for d in data.dilutions:
        counts=[p.count for p in (d.plate_a,d.plate_b) if p.count is not None]
        if not counts:continue
        mean=sum(counts)/len(counts)
        rows.append({'exponent':d.exponent,'volume_ml':d.volume_ml,'counts':counts,'mean':mean,'plates':len(counts),
                     'per_unit':mean*10**d.exponent/d.volume_ml})
    if not rows:return None
    warnings=[]
    lo,hi=data.count_min,data.count_max
    valid=[r for r in rows if lo<=r['mean']<=hi]
    if valid:
        used=valid
    elif all(r['mean']==0 for r in rows):
        low=min(rows,key=lambda r:r['exponent'])
        limit=10**low['exponent']/low['volume_ml']
        return {'value':0,'reported':0,'log10':None,'unit':'UFC/'+data.unit,'in_range':False,'dilutions_used':[],'rows':rows,
                'detection_limit':limit,'warnings':[f'Sin colonias en ninguna placa: reportar como < {limit:.3g} UFC/{data.unit}.']}
    else:
        nonzero=[r for r in rows if r['mean']>0] or rows
        used=[min(nonzero,key=lambda r:lo-r['mean'] if r['mean']<lo else r['mean']-hi)]
        warnings.append(f'Ninguna dilucion tiene un promedio entre {lo} y {hi} colonias: el resultado es una estimacion.')
    if any(r['plates']<2 for r in used):warnings.append('Alguna dilucion usada tiene una sola placa contada.')
    value=sum(r['per_unit'] for r in used)/len(used)
    return {'value':value,'reported':redondear(value),'log10':round(math.log10(value),2) if value>0 else None,
            'unit':'UFC/'+data.unit,'in_range':bool(valid),'dilutions_used':[r['exponent'] for r in used],
            'rows':rows,'warnings':warnings}
