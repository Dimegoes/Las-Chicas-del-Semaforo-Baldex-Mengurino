"""Servicio de conteo con IA y estado de disponibilidad del modelo."""
import asyncio,os
from datetime import datetime
from imagen import save_image
from contador_hibrido import HybridCounter,NeuralConfig,write_hybrid_result

def default_hybrid_factory():
    import torch
    device=os.environ.get('IA_DEVICE','auto').lower()
    if device not in ('auto','cpu','cuda'):
        raise ValueError('IA_DEVICE debe ser auto, cpu o cuda')
    if device=='auto':device='cuda' if torch.cuda.is_available() else 'cpu'
    return HybridCounter(NeuralConfig(device=device,batch_size=1 if device=='cpu' else 8))

class EngineUnavailable(Exception):pass

class EngineService:
    def __init__(self,hybrid_factory=default_hybrid_factory,use_hybrid=True):
        self.hybrid_factory=hybrid_factory;self.use_hybrid=use_hybrid
        self.model=None;self.error=None if use_hybrid else 'Carga del modelo desactivada'
        self.lock=None

    async def start(self):
        # The lock is created inside the server's event loop; it serializes GPU use between requests.
        self.lock=asyncio.Lock()
        if not self.use_hybrid:return
        try:self.model=await asyncio.to_thread(self.hybrid_factory)
        except Exception as exc:  # missing .venv-neural, weights or CUDA
            self.error=f'{type(exc).__name__}: {exc}'
            print('Motor IA no disponible. '+self.error,flush=True)

    def stop(self):self.model=None

    @property
    def engines(self):return ['hybrid'] if self.model else []

    @property
    def device(self):return getattr(self.model,'hardware',None)

    def resolve(self,engine):
        if engine not in ('auto','hybrid'):raise ValueError('Motor: auto o hybrid')
        if not self.model:raise EngineUnavailable('El modelo IA no esta disponible. Revisa la instalacion y reinicia el servidor.')
        return 'hybrid'

    async def analyze(self,bgr,engine,folder):
        """Cuenta, exporta los archivos del motor y guarda la foto original para la revision manual."""
        async with self.lock:
            fn=self.model.count
            result,debug=await asyncio.to_thread(fn,bgr)
            # La fecha va dentro del JSON: la fecha del archivo cambia si se copia o restaura la carpeta de resultados.
            result['analyzed_at']=datetime.now().isoformat(timespec='seconds')
            writer=write_hybrid_result
            await asyncio.to_thread(writer,result,debug,folder,'foto')
            await asyncio.to_thread(save_image,folder/'foto_original.jpg',bgr)
        return result
