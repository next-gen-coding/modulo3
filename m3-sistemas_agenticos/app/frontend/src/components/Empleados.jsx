import { useState, useEffect } from 'react'
import FormEmpleado from './FormEmpleado'
import DirectorioEmpleados from './DirectorioEmpleados'
import VacacionesModal from './VacacionesModal'

function Empleados({ onCambio }) {
  const [empleados, setEmpleados] = useState([])
  const [departamentos, setDepartamentos] = useState([])
  const [mostrarForm, setMostrarForm] = useState(false)
  const [empleadoEditar, setEmpleadoEditar] = useState(null)
  const [mensaje, setMensaje] = useState(null)
  const [empleadoVacaciones, setEmpleadoVacaciones] = useState(null)
  const [busqueda, setBusqueda] = useState('')
  const [filtradoDept, setFiltradoDept] = useState('')

  useEffect(() => {
    cargarDatos()
  }, [])

  function cargarDatos() {
    Promise.all([
      fetch('/api/empleados').then(r => r.json()),
      fetch('/api/departamentos').then(r => r.json())
    ]).then(([emps, depts]) => {
      setEmpleados(emps)
      setDepartamentos(depts)
    })
  }

  function manejarFormGuardar(datos) {
    const metodo = empleadoEditar ? 'PUT' : 'POST'
    const url = empleadoEditar
      ? `/api/empleados/${empleadoEditar.id}`
      : '/api/empleados'

    fetch(url, {
      method: metodo,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datos)
    })
      .then(r => {
        if (!r.ok) return r.json().then(e => Promise.reject(e))
        return r.json()
      })
      .then(() => {
        setMensaje({ tipo: 'exito', texto: empleadoEditar ? 'Empleado actualizado' : 'Empleado registrado' })
        setMostrarForm(false)
        setEmpleadoEditar(null)
        cargarDatos()
        setTimeout(() => setMensaje(null), 3000)
      })
      .catch(err => {
        setMensaje({ tipo: 'error', texto: err.detail || 'Error al guardar' })
        setTimeout(() => setMensaje(null), 5000)
      })
  }

  function manejarBaja(id) {
    if (!confirm('¿Dar de baja a este empleado?')) return

    fetch(`/api/empleados/${id}/baja`, { method: 'POST' })
      .then(r => r.json())
      .then(() => {
        setMensaje({ tipo: 'exito', texto: 'Empleado dado de baja' })
        cargarDatos()
        setTimeout(() => setMensaje(null), 3000)
      })
      .catch(err => {
        setMensaje({ tipo: 'error', texto: err.detail || 'Error' })
        setTimeout(() => setMensaje(null), 5000)
      })
  }

  return (
    <div>
      {mensaje && (
        <div className={`mensaje mensaje-${mensaje.tipo}`} data-testid={`mensaje-${mensaje.tipo}`}>
          {mensaje.texto}
        </div>
      )}

      <div className="seccion">
        <h2>Registrar Empleado</h2>
        {!mostrarForm && (
          <button onClick={() => { setMostrarForm(true); setEmpleadoEditar(null) }}>
            Nuevo Empleado
          </button>
        )}

        {mostrarForm && (
          <FormEmpleado
            departamentos={departamentos}
            empleado={empleadoEditar}
            onGuardar={(datos) => {
              manejarFormGuardar(datos)
            }}
            onCancelar={() => {
              setMostrarForm(false)
              setEmpleadoEditar(null)
            }}
          />
        )}
      </div>

      <div className="seccion">
        <h2>Directorio de Empleados</h2>
        <div className="formulario" style={{ marginBottom: '15px' }}>
          <div className="grupo-form">
            <label>Buscar por nombre o correo</label>
            <input
              type="text"
              placeholder="Buscar..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value.toLowerCase())}
              data-testid="buscar-empleados"
            />
          </div>
          <div className="grupo-form">
            <label>Filtrar por departamento</label>
            <select
              value={filtradoDept}
              onChange={(e) => setFiltradoDept(e.target.value)}
              data-testid="filtro-departamento"
            >
              <option value="">Todos</option>
              {departamentos.map(d => (
                <option key={d} value={d}>{d}</option>
              ))}
            </select>
          </div>
        </div>

        <DirectorioEmpleados
          empleados={empleados}
          busqueda={busqueda}
          filtradoDept={filtradoDept}
          onEditar={(emp) => {
            setEmpleadoEditar(emp)
            setMostrarForm(true)
          }}
          onBaja={(id) => manejarBaja(id)}
          onVacaciones={(emp) => setEmpleadoVacaciones(emp)}
        />
      </div>

      {empleadoVacaciones && (
        <VacacionesModal
          empleado={empleadoVacaciones}
          onCerrar={() => setEmpleadoVacaciones(null)}
          onExito={(msg) => {
            setMensaje({ tipo: 'exito', texto: msg })
            cargarDatos()
            setTimeout(() => setMensaje(null), 5000)
          }}
          onError={(msg) => {
            setMensaje({ tipo: 'error', texto: msg })
            setTimeout(() => setMensaje(null), 5000)
          }}
        />
      )}
    </div>
  )
}

export default Empleados
