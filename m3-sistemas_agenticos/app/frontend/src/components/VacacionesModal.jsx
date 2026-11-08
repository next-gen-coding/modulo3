import { useState, useEffect } from 'react'

function VacacionesModal({ empleado, onCerrar, onExito, onError }) {
  const [resumen, setResumen] = useState(null)
  const [fechaInicio, setFechaInicio] = useState('')
  const [fechaFin, setFechaFin] = useState('')
  const [cargando, setCargando] = useState(true)
  const [mensaje, setMensaje] = useState(null)

  useEffect(() => {
    cargarResumen()
  }, [empleado])

  function cargarResumen() {
    const anio = new Date().getFullYear()
    fetch(`/api/empleados/${empleado.id}/vacaciones?anio=${anio}`)
      .then(r => r.json())
      .then(data => {
        setResumen(data)
        setCargando(false)
      })
      .catch(err => {
        console.error('Error cargando vacaciones:', err)
        setCargando(false)
      })
  }

  function manejarSolicitud(e) {
    e.preventDefault()

    if (!fechaInicio || !fechaFin) {
      setMensaje({ tipo: 'error', texto: 'Completa ambas fechas' })
      return
    }

    fetch(`/api/empleados/${empleado.id}/vacaciones`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        fecha_inicio: fechaInicio,
        fecha_fin: fechaFin
      })
    })
      .then(r => {
        if (!r.ok) return r.json().then(e => Promise.reject(e))
        return r.json()
      })
      .then(data => {
        const msg = `Solicitud registrada: ${data.dias_habiles} días hábiles. Te quedan ${data.dias_disponibles} días disponibles.`
        setMensaje({ tipo: 'exito', texto: msg })
        setFechaInicio('')
        setFechaFin('')
        setTimeout(() => {
          cargarResumen()
          setMensaje(null)
        }, 1000)
      })
      .catch(err => {
        const msgError = err.detail || 'Error al registrar solicitud'
        setMensaje({ tipo: 'error', texto: msgError })
      })
  }

  if (cargando) {
    return (
      <div className="modal-overlay" onClick={onCerrar}>
        <div className="modal" onClick={(e) => e.stopPropagation()}>
          <h2>Cargando...</h2>
        </div>
      </div>
    )
  }

  return (
    <div className="modal-overlay" onClick={onCerrar}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-cerrar" onClick={onCerrar}>×</button>
        <h2 className="modal-titulo">Vacaciones - {empleado.nombre}</h2>

        {resumen && (
          <div className="resumen-vacaciones">
            <p>Año: <strong>{resumen.anio}</strong></p>
            <p>Días disponibles: <span className="numero" data-testid="vacaciones-disponibles">{resumen.dias_disponibles}</span> de {resumen.dias_por_anio}</p>
          </div>
        )}

        {mensaje && (
          <div className={`mensaje mensaje-${mensaje.tipo}`} data-testid={`mensaje-${mensaje.tipo}`}>
            {mensaje.texto}
          </div>
        )}

        <form onSubmit={manejarSolicitud} className="formulario" style={{ marginBottom: '20px' }}>
          <div className="grupo-form">
            <label>Fecha de Inicio</label>
            <input
              type="date"
              value={fechaInicio}
              onChange={(e) => setFechaInicio(e.target.value)}
              data-testid="vacaciones-fecha-inicio"
              required
            />
          </div>

          <div className="grupo-form">
            <label>Fecha de Fin</label>
            <input
              type="date"
              value={fechaFin}
              onChange={(e) => setFechaFin(e.target.value)}
              data-testid="vacaciones-fecha-fin"
              required
            />
          </div>

          <div style={{ gridColumn: '1 / -1' }}>
            <button type="submit" data-testid="vacaciones-solicitar">
              Solicitar Vacaciones
            </button>
          </div>
        </form>

        {resumen && resumen.solicitudes.length > 0 && (
          <div>
            <h3>Solicitudes Registradas</h3>
            <table className="tabla" data-testid="tabla-vacaciones">
              <thead>
                <tr>
                  <th>Desde</th>
                  <th>Hasta</th>
                  <th>Días Hábiles</th>
                </tr>
              </thead>
              <tbody>
                {resumen.solicitudes.map(v => (
                  <tr key={v.id} data-testid={`fila-vacaciones-${v.id}`}>
                    <td>{v.fecha_inicio}</td>
                    <td>{v.fecha_fin}</td>
                    <td data-testid={`dias-vacaciones-${v.id}`}>{v.dias_habiles}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {resumen && resumen.solicitudes.length === 0 && (
          <div className="sin-resultados">
            No hay solicitudes de vacaciones registradas
          </div>
        )}
      </div>
    </div>
  )
}

export default VacacionesModal
