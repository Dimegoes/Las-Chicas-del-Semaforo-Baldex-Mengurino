"""En desarrollo: muestras con varias diluciones. Disponibles en /docs; la PWA aun no los consume."""
from fastapi import APIRouter,Depends,HTTPException
from app.dependencies import get_samples
from app.schemas.samples import SampleIn
from app.services.samples import SampleNotFound,SampleRepository
router=APIRouter(tags=['Muestras (en desarrollo)'])

def not_found():return HTTPException(404,'Muestra no encontrada')

@router.get('/samples')
def list_samples(samples:SampleRepository=Depends(get_samples)):
    return samples.list()

@router.post('/samples',status_code=201)
def create_sample(data:SampleIn,samples:SampleRepository=Depends(get_samples)):
    return samples.create(data)

@router.get('/samples/{ident}')
def get_sample(ident:int,samples:SampleRepository=Depends(get_samples)):
    try:return samples.get(ident)
    except SampleNotFound:raise not_found() from None

@router.put('/samples/{ident}')
def update_sample(ident:int,data:SampleIn,samples:SampleRepository=Depends(get_samples)):
    try:return samples.update(ident,data)
    except SampleNotFound:raise not_found() from None

@router.delete('/samples/{ident}',status_code=204)
def delete_sample(ident:int,samples:SampleRepository=Depends(get_samples)):
    try:samples.delete(ident)
    except SampleNotFound:raise not_found() from None
