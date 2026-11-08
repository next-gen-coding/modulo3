import { useState, useEffect } from 'react'
import Empleados from './components/Empleados'

function App() {
  const [cargar, setCargar] = useState(0)

  useEffect(() => {
    fetch('/api/salud')
      .catch(err => console.error('Error conectando con el backend:', err))
  }, [])

  return (
    <div className="contenedor">
      <h1 className="titulo-principal">Gestión de Empleados</h1>
      <Empleados key={cargar} onCambio={() => setCargar(c => c + 1)} />
    </div>
  )
}

export default App
