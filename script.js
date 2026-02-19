// --- CONFIGURACIÓN DE VARIABLES ---
const galeria = document.getElementById("galeria");
const tituloElemento = document.getElementById("titulo-escrito");
const frase = "Cuidamos tu salud visual con la mejor tecnología";
let index = 0;
let borrando = false;
let datosInventario = [];

// 1. CARGA DE DATOS (Con truco Anti-Cache)
async function cargarDatos() {
  try {
    const respuesta = await fetch("inventario.json?v=" + Date.now());
    datosInventario = await respuesta.json();
    cargarObras("todos");
  } catch (error) {
    console.error("Error en el motor de datos:", error);
  }
}

// 2. FILTRADO DE CATEGORÍAS
function filtrar(categoria, btn) {
  // Actualizar botones
  document
    .querySelectorAll(".filter-btn")
    .forEach((b) => b.classList.remove("active"));
  btn.classList.add("active");
  // Filtrar galería
  cargarObras(categoria);
}

// 3. RENDERIZADO DE CARTAS (Galería Viva y Multivista)
function cargarObras(filtro = "todos") {
  if (!galeria) return;
  galeria.innerHTML = "";

  const items =
    filtro.toLowerCase() === "todos"
      ? datosInventario
      : datosInventario.filter(
          (i) => i.cat.toLowerCase() === filtro.toLowerCase(),
        );

  items.forEach((item) => {
    const card = document.createElement("div");
    card.className = "card animar-subida";

    // --- LÓGICA MULTIVISTA ---
    // Si es una lista, la primera es el frente, la segunda el lado.
    const esMulti = Array.isArray(item.nombre);
    const imgFrente = esMulti ? item.nombre[0] : item.nombre;
    const imgLado = esMulti && item.nombre[1] ? item.nombre[1] : null;

    const textoParaGrid =
      item.desc && item.desc.trim() !== "" ? item.desc : "Opticentro A&E";

    // Construimos el HTML de la imagen
    // Si tiene segunda imagen, añadimos la clase 'has-hover'
    card.innerHTML = `
      <div class="img-container ${imgLado ? "has-hover" : ""}">
        <img src="img/${imgFrente}.jpeg" class="img-main" alt="${imgFrente}">
        ${imgLado ? `<img src="img/${imgLado}.jpeg" class="img-hover" alt="${imgLado}">` : ""}
      </div>
      <span class="descripcion-viva">${textoParaGrid}</span>
    `;

    card.onclick = () => {
      const modal = document.getElementById("modal-visor");
      const imgFull = document.getElementById("img-full");
      const descTxt = document.getElementById("desc-texto");

      // En el modal siempre mostramos la de frente primero
      imgFull.src = `img/${imgFrente}.jpeg`;

      const texto = item.desc || "Calidad y estilo para tu visión.";
      descTxt.textContent = texto;
      descTxt.style.display = "block";

      modal.style.display = "flex";
      document.body.style.overflow = "hidden";
    };
    galeria.appendChild(card);
  });
}

// 4. EFECTO ESCRITURA (Título Principal)
function loopEscritura() {
  if (!tituloElemento) return;
  tituloElemento.textContent = frase.substring(0, index);
  let vel = borrando ? 50 : 120;

  if (!borrando && index === frase.length) {
    vel = 3000;
    borrando = true;
  } else if (borrando && index === 0) {
    borrando = false;
    vel = 1000;
  }

  index += borrando ? -1 : 1;
  setTimeout(loopEscritura, vel);
}

// 5. DARK MODE TOGGLE
const themeBtn = document.getElementById("theme-toggle");
if (themeBtn) {
  themeBtn.onclick = () => {
    const body = document.documentElement;
    const isDark = body.getAttribute("data-theme") === "dark";
    const newTheme = isDark ? "light" : "dark";
    body.setAttribute("data-theme", newTheme);
    themeBtn.innerHTML = isDark
      ? '<i class="fas fa-sun"></i>'
      : '<i class="fas fa-moon"></i>';
  };
}

// 6. INICIALIZACIÓN Y PRELOADER
window.addEventListener("load", () => {
  cargarDatos();
  loopEscritura();
  setTimeout(() => {
    const preloader = document.getElementById("preloader-art");
    if (preloader) {
      preloader.style.opacity = "0";
      setTimeout(() => (preloader.style.display = "none"), 800);
    }
  }, 2000);
});

// Cerrar Modal
document.querySelector(".cerrar-modal").onclick = () => {
  document.getElementById("modal-visor").style.display = "none";
  document.body.style.overflow = "auto";
};
