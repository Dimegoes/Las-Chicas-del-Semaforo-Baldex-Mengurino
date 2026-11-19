// Presentacion del calculo de UFC. El servidor calcula y redondea (campo `reported`, 2 cifras significativas);
// aqui solo se arma el texto que ve el usuario.
const SUP = { '-': '⁻', 0: '⁰', 1: '¹', 2: '²', 3: '³', 4: '⁴', 5: '⁵', 6: '⁶', 7: '⁷', 8: '⁸', 9: '⁹' }

export const sup = (n) => String(n).split('').map((c) => SUP[c] ?? c).join('')

export const fmtNum = (v, digits = 2) => Number(v).toLocaleString('es-PE', { maximumFractionDigits: digits })

// La placa corresponde a la dilucion 10^-n; el factor que multiplica al conteo es 10^n.
export const dilutionLabel = (exp) => (exp === 0 ? '10⁰ (sin diluir)' : `10${sup(-exp)}`)

// 47000 -> "4.7 × 10⁴" (formato numérico de Perú) (2 cifras, como se informa un recuento en placa).
export function sci(value) {
  if (!value) return '0'
  let exp = Math.floor(Math.log10(Math.abs(value)))
  let mantissa = Number((value / 10 ** exp).toFixed(1))
  if (mantissa >= 10) { mantissa /= 10; exp += 1 }
  const m = mantissa.toLocaleString('es-PE', { minimumFractionDigits: 1, maximumFractionDigits: 1 })
  return `${m} × 10${sup(exp)}`
}

// Resultado listo para mostrar: valor, o "< limite" cuando ninguna placa tiene colonias.
export function ufcText(result) {
  if (!result) return ''
  if (!result.value && result.detection_limit) return `< ${sci(result.detection_limit)}`
  return sci(result.reported ?? result.value)
}

// "UFC/mL = (45 + 48) ÷ 2 × 10² ÷ 0.1 mL" con los numeros de esta placa.
export function formulaText(row, unit) {
  if (!row) return ''
  const counts = row.counts || []
  const mean = counts.length > 1 ? `(${counts.join(' + ')}) ÷ ${counts.length}` : String(counts[0] ?? row.mean)
  return `UFC/${unit} = ${mean} × 10${sup(row.exponent)} ÷ ${fmtNum(row.volume_ml, 3)} mL`
}
