# Manual de Marca — MINERVA SMS / FEDEMOTO

Este documento contiene las especificaciones del manual de marca que deben seguirse al diseñar informes, páginas web y cualquier elemento visual del proyecto FEDEMOTO.

## Paleta de Colores

### Colores principales (FCM):
- **Azul FCM**: `#123E92` — Color principal (botones primarios, títulos, enlaces)
- **Rojo FCM**: `#E31825` — Acciones de peligro, alertas, errores
- **Amarillo FCM**: `#F7C31D` — Acentos, destacados
- **Negro FCM**: `#000000` — Texto principal
- **Plata FCM**: `#C0C0C0` — Elementos secundarios

### Colores de fondo:
- **Fondo claro**: `#f5f5f5`
- **Fondo oscuro**: `#1f2937` (dark mode)

### Variaciones para hover:
- **Azul oscuro (hover)**: `#0f3377`
- **Rojo claro (hover)**: `#c41420`

## Tipografía

### Fuentes:

#### Bebas Neue — Títulos
- **Uso**: títulos principales (h1, h2, h3, h4, h5, h6), números grandes, encabezados
- **Características**: letter-spacing: 1-2px para títulos grandes

#### Roboto Condensed — Subtítulos y elementos destacados
- **Pesos**: 300, 400, 700
- **Uso**: subtítulos, botones, elementos de navegación, badges, labels
- **Peso 400**: Navegación normal
- **Peso 700**: Botones activos, elementos destacados

#### Inter — Texto base y UI
- **Pesos**: 300, 400, 500, 600, 700
- **Uso**: body, párrafos, inputs, mensajes, contenido general
- **Peso 400**: Texto normal
- **Peso 500-600**: Texto semibold cuando se necesita énfasis

### Importación de fuentes:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto+Condensed:wght@300;400;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

## Estilos de Componentes

### Botones

#### Botón Primario:
```css
background: #123E92;
color: white;
border-radius: 8px;
padding: 10px 24px;
transition: all 0.2s ease;
font-family: 'Roboto Condensed', sans-serif;
font-weight: 700;
```

**Hover**: `background: #0f3377`

#### Botón Peligro:
```css
background: #E31825;
color: white;
border-radius: 8px;
padding: 10px 24px;
transition: all 0.2s ease;
font-family: 'Roboto Condensed', sans-serif;
font-weight: 700;
```

**Hover**: `background: #c41420`

#### Botón Secundario/Cancelar:
```css
background: #e5e7eb;
color: #374151;
border-radius: 8px;
padding: 10px 24px;
transition: all 0.2s ease;
font-family: 'Roboto Condensed', sans-serif;
font-weight: 400;
```

**Hover**: `background: #d1d5db`

### Inputs

```css
border: 2px solid #d1d5db;
border-radius: 8px;
padding: 15px;
font-family: 'Inter', sans-serif;
font-weight: 400;
transition: border-color 0.2s ease, box-shadow 0.2s ease;
```

**Focus**:
```css
border-color: #123E92;
box-shadow: 0 0 0 3px rgba(18, 62, 146, 0.2);
outline: none;
```

### Títulos

#### H1, H2, H3 (Principales):
```css
font-family: 'Bebas Neue', sans-serif;
color: #123E92;
letter-spacing: 1-2px;
```

#### H4, H5, H6 (Subtítulos):
```css
font-family: 'Bebas Neue', sans-serif;
color: #123E92;
letter-spacing: 1px;
```

### Cards

```css
background: white;
border-radius: 8px;
padding: 25px;
box-shadow: 0 5px 15px rgba(0,0,0,0.1);
transition: transform 0.2s ease, box-shadow 0.2s ease;
```

**Hover**:
```css
transform: translateY(-5px);
box-shadow: 0 10px 25px rgba(0,0,0,0.2);
```

### Dropdowns/Menús

```css
background: white;
border: 1px solid #d1d5db;
border-radius: 8px;
box-shadow: 0 8px 16px rgba(0,0,0,0.2);
```

**Enlaces en dropdown**:
```css
font-family: 'Inter', sans-serif;
color: #000000;
font-weight: 400;
transition: all 0.2s ease;
```

**Hover**:
```css
background: #f8f9fa;
color: #123E92;
```

**Active**:
```css
background: #F7C31D;
color: #123E92;
font-weight: 600;
```

#### ⚠️ IMPORTANTE: Puente invisible entre menú y dropdown

**CRÍTICO**: Siempre debe implementarse un puente invisible entre el elemento del menú principal y su dropdown para evitar que el menú se cierre cuando el cursor se mueve hacia el desplegable.

**Puente para dropdowns principales**:
```css
/* Puente invisible para mantener el hover activo */
.dropdown::before {
    content: '';
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    height: 5px;
    background: transparent;
    z-index: 1001;
}
```

