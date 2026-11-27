/* ============================================================
   BORRADOR REUTILIZABLE
   Guarda lo que el usuario va capturando en ESTE navegador,
   para que no se pierda si recarga la página o cierra un modal.
   No guarda nada en el servidor: es solo un borrador.

   Uso:
       Borrador.guardar("borrador_entrada", listaDeProductos);
       const datos = Borrador.leer("borrador_entrada");   // o null
       Borrador.borrar("borrador_entrada");
   ============================================================ */

const Borrador = (function () {
  function guardar(clave, datos) {
    try {
      localStorage.setItem(clave, JSON.stringify(datos));
    } catch (e) {
      // Si el navegador no permite guardar, seguimos sin borrador
    }
  }

  function leer(clave) {
    try {
      const datos = JSON.parse(localStorage.getItem(clave));
      return datos ?? null;
    } catch (e) {
      return null;
    }
  }

  function borrar(clave) {
    try {
      localStorage.removeItem(clave);
    } catch (e) {}
  }

  return { guardar, leer, borrar };
})();