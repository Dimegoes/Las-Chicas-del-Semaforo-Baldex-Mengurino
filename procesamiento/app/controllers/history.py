"""Historial de analisis guardados en este servidor: foto, conteo, revision y UFC."""
from fastapi import APIRouter,Depends,Query
from fastapi.responses import Response
from app.dependencies import get_results
from app.services.results import ResultStore
router=APIRouter(prefix='/history',tags=['Historial'])

@router.get('')
def history(limit:int=Query(200,ge=1,le=5000),results:ResultStore=Depends(get_results)):
    return results.history(limit)

@router.get('/csv')
def history_csv(results:ResultStore=Depends(get_results)):
    return Response(results.history_csv(),media_type='text/csv; charset=utf-8',
                    headers={'Content-Disposition':'attachment; filename="historial_ufc.csv"'})