**Puente para submenús anidados** (cuando hay sub-dropdowns dentro de dropdowns):
```css
/* Puente invisible para submenús anidados - cubre el espacio entre el item y el sub-submenú */
.dropdown-menu .dropdown::before {
    content: '';
    position: absolute;
    top: 0;
    left: 100%;
    width: 10px;
    height: 100%;
    background: transparent;
    z-index: 10004;
}
```

**Nota**: El puente debe tener un z-index mayor que el dropdown pero menor que el dropdown-menu para funcionar correctamente. La altura del puente principal (5px) debe coincidir con el espacio entre el menú y el dropdown (`margin-top` del dropdown-menu).

## Configuración General

### Border Radius
- **Botones**: `8px`
- **Cards**: `8px`
- **Inputs**: `8px`
- **Dropdowns**: `8px`
- **Modales/Popups**: `12px`

### Transiciones
- **Duración**: `0.2s`
- **Easing**: `ease`
- **Ejemplo**: `transition: all 0.2s ease;`

### Colores de Texto
- **Texto principal**: `#000000` (Negro FCM)
- **Texto secundario**: `#C0C0C0` (Plata FCM)
- **Enlaces**: `#123E92` (Azul FCM)
- **Enlaces hover**: `#0f3377` (Azul oscuro)

### Fondos
- **Body**: `#f5f5f5`
- **Cards/Containers**: `white`
- **Secciones secundarias**: `#f8f9fa`
- **Bordes**: `#C0C0C0` o `#d1d5db`

## Patrones de Uso Comunes

### Títulos de Sección
```css
font-family: 'Bebas Neue', sans-serif;
font-size: 2em;
color: #123E92;
margin-bottom: 25px;
padding-bottom: 15px;
border-bottom: 3px solid #F7C31D;
letter-spacing: 1px;
```

### Números Grandes (Estadísticas)
```css
font-family: 'Bebas Neue', sans-serif;
font-size: 3em;
font-weight: bold;
color: #123E92;
letter-spacing: 2px;
```

### Texto de Navegación
```css
font-family: 'Roboto Condensed', sans-serif;
font-weight: 400;
font-size: 1.1em;
color: white;
```

### Texto de Contenido
```css
font-family: 'Inter', sans-serif;
font-weight: 400;
font-size: 1em;
color: #000000;
line-height: 1.6;
```

## Ejemplos de Aplicación

### Header/Navegación
- Fondo: `#123E92`
- Texto: `white`
- Fuente navegación: `Roboto Condensed`
- Fuente logo: `Bebas Neue`
- Border-radius botones: `8px`

### Hero Section
- Fondo: `linear-gradient(135deg, #123E92 0%, #0f3377 100%)`
- Título: `Bebas Neue`, `white`, `letter-spacing: 2px`
- Subtítulo: `Roboto Condensed`, `white`

### Cards de Información
- Fondo: `white`
- Border-radius: `8px`
- Borde izquierdo destacado: `5px solid #F7C31D`
- Título card: `Bebas Neue`, `#123E92`
- Texto card: `Inter`, `#000000`

### Footer
- Fondo: `#f8f9fa`
- Borde superior: `1px solid #C0C0C0`
- Texto: `Inter`, `#000000`
- Texto desarrollador: `Roboto Condensed`, `#123E92`, `font-weight: 700`

## Notas Importantes

1. **Consistencia**: Siempre usar las fuentes especificadas según el tipo de elemento
2. **Colores**: No usar gradientes excepto en hero sections, usar colores sólidos de la paleta
3. **Espaciado**: Mantener letter-spacing en títulos con Bebas Neue (1-2px)
4. **Transiciones**: Todas las transiciones deben ser `0.2s ease`
5. **Border-radius**: Usar `8px` para la mayoría de elementos, `12px` solo para modales grandes
6. **⚠️ Puente invisible en menús**: **CRÍTICO** - Siempre implementar el puente invisible (`::before`) entre elementos del menú y sus dropdowns para evitar que se cierren al mover el cursor. Ver sección "Dropdowns/Menús" para el código completo.

## Resumen Rápido

- **Color principal**: `#123E92`
- **Color peligro**: `#E31825`
- **Color acento**: `#F7C31D`
- **Fuente títulos**: `Bebas Neue`
- **Fuente subtítulos**: `Roboto Condensed`
- **Fuente texto**: `Inter`
- **Border radius**: `8px` (botones, cards, inputs), `12px` (modales)
- **Transiciones**: `0.2s ease`

---

**Última actualización**: Enero 2026
**Aplicado a**: index.html, informe_2025_fedemoto.html, menu.html
