"""Estilo visual que el tema de Streamlit no cubre: fondo de las tarjetas, texto de los botones
principales y la cabecera con el arte ASCII.

El CSS solo usa las clases st-key-<clave> que Streamlit añade a los elementos con key
(comportamiento documentado), no selectores internos que puedan cambiar entre versiones.
Los colores van aquí y en .streamlit/config.toml; si cambias uno, revisa el otro.
"""

COLOR_FONDO_TARJETA = "#101916"
COLOR_BORDE_TARJETA = "#1E2C27"
COLOR_TEXTO_BOTON = "#0B1210"
# Arte ASCII: apagado por defecto y encendido alrededor del ratón
COLOR_ASCII_APAGADO = "#2E6B58"
COLOR_ASCII_MEDIO = "#5BD3A6"
COLOR_ASCII_ENCENDIDO = "#ECFDF5"
# Radio en píxeles de la zona iluminada alrededor del ratón
RADIO_LUZ = 90

# Antena de telefonía emitiendo señal, dibujada con caracteres
ARTE_ANTENA = r"""
            .  '  .  '  .  '  .  '  .
        '                             '
     .        .  '  .  '  .  '  .        .
          '                         '
               .  '  .___.  '  .
                     /   \
                     \___/
                      |||
                     /|||\
                    //|||\\
                   // ||| \\
                  //__|||__\\
                  \\  |||  //
                   \\ ||| //
                    \\|||//
                    //|||\\
                   // ||| \\
                  //__|||__\\
                 //\\ ||| //\\
                //  \\|||//  \\
               //____\|||/____\\
   ___________//______|||______\\___________
  /::::::::::::::::::::::::::::::::::::::::::\
"""


def css_global():
    """Hoja de estilo de la app. Se inserta una vez con st.html."""
    return f"""
<style>
/* Tarjetas: un fondo algo más claro que la página, como las de Retaino */
[class*="st-key-tarjeta"] {{
    background-color: {COLOR_FONDO_TARJETA};
    border-color: {COLOR_BORDE_TARJETA};
    border-radius: 0.9rem;
}}
/* Botones principales: texto oscuro sobre el acento menta para que se lea */
[class*="st-key-primario"] button p {{
    color: {COLOR_TEXTO_BOTON};
    font-weight: 600;
}}
.cabecera {{
    display: flex;
    align-items: center;
    gap: 1.5rem;
    padding: 1.5rem 0 1rem 0;
}}
/* En pantallas estrechas el texto va arriba y la antena debajo */
@media (max-width: 640px) {{
    .cabecera {{
        flex-direction: column;
        align-items: flex-start;
    }}
}}
.cabecera-texto {{
    flex: 1 1 auto;
    min-width: 0;
}}
.cabecera-texto h1 {{
    font-size: 2.2rem;
    line-height: 1.1;
    font-weight: 600;
    margin: 0.6rem 0 0.8rem 0;
    padding: 0;
}}
.cabecera-texto p {{
    opacity: 0.75;
    margin: 0;
}}
.cabecera-etiqueta {{
    display: inline-block;
    font-size: 0.8rem;
    padding: 0.2rem 0.7rem;
    border-radius: 999px;
    background-color: rgba(110, 231, 183, 0.12);
    color: #6EE7B7;
}}
.cabecera-ascii {{
    flex: 0 0 auto;
    margin: 0;
    font-family: monospace;
    font-size: 12px;
    line-height: 1.15;
    --x: -1000px;
    --y: -1000px;
    /* El texto toma el color de un degradado circular centrado en el ratón */
    background: radial-gradient(
        circle {RADIO_LUZ}px at var(--x) var(--y),
        {COLOR_ASCII_ENCENDIDO} 0%,
        {COLOR_ASCII_MEDIO} 45%,
        {COLOR_ASCII_APAGADO} 100%
    );
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    user-select: none;
}}
</style>
"""


def cabecera_html(etiqueta, titulo, subtitulo):
    """Cabecera con el texto a la izquierda y la antena a la derecha. El script mueve el
    centro del degradado a la posición del ratón; al salir, la luz se apaga."""
    return f"""
<div class="cabecera" id="cabecera-telco">
    <div class="cabecera-texto">
        <span class="cabecera-etiqueta">{etiqueta}</span>
        <h1>{titulo}</h1>
        <p>{subtitulo}</p>
    </div>
    <pre class="cabecera-ascii" id="cabecera-ascii">{ARTE_ANTENA}</pre>
</div>
<script>
{{
    // Bloque propio: Streamlit vuelve a insertar este script en cada ejecución
    const cabecera = document.getElementById("cabecera-telco");
    const arte = document.getElementById("cabecera-ascii");

    function moverLuz(evento) {{
        const caja = arte.getBoundingClientRect();
        arte.style.setProperty("--x", (evento.clientX - caja.left) + "px");
        arte.style.setProperty("--y", (evento.clientY - caja.top) + "px");
    }}

    function apagarLuz() {{
        arte.style.setProperty("--x", "-1000px");
        arte.style.setProperty("--y", "-1000px");
    }}

    cabecera.addEventListener("mousemove", moverLuz);
    cabecera.addEventListener("mouseleave", apagarLuz);
}}
</script>
"""
