"""Selección de dispositivo sin cargar pesos ni necesitar una GPU."""
import asyncio,os,sys,unittest
from types import SimpleNamespace
from unittest.mock import patch
from app.services.engines import default_hybrid_factory,EngineService

class DeviceTests(unittest.TestCase):
    def config_for(self,device,available):
        fake=SimpleNamespace(cuda=SimpleNamespace(is_available=lambda:available))
        with patch.dict(os.environ,{'IA_DEVICE':device}),patch.dict(sys.modules,{'torch':fake}),patch('app.services.engines.HybridCounter',side_effect=lambda cfg:cfg):
            return default_hybrid_factory()
    def test_auto_without_cuda(self):
        cfg=self.config_for('auto',False)
        self.assertEqual((cfg.device,cfg.batch_size),('cpu',1))
    def test_auto_with_cuda(self):
        cfg=self.config_for('auto',True)
        self.assertEqual((cfg.device,cfg.batch_size),('cuda',8))
    def test_forced_cpu_on_gpu_machine(self):
        self.assertEqual(self.config_for('cpu',True).device,'cpu')
    def test_invalid_device(self):
        with self.assertRaises(ValueError):self.config_for('invalid',False)
    def test_failure_keeps_classic(self):
        def fail():raise RuntimeError('no weights')
        service=EngineService(fail)
        asyncio.run(service.start())
        self.assertEqual(service.engines,['classic'])
        self.assertIn('no weights',service.error)
    def test_classic_does_not_load_torch(self):
        with patch('app.services.engines.default_hybrid_factory') as factory:
            service=EngineService(factory,use_hybrid=False)
            asyncio.run(service.start())
            factory.assert_not_called()

if __name__=='__main__':unittest.main()
