"""Metricas del conteo frente a anotaciones de referencia."""
import statistics

def match_centers(detections, boxes):
    adjacency=[]
    for d in detections:
        adjacency.append([i for i,b in enumerate(boxes) if b['x']<=d['x']<=b['x']+b['width'] and b['y']<=d['y']<=b['y']+b['height']])
    assigned={}
    def visit(pred,seen):
        for gt in adjacency[pred]:
            if gt in seen: continue
            seen.add(gt)
            if gt not in assigned or visit(assigned[gt],seen):
                assigned[gt]=pred
                return True
        return False
    return sum(visit(i,set()) for i in range(len(detections)))

def summarize(rows):
    n=len(rows)
    matched=sum(r['matched_centers'] for r in rows)
    predicted=sum(r['predicted'] for r in rows)
    reference=sum(r['reference'] for r in rows)
    return {'n':n,'mae_colonies':round(statistics.mean(r['absolute_error'] for r in rows),3),
        'bias_colonies':round(statistics.mean(r['predicted']-r['reference'] for r in rows),3),
        'median_absolute_error':statistics.median(r['absolute_error'] for r in rows),
        'within_10_percent_or_2_colonies':sum(r['absolute_error']<=max(2,.10*r['reference']) for r in rows),
        'seconds_mean':round(statistics.mean(r['seconds'] for r in rows),3),
        'center_in_box_precision':round(matched/predicted,4) if predicted else None,
        'center_in_box_recall':round(matched/reference,4) if reference else None,
        'localization_note':'Correspondencia uno a uno: centro predicho dentro de caja AGAR. No equivale a mAP/IoU.'}
