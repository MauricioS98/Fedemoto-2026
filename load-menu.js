/**
 * Script para cargar el menú de navegación dinámicamente
 * Ajusta automáticamente las rutas según la ubicación del archivo HTML
 */

(function() {
    'use strict';

    // Función para calcular la ruta relativa desde el archivo actual hasta la raíz
    function getBasePath() {
        // Método principal: contar los ../ en el atributo src del script
        const scripts = document.getElementsByTagName('script');
        let scriptSrc = '';
        
        // Buscar el script load-menu.js y obtener su atributo src original
        for (let i = 0; i < scripts.length; i++) {
            const script = scripts[i];
            const src = script.getAttribute('src');
            if (src && src.includes('load-menu.js')) {
                scriptSrc = src;
                break;
            }
        }
        
        // Si encontramos el script con ruta relativa, contar los ../
        if (scriptSrc) {
            // Contar cuántos niveles sube (../)
            const match = scriptSrc.match(/^(\.\.\/)+/);
            if (match) {
                const depth = (match[0].match(/\.\.\//g) || []).length;
                const basePath = '../'.repeat(depth);
                console.log('Base path calculado desde script src:', basePath, '(depth:', depth, ', src:', scriptSrc, ')');
                return basePath;
            } else if (scriptSrc.startsWith('./') || scriptSrc === 'load-menu.js') {
                // Está en la raíz
                console.log('Script está en la raíz, usando "./"');
                return './';
            }
        }
        
        // Método alternativo: calcular desde la URL actual del documento
        try {
            const currentPath = window.location.pathname;
            // Decodificar URL encoding
            const decodedPath = decodeURIComponent(currentPath);
            // Remover el nombre del archivo HTML y cualquier query string
            const pathParts = decodedPath.split('/').filter(p => p && p !== '' && !p.endsWith('.html') && !p.includes('?'));
            
            // Si estamos en la raíz
            if (pathParts.length === 0) {
                console.log('Documento está en la raíz, usando "./"');
                return './';
            }
            
            // Contar los directorios
            const depth = pathParts.length;
            const basePath = '../'.repeat(depth);
            console.log('Base path calculado desde URL:', basePath, '(depth:', depth, ', pathParts:', pathParts, ')');
            return basePath;
        } catch (e) {
            console.warn('Error al calcular ruta desde URL:', e);
        }
        
        // Fallback: asumir que estamos en la raíz
        console.warn('No se pudo calcular la ruta, usando "./" como fallback');
        return './';
    }

    // Función para ajustar las rutas en el menú según la ubicación actual
    function adjustMenuPaths(menuElement, basePath) {
        // Ajustar la ruta del logo
        const logo = menuElement.querySelector('#menu-logo');
        if (logo) {
            // Remover cualquier ruta relativa existente y usar basePath
            logo.src = basePath + 'fedemoto-logo.png';
        }

        // Ajustar todas las rutas de los enlaces
        const links = menuElement.querySelectorAll('a[href]');
        links.forEach(link => {
            const href = link.getAttribute('href');
            
            // Solo ajustar rutas que no sean absolutas o que empiecen con #
            if (href && !href.startsWith('#') && !href.startsWith('http') && !href.startsWith('//')) {
                // Las rutas en menu.html están definidas desde la raíz del proyecto
                // Necesitamos ajustarlas según basePath
                if (href.startsWith('Informes/') || href === 'index.html') {
                    // Rutas desde la raíz: simplemente agregar basePath
                    link.setAttribute('href', basePath + href);
                } else if (href.startsWith('../')) {
                    // Si ya tiene ../, removerlos y usar basePath
                    const cleanHref = href.replace(/^\.\.\//g, '');
                    link.setAttribute('href', basePath + cleanHref);
                } else if (!href.startsWith('./')) {
                    // Cualquier otra ruta relativa (sin ../ o ./)
                    link.setAttribute('href', basePath + href);
                }
            }
        });
    }

    // Función para inicializar los dropdowns del menú
    function initMenuDropdowns() {
        // Marcar el enlace activo según la página actual
        const currentPath = window.location.pathname;
        const currentHref = window.location.href;
        const currentFile = currentPath.split('/').pop() || 'index.html';
        const currentFileName = currentFile.split('?')[0]; // Remover query strings
        
        // Buscar en todos los enlaces del menú (incluyendo dropdowns)
        const links = document.querySelectorAll('.nav-menu a[href], .dropdown-menu a[href]');
        links.forEach(link => {
            const href = link.getAttribute('href');
            if (href && href !== '#') {
                const linkFile = href.split('/').pop() || href.split('\\').pop();
                const linkFileName = linkFile ? linkFile.split('?')[0] : ''; // Remover query strings
                
                // Comparar nombres de archivo
                if (linkFileName && currentFileName && linkFileName === currentFileName) {
                    link.classList.add('active');
                    const dropdown = link.closest('.dropdown');
                    if (dropdown) {
                        dropdown.classList.add('active');
                    }
                } else if (href.includes(currentFileName) || currentPath.includes(linkFileName)) {
                    link.classList.add('active');
                    const dropdown = link.closest('.dropdown');
                    if (dropdown) {
                        dropdown.classList.add('active');
                    }
                }
            }
        });

        // Manejar clics en menús desplegables para móviles
        const dropdowns = document.querySelectorAll('.dropdown > a');
        
        dropdowns.forEach(dropdown => {
            // Remover listeners anteriores si existen
            const newDropdown = dropdown.cloneNode(true);
            dropdown.parentNode.replaceChild(newDropdown, dropdown);
            
            newDropdown.addEventListener('click', function(e) {
                if (window.innerWidth <= 768) {
                    e.preventDefault();
                    e.stopPropagation();
                    const parent = this.parentElement;
                    const isActive = parent.classList.contains('active');
                    
                    // Cerrar todos los demás dropdowns del mismo nivel
                    const siblings = Array.from(parent.parentElement.children);
                    siblings.forEach(sibling => {
                        if (sibling !== parent && sibling.classList.contains('dropdown')) {
                            sibling.classList.remove('active');
                        }
                    });
                    
                    // Toggle del dropdown actual
                    if (isActive) {
                        parent.classList.remove('active');
                    } else {
                        parent.classList.add('active');
                    }
                }
            });
        });

        // Cerrar dropdowns al hacer clic fuera
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown').forEach(d => {
                    d.classList.remove('active');
                });
            }
        });
    }

    // Función para inicializar el menú
    function initMenu() {
        const basePath = getBasePath();
        const menuContainer = document.getElementById('menu-container');
        
        if (!menuContainer) {
            console.error('No se encontró el contenedor del menú con id="menu-container"');
            return;
        }

        // Verificar si estamos en file:// (archivo local)
        const isFileProtocol = window.location.protocol === 'file:';
        
        if (isFileProtocol) {
            console.warn('Archivo abierto con file:// - Las peticiones fetch pueden estar bloqueadas por CORS');
            console.warn('Recomendación: Usar un servidor web local (Live Server, Python http.server, etc.)');
        }

        // Construir la URL del menú
        // Asegurarse de que basePath termine correctamente
        let normalizedBasePath = basePath;
        if (!normalizedBasePath.endsWith('/') && normalizedBasePath !== './') {
            normalizedBasePath += '/';
        }
        if (normalizedBasePath === './') {
            normalizedBasePath = './';
        }
        
        const menuUrl = normalizedBasePath + 'menu.html';
        console.log('=== Información de carga del menú ===');
        console.log('Base path calculado:', basePath);
        console.log('Base path normalizado:', normalizedBasePath);
        console.log('URL del menú:', menuUrl);
        console.log('URL actual del documento:', window.location.href);
        console.log('Pathname actual:', window.location.pathname);

        // Función para cargar los estilos CSS del menú
        function loadMenuStyles() {
            // Verificar si los estilos ya están cargados
            if (document.getElementById('menu-styles')) {
                return;
            }

            // Cargar estilos desde menu-styles.css
            const link = document.createElement('link');
            link.id = 'menu-styles';
            link.rel = 'stylesheet';
            link.href = normalizedBasePath + 'menu-styles.css';
            link.onerror = function() {
                console.warn('No se pudo cargar menu-styles.css, usando estilos inline');
                // Inyectar estilos inline como fallback
                injectInlineStyles();
            };
            document.head.appendChild(link);
        }

        // Función para inyectar estilos inline como fallback
        function injectInlineStyles() {
            if (document.getElementById('menu-styles-inline')) {
                return;
            }
            
            const style = document.createElement('style');
            style.id = 'menu-styles-inline';
            style.textContent = `
                @media (max-width: 768px) {
                    .menu-toggle { 
                        display: block !important; 
                        order: -1;
                        margin-right: 0 !important;
                        margin-left: 15px !important;
                        flex-shrink: 0;
                        align-self: flex-start;
                        z-index: 10002 !important;
                        position: relative !important;
                    }
                    .menu-overlay {
                        pointer-events: none;
                    }
                    .menu-overlay.active {
                        pointer-events: auto;
                    }
                    .fixed-header {
                        display: flex !important;
                        justify-content: flex-start !important;
                    }
                    .fixed-header .header-content { 
                        padding: 15px 20px !important;
                        flex-wrap: nowrap !important;
                        align-items: center !important;
                        justify-content: flex-start !important;
                        width: 100% !important;
                        max-width: 100% !important;
                        margin: 0 !important;
                    }
                    body {
                        padding-top: 120px !important;
                    }
                    body > *:not(.fixed-header):not(script):not(.menu-overlay) {
                        margin-top: 0 !important;
                    }
                    main, .content, .container, [class*="content"], [class*="container"],
                    h1:not(.logo-container h1), h2, h3, .titulo, .title {
                        margin-top: 0 !important;
                        padding-top: 0 !important;
                    }
                    body > div:first-of-type:not(.fixed-header):not(.menu-overlay),
                    body > section:first-of-type,
                    body > main:first-of-type {
                        margin-top: 0 !important;
                        padding-top: 0 !important;
                    }
                    .logo-container {
                        display: none !important;
                    }
                    .logo-container h1 {
                        display: none !important;
                    }
                    .logo-container img {
                        display: none !important;
                    }
                    .menu-overlay {
                        display: none;
                        position: fixed;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: rgba(0, 0, 0, 0.5);
                        z-index: 10000;
                        opacity: 0;
                        transition: opacity 0.3s ease;
                        pointer-events: none;
                    }
                    .menu-overlay.active {
                        display: block;
                        opacity: 1;
                        pointer-events: auto;
                    }
                    .fixed-header nav {
                        position: fixed !important;
                        top: 0 !important;
                        left: -100% !important;
                        width: 280px !important;
                        height: 100vh !important;
                        background: #123E92 !important;
                        overflow-y: auto !important;
                        transition: left 0.3s ease-out !important;
                        box-shadow: 2px 0 10px rgba(0,0,0,0.3) !important;
                        z-index: 10000 !important;
                        padding-top: 70px !important;
                        display: block !important;
                        align-items: flex-start !important;
                        justify-content: flex-start !important;
                        max-width: none !important;
                        margin: 0 !important;
                    }
                    .fixed-header nav.menu-open {
                        left: 0 !important;
                    }
                    body.menu-open {
                        overflow: hidden;
                    }
                    .nav-menu {
                        flex-direction: column;
                        width: 100%;
                        padding: 10px 0;
                    }
                    .nav-menu > li {
                        width: 100%;
                        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    }
                    .nav-menu > li > a {
                        padding: 15px 20px;
                        text-align: left;
                        font-size: 1em;
                        width: 100%;
                    }
                    .dropdown-menu {
                        position: static;
                        display: none;
                        background: rgba(0, 0, 0, 0.2);
                        width: 100%;
                        box-shadow: none;
                    }
                    .dropdown.active > .dropdown-menu {
                        display: block;
                    }
                    .dropdown-menu a {
                        padding: 12px 30px;
                        color: white;
                        text-align: left;
                    }
                    body { padding-top: 70px; }
                }
            `;
            document.head.appendChild(style);
        }

        // Función para crear el overlay oscuro
        function createMenuOverlay() {
            // Verificar si el overlay ya existe
            if (document.getElementById('menu-overlay')) {
                return document.getElementById('menu-overlay');
            }

            const overlay = document.createElement('div');
            overlay.id = 'menu-overlay';
            overlay.className = 'menu-overlay';
            document.body.appendChild(overlay);
            return overlay;
        }

        // Función para agregar el botón hamburguesa
        function addHamburgerButton(headerContent) {
            // Verificar si el botón ya existe
            if (headerContent.querySelector('.menu-toggle')) {
                return;
            }

            const menuToggle = document.createElement('button');
            menuToggle.className = 'menu-toggle';
            menuToggle.setAttribute('aria-label', 'Toggle menu');
            menuToggle.innerHTML = '☰';
            
            // Insertar al principio del header-content (antes del logo)
            const logoContainer = headerContent.querySelector('.logo-container');
            if (logoContainer) {
                headerContent.insertBefore(menuToggle, logoContainer);
            } else {
                // Si no hay logo, insertar antes del nav
                const nav = headerContent.querySelector('nav');
                if (nav) {
                    headerContent.insertBefore(menuToggle, nav);
                } else {
                    headerContent.insertBefore(menuToggle, headerContent.firstChild);
                }
            }
            
            // Crear overlay oscuro
            const overlay = createMenuOverlay();
            
            // Obtener el nav para los eventos
            const nav = headerContent.querySelector('nav');
            if (nav) {
                // Función para abrir el menú
                function openMenu() {
                    nav.classList.add('menu-open');
                    overlay.classList.add('active');
                    document.body.classList.add('menu-open');
                    menuToggle.innerHTML = '✕';
                }
                
                // Función para cerrar el menú
                function closeMenu() {
                    nav.classList.remove('menu-open');
                    overlay.classList.remove('active');
                    document.body.classList.remove('menu-open');
                    menuToggle.innerHTML = '☰';
                }
                
                // Agregar evento click al botón hamburguesa
                menuToggle.addEventListener('click', function(e) {
                    e.stopPropagation();
                    e.preventDefault();
                    // Usar setTimeout para asegurar que el evento se procese antes de cambiar el estado
                    setTimeout(function() {
                        if (nav.classList.contains('menu-open')) {
                            closeMenu();
                        } else {
                            openMenu();
                        }
                    }, 0);
                });
                
                // Cerrar menú al hacer clic en el overlay (pero no en el botón)
                overlay.addEventListener('click', function(e) {
                    // No cerrar si el clic fue en el botón hamburguesa
                    if (!menuToggle.contains(e.target) && e.target !== menuToggle) {
                        closeMenu();
                    }
                });
                
                // Cerrar menú al hacer clic en un enlace
                nav.addEventListener('click', function(e) {
                    if (window.innerWidth <= 768 && e.target.tagName === 'A' && e.target.getAttribute('href') !== '#') {
                        setTimeout(() => {
                            closeMenu();
                        }, 300);
                    }
                });
                
                // Cerrar menú con la tecla Escape
                document.addEventListener('keydown', function(e) {
                    if (e.key === 'Escape' && nav.classList.contains('menu-open')) {
                        closeMenu();
                    }
                });
                
                // Ajustar cuando se redimensiona la ventana
                window.addEventListener('resize', function() {
                    if (window.innerWidth > 768 && nav.classList.contains('menu-open')) {
                        closeMenu();
                    }
                });
            }
        }

        // Función para procesar el HTML del menú
        function processMenuHTML(html) {
            // Cargar estilos primero
            loadMenuStyles();
            
            // Crear un contenedor temporal para parsear el HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            
            // Obtener el header del menú
            const menuHeader = tempDiv.querySelector('.fixed-header');
            
            if (menuHeader) {
                // Ajustar las rutas según la ubicación actual (usar normalizedBasePath)
                adjustMenuPaths(menuHeader, normalizedBasePath);
                
                // Insertar el menú en el contenedor
                menuContainer.innerHTML = menuHeader.outerHTML;
                
                // Agregar botón hamburguesa después de insertar
                const headerContent = menuContainer.querySelector('.header-content');
                if (headerContent) {
                    addHamburgerButton(headerContent);
                }
                
                // Inicializar los dropdowns después de insertar el menú
                setTimeout(initMenuDropdowns, 100);
                console.log('✅ Menú cargado correctamente');
            } else {
                console.error('No se encontró el elemento .fixed-header en menu.html');
                menuContainer.innerHTML = '<div style="padding: 20px; background: #f0f0f0; color: #333;">Error: No se encontró el menú en menu.html</div>';
            }
        }

        // Función para mostrar error
        function showError(error) {
            console.error('Error al cargar el menú:', error);
            console.error('URL intentada:', menuUrl);
            
            let errorMessage = error.message || error;
            let solutionMessage = '';
            
            if (isFileProtocol) {
                solutionMessage = `
                    <br><strong>Solución:</strong><br>
                    <small>1. Usa Live Server en VS Code (extensión "Live Server")</small><br>
                    <small>2. O ejecuta: <code>python -m http.server 8000</code> en la carpeta del proyecto</small><br>
                    <small>3. Luego abre: <code>http://localhost:8000</code></small>
                `;
            }
            
            // Mostrar un mensaje de error más detallado
            menuContainer.innerHTML = `
                <div style="padding: 20px; background: #ffebee; color: #c62828; border: 1px solid #ef5350; border-radius: 5px; font-family: Arial, sans-serif;">
                    <strong>Error al cargar el menú de navegación</strong><br>
                    <small><strong>URL intentada:</strong> ${menuUrl}</small><br>
                    <small><strong>Error:</strong> ${errorMessage}</small><br>
                    <small><strong>Protocolo:</strong> ${window.location.protocol}</small>
                    ${solutionMessage}
                </div>
            `;
        }

        // Intentar cargar con fetch primero
        fetch(menuUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.text();
            })
            .then(html => {
                if (!html || html.trim() === '') {
                    throw new Error('El archivo menu.html está vacío');
                }
                console.log('HTML del menú recibido, procesando...');
                processMenuHTML(html);
            })
            .catch(error => {
                // Si fetch falla, intentar con XMLHttpRequest como alternativa
                console.warn('Fetch falló, intentando con XMLHttpRequest...', error);
                
                const xhr = new XMLHttpRequest();
                xhr.open('GET', menuUrl, true);
                xhr.onreadystatechange = function() {
                    if (xhr.readyState === 4) {
                        if (xhr.status === 0 || xhr.status === 200) {
                            processMenuHTML(xhr.responseText);
                        } else {
                            showError(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`));
                        }
                    }
                };
                xhr.onerror = function() {
                    showError(new Error('Error de red al cargar el menú'));
                };
                xhr.send();
            });
    }

    // Cargar el menú cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initMenu);
    } else {
        // DOM ya está listo, ejecutar inmediatamente
        initMenu();
    }
})();

