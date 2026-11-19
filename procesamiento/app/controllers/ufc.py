"""Calculo de UFC sin guardar nada: la PWA lo usa para mostrar el resultado mientras se llenan los datos."""
from fastapi import APIRouter
from app.schemas.samples import UfcInput
from app.services.ufc import calcular_ufc
router=APIRouter(tags=['Calculo de UFC'])

@router.post('/ufc')
def ufc(data:UfcInput):
    return calcular_ufc(data)
