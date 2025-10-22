# Plan: VEC Tools Dashboard - Sistema de Gestión y Ejecución de Scripts

## Fase 1: Estructura Base y Autenticación ✅
- [x] Configurar rxconfig.py con desactivación de SitemapPlugin
- [x] Crear estructura de carpetas (app/pages/, assets/)
- [x] Implementar auth.py con login basado en variables de entorno
- [x] Crear página de login con UI inspirada en VEC Fleet
- [x] Implementar sistema de sesión con cookies firmadas
- [x] Crear state.py con AppState base (user, theme_dark, tools, groups)

---

## Fase 2: Descubrimiento y Gestión de Scripts ✅
- [x] Implementar utils.py con discover_tools() para escanear directorio
- [x] Crear load_tools_catalog() para enriquecer desde tools.json opcional
- [x] Implementar agrupación de scripts por carpeta
- [x] Normalizar estructura de items con defaults para title/desc/icon
- [x] Integrar descubrimiento en AppState.on_load

---

## Fase 3: Dashboard UI y Ejecución de Scripts ✅
- [x] Crear topbar con logo, título "VEC Tools", toggle tema, botón LOGOUT
- [x] Implementar sidebar (260px) con lista de grupos y hover effects
- [x] Crear grid responsive de cards con bordes, sombras y hover effects
- [x] Implementar run_script() en utils.py con asyncio subprocess
- [x] Crear modal de resultados con STDOUT/STDERR en code_blocks
- [x] Añadir botones "Copiar" para STDOUT/STDERR
- [x] Aplicar tema claro/oscuro con rx.theme y rx.cond
- [x] Proteger dashboard con rx.effect para redirigir no autenticados

---

## Notas Técnicas
- Compatible con Windows + Python 3.14 + Node 18+ + Pydantic v2
- Sin Docker, sin expresiones Python `if/or` sobre Vars
- Usar rx.cond para condicionales en UI
- Props literales correctas (justify="between", no "space-between")
- Logo remoto: https://backoffice.staging.vecfleet.io/static/media/logo-login-app.3ef99420e5a1cc400d8f.png
- Timeout de ejecución: 60s
- Truncamiento STDOUT/STDERR: 4000 chars c/u
