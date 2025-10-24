# Plan: VEC Tools Dashboard - Fix Modo Oscuro + Sistema de Usuarios y Permisos

## Fase 1: Arreglar Modo Oscuro ✅
- [x] Configurar rxconfig.py con desactivación de SitemapPlugin
- [x] Crear estructura de carpetas (app/pages/, assets/)
- [x] Implementar auth.py con login basado en variables de entorno
- [x] Crear página de login con UI inspirada en VEC Fleet
- [x] Implementar sistema de sesión con cookies firmadas
- [x] Crear state.py con AppState base (user, theme_dark, tools, groups)
- [x] **FIX: Implementar correctamente el tema oscuro con rx.theme y appearance binding**
- [x] **FIX: Persistir preferencia de tema en cookie**
- [x] **FIX: Aplicar estilos dark mode a todos los componentes (topbar, sidebar, cards, modal)**

---

## Fase 2: Base de Datos y Modelos de Usuario ✅
- [x] Instalar SQLAlchemy y bcrypt
- [x] Crear models.py con tablas User, Permission, UserPermission
- [x] Crear database.py con configuración de conexión (SQLite por defecto)
- [x] Definir modelo User (id, username, password_hash, email, is_admin, created_at)
- [x] Definir modelo Permission (id, script_relpath, description)
- [x] Definir modelo UserPermission (user_id, permission_id, granted_at)
- [x] Crear funciones helper para hash de contraseñas (bcrypt)
- [x] Implementar funciones CRUD básicas para usuarios
- [x] **FIX: Corregir sistema de sesión en AppState (usar persistencia automática de Reflex)**
- [x] **FIX: Actualizar login/logout para usar BD en lugar de env vars**
- [x] **FIX: Remover hydrate_user y usar persistencia automática**
- [x] **FIX: Usar rx.color_mode en lugar de theme_dark custom**

---

## Fase 3: UI de Administración de Usuarios ✅
- [x] Crear página /admin con tabla de usuarios (nombre, email, rol, acciones)
- [x] Implementar formulario de creación de usuario (username, email, password, is_admin)
- [x] Implementar formulario de edición de usuario
- [x] Agregar función de eliminación de usuario con confirmación
- [x] Agregar navegación a /admin en sidebar (solo visible para admin)
- [x] Proteger ruta /admin con rx.cond verificando AppState.user_is_admin

---

## Fase 4: Sistema de Permisos y Filtrado de Scripts ✅
- [x] Crear página /admin/permissions para gestionar permisos por usuario
- [x] Implementar modal/formulario para asignar scripts a usuarios
- [x] Modificar AppState.on_load para sincronizar permisos automáticamente
- [x] Filtrar tools según permisos del usuario (admin ve todos)
- [x] Modificar run_tool para validar permisos antes de ejecutar
- [x] Agregar indicador visual en cards (badge o lock icon) si no tiene permiso
- [x] **FIX: Importar Permission en database.py para sync_permissions**

---

## Fase 5: Mejoras de Seguridad y UX
- [ ] Implementar cambio de contraseña para usuarios
- [ ] Agregar logging de ejecuciones (quién ejecutó qué script y cuándo)
- [ ] Crear página /logs con historial de ejecuciones (solo admin)
- [ ] Implementar sesiones con expiración automática
- [ ] Agregar confirmación antes de ejecutar scripts críticos
- [ ] Mejorar mensajes de error en modal con formato mejorado

---

## Notas Técnicas
- Base de datos: SQLite por defecto (DB_PATH en .env, default: ./vec_tools.db)
- Hash de contraseñas: bcrypt con salt rounds=12
- Usuario admin inicial: se crea automáticamente en primer arranque si DB vacía
- Permisos por defecto: admin tiene acceso a todo, nuevos usuarios ninguno
- UI admin: tabla con ag-grid o tabla nativa de Reflex con paginación
- **Sesión en Reflex**: El estado se persiste automáticamente por session_id
- **Modo oscuro**: Usar rx.color_mode y rx.toggle_color_mode (no variable custom)
- **Sistema de permisos**: Sincronización automática de scripts descubiertos con tabla Permission
- **Filtrado**: Usuarios regulares solo ven scripts con permiso asignado, admins ven todo
