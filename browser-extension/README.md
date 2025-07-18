# Browser Extension

The extension is built using the following:

- [vite-plugin-web-extension](https://vite-plugin-web-extension.aklinker1.io/)
- [Vue](https://vuejs.org/guide/introduction.html#what-is-vue)
- [TypeScript](https://www.typescriptlang.org/)
- [Vite](https://vitejs.dev/)
- [pnpm](https://pnpm.io/).

## Main files

| File                                         | Description                                                                                                     |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| [src/manifest.json](./src/manifest.json)     | Manifest file for the browser extension                                                                         |
| [src/pages/Popup.vue](./src/pages/Popup.vue) | Main component displayed when the extension is clicked                                                          |
| [src/components](./src/components)           | Collection of Vue components that provide the main UI features                                                  |
| [src/background.ts](./src/background.ts)     | Handles the main interactions between the browser extension and the backend agents (copilot services)           |
| [src/side-panel.ts](./src/side-panel.ts)     | Creates and toggles the sidebar (including the popup component) when a message is sent by the background script |
| [src/popup.ts](./src/popup.ts)               | Initializes vue                                                                                                 |

# Cambios en browser-extension

## package.json

- Actualización menor: Se actualizó la versión del paquete `vite-plugin-web-extension` de `^3.2.0` a `^4.4.4`.

## pnpm-lock.yaml

- Gran actualización del lockfile con más de 5900 líneas modificadas.
- Actualización de múltiples dependencias como `autoprefixer`, `echarts`, `oidc-client-ts`, `postcss`, entre otras.
- Cambio de la estructura del lockfile para adaptarse a nueva versión de PNPM (de versión 6 a 9).

## src/components/CopilotChat.vue

- Cambios en la lógica y renderizado del componente principal del chat.
- Mejoras en la gestión del estado y actualización de mensajes.

## src/components/Message.vue

- Modificaciones extensas en la visualización y comportamiento de cada mensaje.
- Implementación de elementos colapsables para mostrar procesos internos (pensamiento profundo, pasos del agente).
- Mejoras en el manejo de diferentes estados de mensajes (usuario, agente, archivos adjuntos, etc.).

## src/pages/Index.vue

- Cambios menores, posiblemente ajustes en la página principal de la extensión.

## src/scripts/auth.ts

- Ajustes y mejoras en el sistema de autenticación.
- Cambios en la gestión de sesiones y almacenamiento local.

## src/scripts/flow.ts

- Modificación en la lógica de flujo de interacción del agente.
- Ajustes para mejor soporte de tipos y manejo de errores.

## src/scripts/tab-state.ts

- Mejoras en el manejo del estado de pestañas del navegador.
- Cambios en sincronización y almacenamiento de mensajes y contexto.

## Componente `Collapsible.vue`

- Componente Vue.js que muestra un bloque colapsable con título y contenido.
- Propiedades principales:
  - `title`: texto del encabezado.
  - `content`: contenido a mostrar u ocultar.
  - `open` (opcional): estado inicial abierto o cerrado.
- Controla internamente el estado de visibilidad (`visible`) y emite eventos al padre cuando cambia.
- Permite expandir o contraer contenido para mejorar la experiencia de usuario y evitar saturación visual.
- Utiliza watchers para sincronizar el estado interno con las propiedades externas.
- Ideal para organizar información en secciones dinámicas y navegables.
