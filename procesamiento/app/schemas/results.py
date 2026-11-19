"""Revision humana y calculo de UFC de un analisis. Los centros van en pixeles de la foto original."""
from typing import Literal
from pydantic import BaseModel,Field,model_validator

class Point(BaseModel):
    x:float=Field(ge=0,allow_inf_nan=False)
    y:float=Field(ge=0,allow_inf_nan=False)

class Review(BaseModel):
    centers:list[Point]=Field(max_length=10000)
    note:str=Field(default='',max_length=2000)

class SampleInfo(BaseModel):
    """Trazabilidad opcional: se guarda junto a la foto y aparece en el historial."""
    code:str=Field(default='',max_length=40)
    sample_type:str=Field(default='',max_length=40)
    responsible:str=Field(default='',max_length=80)
    notes:str=Field(default='',max_length=2000)

class PlateUfc(BaseModel):
    """Datos de la placa analizada. El conteo no viaja aqui: el servidor usa la revision guardada o, si no hay, el conteo automatico."""
    exponent:int=Field(ge=0,le=12)  # la placa corresponde a la dilucion 10^-exponent
    volume_ml:float=Field(gt=0,le=10,allow_inf_nan=False)
    unit:Literal['mL','g']='mL'
    duplicate_count:int|None=Field(default=None,ge=0,le=100000)  # placa duplicada de la misma dilucion, contada aparte
    count_min:int=Field(default=30,ge=0,le=10000)
    count_max:int=Field(default=300,ge=1,le=100000)
    sample:SampleInfo=SampleInfo()
    @model_validator(mode='after')
    def check_range(self):
        if self.count_min>=self.count_max:raise ValueError('El rango contable minimo debe ser menor que el maximo')
        return self
