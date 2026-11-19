import { describe, it, expect, vi } from 'vitest'
import { renderToStaticMarkup } from 'react-dom/server'
import { MemoryRouter } from 'react-router-dom'
import { HealthContext } from '../health.js'
vi.mock('../api.js', () => ({api:{}, AccessDenied:class extends Error {}}))
import Analyze from './Analyze.jsx'
import { EngineStatus } from './Home.jsx'
const render = (element, health) => renderToStaticMarkup(
  <MemoryRouter><HealthContext.Provider value={health}>{element}</HealthContext.Provider></MemoryRouter>
)
describe('Conteo con IA', () => {
  it('muestra disponibilidad de IA y no ofrece selector de motores', () => {
    const health = {status:'ok', engines:['hybrid'], device:'CPU'}
    expect(render(<EngineStatus />, health)).toContain('Motor IA · CPU')
    expect(render(<Analyze />, health)).not.toContain('Motor de conteo')
  })
  it('explica el bloqueo si el modelo no cargó', () => {
    const health = {status:'ok', engines:[], ready:false}
    expect(render(<EngineStatus />, health)).toContain('IA no disponible')
    const page = render(<Analyze />, health)
    expect(page).toContain('El modelo IA no está disponible')
    expect(page).toMatch(/disabled=""[^>]*>Analizar placa/)
  })
})
