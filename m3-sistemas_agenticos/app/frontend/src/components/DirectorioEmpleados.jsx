function DirectorioEmpleados({ empleados, busqueda, filtradoDept, onEditar, onBaja, onVacaciones }) {
  const filtrados = empleados.filter(e => {
    const cumpleBusqueda = !busqueda ||
      e.nombre.toLowerCase().includes(busqueda) ||
      e.correo.toLowerCase().includes(busqueda)

    const cumpleFiltro = !filtradoDept || e.departamento === filtradoDept

    return cumpleBusqueda && cumpleFiltro
  })

  if (filtrados.length === 0) {
    return (
      <div className="sin-resultados" data-testid="sin-resultados">
        No hay empleados que coincidan con los criterios de búsqueda
      </div>
    )
  }

  return (
    <table className="tabla" data-testid="tabla-empleados">
      <thead>
        <tr>
          <th>Número</th>
          <th>Nombre</th>
          <th>Correo</th>
          <th>Puesto</th>
          <th>Departamento</th>
          <th>Fecha Ingreso</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {filtrados.map(e => (
          <tr key={e.id} data-testid={`fila-empleado-${e.id}`}>
            <td data-testid={`numero-empleado-${e.id}`}>{e.numero_empleado}</td>
            <td>{e.nombre}</td>
            <td>{e.correo}</td>
            <td>{e.puesto}</td>
            <td>{e.departamento}</td>
            <td>{e.fecha_ingreso}</td>
            <td>
              <span className={`estado-${e.estado}`} data-testid={`estado-empleado-${e.id}`}>
                {e.estado === 'activo' ? 'Activo' : 'Baja'}
              </span>
            </td>
            <td>
              <div className="acciones">
                {e.estado === 'activo' && (
                  <>
                    <button
                      className="boton-pequeno"
                      onClick={() => onEditar(e)}
                      data-testid={`editar-empleado-${e.id}`}
                    >
                      Editar
                    </button>
                    <button
                      className="boton-pequeño boton-exito"
                      onClick={() => onVacaciones(e)}
                      data-testid={`vacaciones-empleado-${e.id}`}
                    >
                      Vacaciones
                    </button>
                    <button
                      className="boton-pequeno boton-peligro"
                      onClick={() => onBaja(e.id)}
                      data-testid={`baja-empleado-${e.id}`}
                    >
                      Dar de baja
                    </button>
                  </>
                )}
                {e.estado === 'baja' && (
                  <span>Empleado dado de baja</span>
                )}
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export default DirectorioEmpleados
