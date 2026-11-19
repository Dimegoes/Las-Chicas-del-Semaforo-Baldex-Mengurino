import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { Icon } from '../icons.jsx'
import { fmtDateTime } from '../recent.js'
import { dilutionLabel, ufcText } from '../ufc.js'

// Una fila del historial: foto, fecha, muestra, conteo usado y UFC (si ya se calculo).
export function HistoryRow({ item }) {
  const { analysis_id: id, ufc } = item
  const count = ufc ? `${ufc.count}${ufc.duplicate_count != null ? ` y ${ufc.duplicate_count}` : ''}` : item.reviewed_count ?? item.automatic_count
  const reviewed = ufc ? ufc.count_source === 'revisado' : item.reviewed_count != null
  return (
    <Link to={`/resultado/${id}`} className="history-row">
      <img src={api.fileUrl(id, 'miniatura.jpg')} alt="" loading="lazy" />
      <span className="history-main">
        <strong>{ufc ? <>{ufcText(ufc)} <span className="unit">{ufc.unit}</span></> : 'Sin cálculo de UFC'}</strong>
        <span className="muted small">{count} colonias{reviewed ? ' (revisado)' : ''}{ufc ? ` · dilución ${dilutionLabel(ufc.exponent)} · ${ufc.volume_ml} mL` : ''}</span>
        <span className="muted small">{fmtDateTime(item.analyzed_at)}{ufc?.sample?.code ? ` · ${ufc.sample.code}` : ''}{ufc?.sample?.sample_type ? ` · ${ufc.sample.sample_type}` : ''}</span>
      </span>
      <Icon name="chevron" />
    </Link>
  )
}

export default function History() {
  const [items, setItems] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let alive = true
    api.history().then((list) => alive && setItems(list)).catch((e) => alive && setError(e.message))
    return () => { alive = false }
  }, [])

  return (
    <div className="stack">
      <div className="history-head">
        <div>
          <h2 className="page-title">Historial</h2>
          <p className="muted small">Análisis guardados en este servidor, del más reciente al más antiguo.</p>
        </div>
        <a className="btn btn-ghost" href={api.historyCsvUrl()} download="historial_ufc.csv"><Icon name="download" size={20} /> CSV</a>
      </div>
      {error && <p className="alert" role="alert">{error}</p>}
      {!items && !error && <p className="muted">Cargando historial…</p>}
      {items?.length === 0 && <p className="muted">Todavía no hay análisis guardados. <Link to="/analizar">Analiza una placa</Link>.</p>}
      {items?.length > 0 && (
        <ul className="history-list">
          {items.map((item) => <li key={item.analysis_id}><HistoryRow item={item} /></li>)}
        </ul>
      )}
    </div>
  )
}
