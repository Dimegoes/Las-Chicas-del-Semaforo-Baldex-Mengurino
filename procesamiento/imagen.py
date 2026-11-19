"""Lectura de fotografias y delimitacion geometrica de placas para el motor IA."""
from __future__ import annotations
from pathlib import Path
import math
import cv2
import numpy as np
from PIL import Image

def read_image(path: str | Path) -> np.ndarray:
    # Keep stored pixel orientation, matching AGAR coordinates. No automatic EXIF rotation.
    with Image.open(path) as im:
        if im.width * im.height > 60_000_000:
            raise ValueError('Imagen demasiado grande (limite: 60 megapixeles).')
        rgb = np.asarray(im.convert('RGB'))
    if min(rgb.shape[:2]) < 64:
        raise ValueError('La imagen debe medir al menos 64 x 64 pixeles.')
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

def save_image(path: Path, array: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ok, encoded = cv2.imencode(path.suffix, array)
    if not ok:
        raise ValueError(f'No se pudo codificar {path}')
    encoded.tofile(str(path))

def locate_plate(bgr: np.ndarray):
    h, w = bgr.shape[:2]
    scale = min(1.0, 700 / max(h, w))
    small = cv2.resize(bgr, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 1.2)
    sh, sw = gray.shape
    # Perspective and cropped edges make a fitted ellipse more faithful than a circle.
    edges = cv2.Canny(gray,30,90)
    contours,_ = cv2.findContours(edges,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
    ellipses=[]
    for contour in contours:
        if len(contour)<100:
            continue
        (ex,ey),(aw,ah),angle=cv2.fitEllipse(contour)
        if min(aw,ah)<min(sh,sw)*.52 or max(aw,ah)>min(sh,sw)*1.18 or min(aw,ah)/max(aw,ah)<.70:
            continue
        center_distance=math.hypot((ex-sw/2)/sw,(ey-sh/2)/sh)
        if center_distance>.25:
            continue
        points=contour[:,0,:].astype(np.float32)-[ex,ey]
        theta=math.radians(angle)
        u=(points[:,0]*math.cos(theta)+points[:,1]*math.sin(theta))/(aw/2)
        v=(-points[:,0]*math.sin(theta)+points[:,1]*math.cos(theta))/(ah/2)
        residual=float(np.median(np.abs(np.sqrt(u*u+v*v)-1)))
        bins=np.unique(np.int32((np.arctan2(v,u)+math.pi)*36/(2*math.pi)))
        area_fraction=math.pi*aw*ah/4/(sw*sh)
        if residual<.018 and len(bins)>=25 and .25<area_fraction<.90:
            ellipses.append((area_fraction-center_distance*.12,ex,ey,aw/2,ah/2,angle))
    if ellipses:
        _,ex,ey,ra,rb,angle=max(ellipses)
        return (ex/scale,ey/scale,ra/scale,rb/scale,angle),'ellipse'
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1.2, minDist=min(sh,sw)*0.3,
                               param1=65, param2=35, minRadius=int(min(sh,sw)*0.28),
                               maxRadius=int(min(sh,sw)*0.52))
    choices = []
    if circles is not None:
        for x,y,r in circles[0]:
            center_distance = math.hypot((float(x)-sw/2)/sw, (float(y)-sh/2)/sh)
            if center_distance < 0.25 and x-r > -sw*.08 and x+r < sw*1.08 and y-r > -sh*.08 and y+r < sh*1.08:
                choices.append((float(r)/min(sh,sw) - center_distance*.8, float(x),float(y),float(r)))
    if choices:
        _,x,y,r = max(choices)
        return (x/scale,y/scale,r/scale,r/scale,0.), 'hough'
    # A visible fallback is never treated as a reliable plate detection.
    return (w/2,h/2,min(w,h)*.43,min(w,h)*.43,0.), 'fallback'
