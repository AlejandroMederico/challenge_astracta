![logo](./copilot-full-logo.png)

Browser Copilot is a browser extension that allows you to use existing or custom-built AI assistants to help you in everyday web application tasks.

![demo=](./demo.gif)

## Motivation

The goal is to provide a versatile UI and simple framework to implement and use an ever-increasing set of copilots (AI assistants). These copilots can help in a wide range of tasks by taking advantage of browser extension capabilities.

Here are a few examples of what these copilots can do:

- 🤖 Automatically activate copilots that are relevant to specific web applications. For instance, a Mail Copilot can activate when a Mail web app is loaded in a browser tab.
- 🔍 Extract information from the current web application. For example, the copilot could extract current mail content, from a Mail web app, and provide a summarization of the mail, or users may ask questions about the mail contents.
- ⚙️ Interact with web applications. A copilot could generate mail bodies based on user requests. It could also fill web app form fields with appropriate test data.
- 🔌 Use any service API to extract additional information or automate web app processes. For example, the copilot could retrieve valid examples from the web app backend to populate frontend forms.
- 💡 Many other ideas and capabilities can be explored by combining the browser extension with AI and LLM capabilities.

## Usage

1. Install the extension in your browser by downloading the latest version from the [releases](https://github.com/abstracta/browser-copilot/releases). To install an extension from a zip file you need to go to your browser "Manage Extension" screen, enable developer mode, and drag and drop the extension zip file.
2. Open the extension by clicking on its icon and add a new copilot by providing its base URL. The base URL should correspond to the location of `manifest.json` and `logo.png`, for example: `http://localhost:8000` if your agent is running locally.
3. Start a new chat by clicking on a configured copilot, or, if the copilot has automatic activation, just use your browser and the copilot chat will automatically appear when the copilot activates.
4. Save your preferred prompts directly from the chat. To quickly access them later, simply type '/' in the chat input.

At any point, you can close the copilot to later resume the conversation by the extension icon or right-clicking on the page and selecting `Toggle Browser Copilot`.

If you don't know any copilot URLs, this project includes a simple copilot implementation in [agent folder](./agent). You can start it by copying [agent/sample.env](./agent/sample.env) to `agent/.env`, changing the environment variables on it, and running `docker-compose up` (docker is required for this). Once started, you can configure your extension to use it by adding a copilot with the URL `http://localhost:8000`.

When you activate the copilot (click on the copilots list), it will request some credentials. Use `test` user and `test` password to login.

In the future, we plan to add a catalog of copilots contributed by the community. Therefore, **if you create new copilots, please let us know** so we can include them in the initial catalog.

## Development

### Agent Development

To develop a new agent, you can refer to the [agent-mock](./agent-mock), [agent-simple](./agent-simple) or [agent-extended](./agent-extended/) folders. The later is the most complete one with proper documentation on endpoints and `manifest.json`.

For the development environment, this project uses [devbox](https://www.jetpack.io/devbox) and [direnv](https://github.com/direnv/direnv).

To install all required dependencies (after installing devbox and direnv), run the following command:

```bash
devbox run install
```

Next, set appropriate environment variables in `agent-extended/.env`.

> To speed up development, you can comment out the Keycloak section, so you don't need to authenticate every time you want to try your copilot in the extension.
> If you don't comment out the Keycloak section, then you need to run `devbox run keycloak` to spin up Keycloak for authentication and use `test` `test` credentials for login (when requested by the browser extension).

To run the agent in dev mode, enabling automatic hot-reloading whenever any changes are detected in the agent source files, execute the following command:

```bash
devbox run agent
```

> If you want to debug the agent, you can start the agent with your preferred IDE, pointing to the relevant virtual environment created by devbox, and using IDE's debugger capabilities to run the [main script](./agent/gpt_agent/__main__.py).

For more details about the agent, please refer to [its readme](./agent/README.md).

### Browser Extension Development

If you plan to contribute changes to the browser extension, refer to the [browser-extension folder](./browser-extension).

To launch a Chrome browser with hot-reload capabilities, use the following command:

```bash
devbox run browser
```

To modify the default browser settings, consult [browser-extension/vite.config.ts](./browser-extension/vite.config.ts).

To build the final distribution of the extension, execute the following command:

```bash
devbox run build
```

## Contributing

We welcome all kinds of contributions!

- ⭐ **Give this project a star** to make it more visible to the entire community. It lets us know that you are interested in this project, motivating us to invest more effort into it.
- 📢 Spread the word about this project. If you make any publications (tweets, StackOverflow mentions, LinkedIn posts, Medium articles, etc.) about it, please let us know. We plan to add references to such publications in the future.
- 🙋 Ask questions and request improvements by creating issues or opening discussions in the repository.
- 🧑‍💻 If you enjoy coding, you can build new agents, helping us implement browser extension features or general improvements.

# Steps to Run the Project

1. In the Browser-extension/ folder, copy the file virtual_temp.js.js.map to Browser-extension/dist/.
2. The folder Browser-extension/dist/ contains the extension.
3. Depending on your browser, enable developer mode and load the extension.
4. Docker must be installed.
5. In the agent-simple/ folder, copy the file sample.env to .env and modify it with your environment variables.
6. In the agent-simple/ folder, run the following commands:

```bash
docker build -t agent-simple .
docker run -p 8000:8000 --name agent-simple agent-simple
```

7. This will start the agent on port 8000.
8. When you open the extension, add a new copilot with the URL http://localhost:8000.
9. Select the simple copilot and open the chat.
10. You can start asking anything.

# General Summary of Changes - Browser Extension and Backend Project

## Browser Extension

- **Dependencies**:

  - Important update of `vite-plugin-web-extension` and multiple libraries (e.g. `autoprefixer`, `oidc-client-ts`, `postcss`).
  - Change of version and lockfile structure of PNPM for better package management.

- **Main Components**:

  - `CopilotChat.vue`: Improvements in chat management and rendering.
  - `Message.vue`: Incorporation of collapsible elements to display internal reasoning and improved message states.
  - `Index.vue`: Minor adjustments to the main page.

- **Scripts and logic**:

  - `auth.ts`: Improvements in authentication, session management, and local storage.
  - `flow.ts`: Adjustments in interaction flow and error handling.
  - `tab-state.ts`: Improvements in synchronization and management of tab and message states.

- **New `Collapsible.vue` component**:
  - Vue component to display collapsible blocks with title and content.
  - Allows expanding/collapsing content to improve usability and prevent visual saturation.
  - Manages internal state and communicates with parent components via events.

## Backend (agent-simple y agent-mock)

- **agent-simple**:

  - Correction and improvement in the `clock()` function to return the time with Argentine timezone and bilingual docstring.
  - Modification in `process_question` to avoid literal placeholders and display the real time and step-by-step reasoning.
  - Simplification of the Dockerfile by removing unnecessary dependencies and improving the build with Poetry.
  - Update in models, main logic (`agent_logic.py`, `main.py`) and documentation.

- **agent-mock**:

  - Update to maintain consistency with agent-simple.
  - Changes in simulation logic and documentation.
  - Adjustments in dependencies to align with agent-simple.

- **agent-extended**:

  - Added the `get_keycloak_token()` function to obtain valid JWT tokens from Keycloak using grant password with user `test`.
  - Modification in `test_agent()` to incorporate authentication with token, validating session creation and sending questions to protected endpoints.
  - Improvements in test logs for greater clarity during execution.
  - Adjustment of `client_id` in the token request to match the configuration in `.env` (`browser-copilot`).
  - Update and optimization of Dockerfile to use `python:3.11-slim`, installation of system dependencies, and use of `wait-for-it.sh` script to wait for dependent services.
  - In `docker-compose.yml` the official `keycloak:latest` image was specified, variables of environment were corrected and `depends_on` was added for correct service dependency.
  - In `entrypoint.sh` the call to `wait-for-it.sh` was modified to use relative path and ensure correct waiting for Keycloak.
  - Update of dependencies in `pyproject.toml` and `.env` to include Keycloak and OpenAI configurations.

- **agent-mock**:
  - Added an agent-ext for performing authentication tests with keycloak and sending questions to protected endpoints.
  - For this, first you must run the docker-compose.yml with the following command:

```bash
docker-compose up -d
```

- In the environment variables, verify this variable: OPENID_URL=http://keycloak-1:8080/realms/browser-copilot, it is responsible for authenticating the agent-mock-ext.
- Then you must run the following command to start the agent-mock-ext:

```bash
poetry run python agent.py test
```

## Final Remarks

These changes improve the integration of the agent with authentication systems, ensure an ordered startup of services in Docker, and facilitate automatic tests with real authentication, improving stability and maintainability of the project.

## ESPAÑOL

![logo](./copilot-full-logo.png)

Browser Copilot es una extensión de navegador que te permite usar asistentes IA existentes o personalizados para ayudarte en tareas cotidianas dentro de aplicaciones web.

![demo=](./demo.gif)

## Motivación

El objetivo es proveer una interfaz versátil y un marco sencillo para implementar y usar un conjunto creciente de copilotos (asistentes IA). Estos copilotos pueden ayudar en una amplia variedad de tareas aprovechando las capacidades de las extensiones de navegador.

Algunos ejemplos de lo que pueden hacer estos copilotos:

- 🤖 Activar automáticamente copilotos relevantes para aplicaciones web específicas. Por ejemplo, un Copiloto de Mail que se activa cuando se carga una app de correo en una pestaña del navegador.
- 🔍 Extraer información de la aplicación web actual. Por ejemplo, el copiloto puede extraer el contenido de un mail desde una app de correo y ofrecer un resumen, o responder preguntas sobre dicho contenido.
- ⚙️ Interactuar con aplicaciones web. Puede generar cuerpos de mails según peticiones del usuario, o completar formularios de la app con datos de prueba.
- 🔌 Usar cualquier API de servicio para extraer información adicional o automatizar procesos web. Por ejemplo, obtener ejemplos válidos del backend para llenar formularios del frontend.
- 💡 Muchas otras ideas y funcionalidades pueden explorarse combinando la extensión con IA y modelos LLM.

## Uso

1. Instala la extensión en tu navegador descargando la última versión desde los [releases](https://github.com/abstracta/browser-copilot/releases). Para instalar desde un zip, ve a la pantalla "Gestionar extensiones" de tu navegador, activa el modo desarrollador y arrastra el archivo zip.
2. Abre la extensión haciendo clic en su ícono y agrega un nuevo copiloto indicando su URL base. La URL base debe corresponder a donde se encuentran `manifest.json` y `logo.png`, por ejemplo: `http://localhost:8000` si tu agente corre localmente.
3. Inicia un nuevo chat haciendo clic en un copiloto configurado, o si el copiloto se activa automáticamente, simplemente navega y el chat aparecerá.
4. Guarda tus prompts preferidos directamente desde el chat. Para acceder rápidamente a ellos, escribe '/' en la entrada del chat.

Puedes cerrar el copiloto en cualquier momento y retomar la conversación luego desde el ícono de la extensión o con clic derecho seleccionando `Toggle Browser Copilot`.

Si no tienes URLs de copilotos, el proyecto incluye una implementación simple en la carpeta [agent](./agent). Puedes iniciarlo copiando [agent/sample.env](./agent/sample.env) a `agent/.env`, modificar variables de entorno y ejecutar `docker-compose up` (requiere Docker). Luego configuras la extensión con la URL `http://localhost:8000`.

Al activar el copiloto (clic en la lista de copilotos) pedirá credenciales: usa usuario `test` y contraseña `test`.

En el futuro planeamos un catálogo comunitario de copilotos, así que **si creas nuevos copilotos, avísanos** para incluirlos.

## Desarrollo

### Desarrollo del Agente

Para crear un nuevo agente puedes usar las carpetas [agent-mock](./agent-mock), [agent-simple](./agent-simple) o [agent-extended](./agent-extended/). La última es la más completa con documentación de endpoints y `manifest.json`.

Este proyecto usa [devbox](https://www.jetpack.io/devbox) y [direnv](https://github.com/direnv/direnv) para el entorno de desarrollo.

Para instalar dependencias (tras instalar devbox y direnv), ejecuta:

```bash
devbox run install
```

Luego configura las variables de entorno adecuadas en agent-extended/.env.

Para acelerar desarrollo puedes comentar la sección de Keycloak para evitar autenticar siempre que pruebes el copiloto.
Si no la comentas, debes ejecutar devbox run keycloak para levantar Keycloak y usar usuario test y contraseña test para login (cuando la extensión lo pida).

Para correr el agente en modo desarrollo con recarga automática:

```bash
devbox run agent
```

Para debuguear, abre el agente con tu IDE apuntando al entorno virtual creado por devbox y usa su debugger en el script principal.

Más detalles en el readme del agente.

Desarrollo de la Extensión
Para contribuir a la extensión, ve a la carpeta browser-extension.

Para lanzar Chrome con recarga en caliente:

```bash
devbox run browser
```

Desarrollo de la Extensión
Para contribuir a la extensión, ve a la carpeta browser-extension.

Para lanzar Chrome con recarga en caliente:

```bash
devbox run browser
```

Más detalles en el readme de la extensión.

## Contribuyendo

¡Toda contribución es bienvenida!

⭐ Dale una estrella al proyecto para hacerlo más visible y motivarnos a seguir.

📢 Difunde el proyecto. Si publicas sobre él (tweets, StackOverflow, LinkedIn, Medium, etc.) avísanos para incluir referencias.

🙋 Pregunta o solicita mejoras creando issues o debates.

🧑‍💻 Si te gusta programar, crea agentes nuevos o ayuda con mejoras.

## Pasos para ejecutar el proyecto

1. En la carpeta Browser-extension/ copia el archivo virtual_temp.js.js.map a Browser-extension/dist/.

2. La carpeta Browser-extension/dist/ contiene la extensión.

3. Según tu navegador, activa modo desarrollo y carga la extensión.

4. Debes tener Docker instalado.

5. En agent-simple/ copia sample.env a .env y modifica con tus variables.

6. En agent-simple/ ejecuta:

```bash
docdocker build -t agent-simple .
docker run -p 8000:8000 --name agent-simple agent-simple

```

7. Esto iniciará el agente en el puerto 8000.

8. Abre la extensión, agrega un copiloto con URL http://localhost:8000.

9. Selecciona el copiloto simple y abre el chat.

10. Comienza a hacer preguntas.

## Resumen General de Cambios - Extensión y Backend

## Extensión

- Dependencias:

  - Actualización importante de vite-plugin-web-extension y varias librerías (autoprefixer, oidc-client-ts, postcss).

  - Cambio de versión y estructura del lockfile PNPM para mejor gestión de paquetes.

- Componentes principales:

  - CopilotChat.vue: Mejoras en gestión y renderizado del chat.

  - Message.vue: Añadidos elementos colapsables para mostrar razonamientos y mejor estado de mensajes.

  - Index.vue: Ajustes menores en la página principal.

- Scripts y lógica:

  - auth.ts: Mejoras en autenticación, gestión de sesión y almacenamiento local.

  - flow.ts: Ajustes en flujo de interacción y manejo de errores.

  - tab-state.ts: Mejoras en sincronización y manejo del estado de pestañas y mensajes.

  - Nuevo componente Collapsible.vue:

    - Componente Vue para mostrar bloques colapsables con título y contenido.

    - Permite expandir/contraer contenido para mejor usabilidad y evitar saturación visual.

    - Maneja estado interno y comunicación con componentes padres vía eventos.

## Backend (agent-simple y agent-mock)

### agent-simple:

- Corrección y mejora en función clock() para devolver hora en zona horaria Argentina con docstring bilingüe.

- Modificación en process_question para evitar placeholders literales y mostrar hora real y razonamiento paso a paso.

- Simplificación de Dockerfile eliminando dependencias innecesarias y mejorando build con Poetry.

- Actualización en modelos, lógica principal (agent_logic.py, main.py) y documentación.

### agent-mock:

- Actualización para mantener coherencia con agent-simple.

- Cambios en lógica de simulación y documentación.

- Ajustes en dependencias para alinear con agent-simple.

### agent-extended:

- Se agregó función get_keycloak_token() para obtener tokens JWT válidos desde Keycloak usando grant password con usuario test.

- Modificación en test_agent() para incorporar autenticación con token, validando creación de sesión y envío de preguntas a endpoints protegidos.

- Mejoras en logs de pruebas para mayor claridad.

- Ajuste de client_id en solicitud de token para coincidir con configuración en .env (browser-copilot).

- Actualización y optimización de Dockerfile para usar python:3.11-slim, instalar dependencias del sistema y usar script wait-for-it.sh para esperar servicios dependientes.

- En docker-compose.yml se especificó imagen oficial keycloak:latest, se corrigieron variables de entorno y se agregó depends_on para dependencia correcta de servicios.

- En entrypoint.sh se modificó llamada a wait-for-it.sh para usar ruta relativa y asegurar espera correcta de Keycloak.

- Actualización de dependencias en pyproject.toml y .env para incluir configuraciones de Keycloak y OpenAI.

### agent-extended:

- Se agregó un agent-ext para pruebas de autenticación con Keycloak y envío de preguntas a endpoints protegidos.

- Para ello primero se debe correr el docker-compose.yml con:

```bash
docker-compose up -d
```

- En variables de entorno verificar OPENID_URL=http://keycloak-1:8080/realms/browser-copilot, encargada de autenticar agent-mock-ext.

- Luego ejecutar:

```bash
poetry run python agent.py test
```
