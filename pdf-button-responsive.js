/**
 * Script para manejar el botón de descarga PDF de forma responsive
 * Oculta el botón en dispositivos móviles y muestra un mensaje
 */

(function() {
    'use strict';

    // Función para calcular la ruta base (similar a load-menu.js)
    function getBasePath() {
        const scripts = document.getElementsByTagName('script');
        let scriptSrc = '';
        
        for (let i = 0; i < scripts.length; i++) {
            const src = scripts[i].getAttribute('src');
            if (src && src.includes('pdf-button-responsive.js')) {
                scriptSrc = src;
                break;
            }
        }
        
        if (scriptSrc) {
            const match = scriptSrc.match(/^(\.\.\/)+/);
            if (match) {
                return match[0];
            } else if (scriptSrc.startsWith('./') || scriptSrc === 'pdf-button-responsive.js') {
                return './';
            }
        }
        
        // Fallback: calcular desde URL
        const currentPath = window.location.pathname;
        const pathParts = decodeURIComponent(currentPath).split('/').filter(p => p && p !== '' && !p.endsWith('.html'));
        return pathParts.length === 0 ? './' : '../'.repeat(pathParts.length);
    }

    function initPDFButtonResponsive() {
        const pdfButton = document.getElementById('descargarPDF');
        if (!pdfButton) {
            return;
        }

        const buttonContainer = pdfButton.parentElement;
        
        // Crear mensaje para móviles
        const mobileMessage = document.createElement('div');
        mobileMessage.id = 'pdf-mobile-message';
        mobileMessage.style.cssText = `
            display: none;
            text-align: center;
            padding: 20px;
            background: #f8f9fa;
            border: 2px solid #123E92;
            border-radius: 8px;
            color: #333;
            font-size: 1em;
            line-height: 1.6;
            margin-top: 20px;
        `;
        mobileMessage.innerHTML = `
            <p style="margin: 0; color: #123E92; font-weight: 600; margin-bottom: 10px;">
                📱 Descarga no disponible en dispositivos móviles
            </p>
            <p style="margin: 0; color: #666; font-size: 0.9em;">
                Si desea descargar el contenido de esta página en un PDF, por favor visualícela desde un ordenador.
            </p>
        `;

        // Insertar el mensaje después del botón
        // Si hay un siguiente hermano, insertar antes de él, sino agregar al final
        if (pdfButton.nextSibling) {
            buttonContainer.insertBefore(mobileMessage, pdfButton.nextSibling);
        } else {
            buttonContainer.appendChild(mobileMessage);
        }

        // Función para verificar el tamaño de pantalla
        function checkScreenSize() {
            if (window.innerWidth <= 768) {
                // Móvil: ocultar botón, mostrar mensaje
                pdfButton.style.display = 'none';
                mobileMessage.style.display = 'block';
            } else {
                // Desktop: mostrar botón, ocultar mensaje
                pdfButton.style.display = 'inline-block';
                mobileMessage.style.display = 'none';
            }
        }

        // Verificar al cargar
        checkScreenSize();

        // Verificar al redimensionar
        window.addEventListener('resize', checkScreenSize);
    }

    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPDFButtonResponsive);
    } else {
        initPDFButtonResponsive();
    }
})();

