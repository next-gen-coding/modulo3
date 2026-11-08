import { useState, useEffect } from 'react'

function FormEmpleado({ departamentos, empleado, onGuardar, onCancelar }) {
  const [datos, setDatos] = useState({
    nombre: '',
    correo: '',
    puesto: '',
    departamento: departamentos[0] || '',
    fecha_ingreso: ''
  })

  useEffect(() => {
    if (empleado) {
      setDatos({
        nombre: empleado.nombre,
        puesto: empleado.puesto,
        departamento: empleado.departamento,
        correo: empleado.correo,
        fecha_ingreso: empleado.fecha_ingreso
      })
    }
  }, [empleado])

  function manejarCambio(e) {
    const { name, value } = e.target
    setDatos(d => ({ ...d, [name]: value }))
  }

  function manejarSubmit(e) {
    e.preventDefault()
    const payload = {
      nombre: datos.nombre,
      correo: datos.correo,
      puesto: datos.puesto,
      departamento: datos.departamento,
      fecha_ingreso: datos.fecha_ingreso
    }

    if (empleado) {
      delete payload.correo
      delete payload.fecha_ingreso
    }

    onGuardar(payload)
  }

  return (
    <form onSubmit={manejarSubmit} className="formulario" style={{ marginTop: '20px' }}>
      <div className="grupo-form">
        <label>Nombre</label>
        <input
          type="text"
          name="nombre"
          value={datos.nombre}
          onChange={manejarCambio}
          required
          data-testid="empleado-nombre"
        />
      </div>

      {!empleado && (
        <div className="grupo-form">
          <label>Correo</label>
          <input
            type="email"
            name="correo"
            value={datos.correo}
            onChange={manejarCambio}
            required
            data-testid="empleado-correo"
          />
        </div>
      )}

      <div className="grupo-form">
        <label>Puesto</label>
        <input
          type="text"
          name="puesto"
          value={datos.puesto}
          onChange={manejarCambio}
          required
          data-testid="empleado-puesto"
        />
      </div>

      <div className="grupo-form">
        <label>Departamento</label>
        <select
          name="departamento"
          value={datos.departamento}
          onChange={manejarCambio}
          required
          data-testid="empleado-departamento"
        >
          {departamentos.map(d => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
      </div>

      {!empleado && (
        <div className="grupo-form">
          <label>Fecha de Ingreso</label>
          <input
            type="date"
            name="fecha_ingreso"
            value={datos.fecha_ingreso}
            onChange={manejarCambio}
            required
            data-testid="empleado-fecha-ingreso"
          />
        </div>
      )}

      <div style={{ gridColumn: '1 / -1', display: 'flex', gap: '10px' }}>
        <button type="submit" data-testid="empleado-guardar">
          Guardar
        </button>
        <button type="button" onClick={onCancelar} style={{ backgroundColor: '#6c757d' }}>
          Cancelar
        </button>
      </div>
    </form>
  )
}

export default FormEmpleado
