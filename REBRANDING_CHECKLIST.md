# FEDEMOTO Rebranding Checklist

## Estado general

- Sistema visual centralizado en `fedemoto-theme.css`.
- Navegacion unificada en `menu.html` + `menu-styles.css` + `load-menu.js`.
- Paginas de informes/resultados/inscritos enlazadas al tema global.
- Workflow de deploy estatico en `.github/workflows/deploy-pages.yml`.
- Compatibilidad GitHub Pages con `.nojekyll`.

## Validaciones visuales pendientes (manual)

- Verificar desktop (>= 1280px): espaciados, tablas y modales.
- Verificar tablet (768px - 1024px): menu, cards y ancho de tablas.
- Verificar mobile (< 768px): menu lateral, buscadores y botones de modal.
- Verificar contraste en encabezados de tabla y estados hover.
- Verificar impresion PDF en paginas de resultados_validas.

## Criterios de cierre

- Sin estilos inline nuevos para layout principal.
- Tipografia consistente (Montserrat/Source Sans 3/Barlow Condensed).
- Navbar sticky y responsive estable en todas las paginas.
- Tablas con enfoque institucional (legibilidad + jerarquia de podio).
