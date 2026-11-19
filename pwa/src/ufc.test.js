import { describe, expect, it, vi } from 'vitest'
vi.mock('./api.js', () => ({ api: {} }))
import { dilutionLabel, formulaText, sci, ufcText } from './ufc.js'
import { bodyFromForm, formError, formFromRecord } from './components/UfcCalculator.jsx'

describe('presentacion de UFC', () => {
  it('escribe en notacion cientifica con dos cifras', () => {
    expect(sci(47000)).toBe('4.7 × 10⁴')
    expect(sci(99999)).toBe('1.0 × 10⁵')
    expect(sci(250)).toBe('2.5 × 10²')
    expect(sci(0)).toBe('0')
  })

  it('usa el valor redondeado del servidor y el limite de deteccion', () => {
    expect(ufcText({ value: 46500, reported: 47000 })).toBe('4.7 × 10⁴')
    expect(ufcText({ value: 0, detection_limit: 100 })).toBe('< 1.0 × 10²')
  })

  it('muestra la dilucion y la formula con los numeros de la placa', () => {
    expect(dilutionLabel(3)).toBe('10⁻³')
    expect(dilutionLabel(0)).toBe('10⁰ (sin diluir)')
    expect(formulaText({ counts: [45, 48], exponent: 2, volume_ml: 0.1 }, 'mL')).toBe('UFC/mL = (45 + 48) ÷ 2 × 10² ÷ 0.1 mL')
    expect(formulaText({ counts: [120], exponent: 3, volume_ml: 1 }, 'g')).toBe('UFC/g = 120 × 10³ ÷ 1 mL')
  })
})

describe('formulario de UFC', () => {
  it('parte de valores tipicos y recupera un calculo guardado', () => {
    expect(formFromRecord(null)).toMatchObject({ exponent: 1, volume: '0.1', unit: 'mL', duplicate: '' })
    const saved = { exponent: 3, volume_ml: 1, unit: 'g', duplicate_count: 50, count_min: 25, count_max: 250, sample: { code: 'M-1' } }
    expect(bodyFromForm(formFromRecord(saved))).toEqual({
      exponent: 3, volume_ml: 1, unit: 'g', duplicate_count: 50, count_min: 25, count_max: 250,
      sample: { code: 'M-1', sample_type: '', responsible: '', notes: '' },
    })
  })

  it('valida volumen, placa duplicada y rango antes de calcular', () => {
    const ok = formFromRecord(null)
    expect(formError(ok)).toBe('')
    expect(formError({ ...ok, volume: '0' })).toMatch(/volumen/)
    expect(formError({ ...ok, volume: '0,1' })).toBe('')
    expect(formError({ ...ok, duplicate: '4.5' })).toMatch(/duplicada/)
    expect(formError({ ...ok, min: '300', max: '30' })).toMatch(/rango/)
  })
})
