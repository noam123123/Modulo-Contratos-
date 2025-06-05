# 📋 Módulo de Contratos GPS para Costa Rica

Un módulo completo de Odoo para la gestión profesional de contratos de servicios GPS, dispositivos de rastreo y servicios SIM, diseñado específicamente para cumplir con los requisitos legales de Costa Rica.

## 🌟 Características Principales

### 📋 Gestión Completa de Contratos Personalizables
- ✅ Creación de cualquier tipo de contrato con validación legal costarricense
- 🎨 **Personalización Total**: Modifica campos, plantillas y flujos desde la interfaz
- 🔄 Estados configurables del contrato: Borrador → Enviado → Confirmado → Activo → Terminado
- 📅 Renovaciones automáticas y ciclos de facturación totalmente configurables
- 💰 Gestión flexible de precios, depósitos, descuentos y términos financieros
- 📄 Generación de PDF con plantillas 100% editables desde Odoo

### 🔗 Integración Completa con Odoo
- 👥 **CRM**: Gestión completa de oportunidades y pipeline de ventas desde leads hasta contratos firmados
- 📇 **Contactos**: Integración total con la base de datos de clientes, proveedores y contactos
- 💰 **Contabilidad**: Generación automática de facturas, asientos contables y seguimiento de pagos
- 📊 **Ventas**: Conversión automática de contratos a órdenes de venta con líneas detalladas
- 🔄 **Facturación Periódica**: Programación automática de facturación recurrente según ciclos configurados
- 💼 **Portal del Cliente**: Acceso para clientes para revisar contratos y descargar documentos

### 📊 Tipos de Contratos Incluidos
- 🟢 **Servicio GPS Básico y Premium**: Rastreo con reportes en tiempo real
- 🔵 **Venta y Alquiler de Dispositivos**: GPS trackers con garantía
- 🟡 **Servicios de Conectividad SIM**: Datos y comunicación
- 🟣 **Contratos de Mantenimiento**: Preventivo y correctivo
- 🟠 **Paquetes Completos**: Dispositivo + Servicio + SIM + Mantenimiento

### 🔗 Integración Completa con Odoo
- 🌐 Sincronización automática con CRM, Contactos y Contabilidad
- 📡 Conexión en tiempo real con módulos de Ventas
- 📱 Gestión centralizada de información de clientes
- 🔄 Actualización automática de datos financieros

### 💰 Integración Financiera Completa
- 💳 Conexión con módulos de Ventas y Contabilidad de Odoo
- 📄 Generación automática de órdenes de venta
- 🔁 Facturación periódica programada
- 💵 Gestión de depósitos y garantías

### 🇨🇷 Específico para Costa Rica
- ⚖️ Cumple con el Código de Comercio costarricense
- 🛡️ Integra Ley de Protección al Consumidor No. 7472
- 🔒 Conforme a Ley de Protección de Datos No. 8968
- 📋 Plantillas con formato legal apropiado

## 🛠️ Especificaciones Técnicas

- **Versión Odoo**: 16.0+
- **Dependencias**: `base`, `sale`, `account`, `stock`, `fleet`, `contacts`, `mail`, `portal`
- **Idioma**: Español (traducciones completas)
- **API**: Integración con plataformas externas
- **Reportes**: PDF con formato legal costarricense
- **Seguridad**: Control de acceso por roles

## 📦 Instalación

### Prerrequisitos
- Odoo 16.0 o superior instalado
- Módulos base de Odoo: Sales, Accounting, Fleet, Contacts
- Python 3.8+ con librerías: `requests`, `json`

### Pasos de Instalación

1. **Descargar el módulo**
   ```bash
   # Clonar o descargar el módulo en la carpeta addons de Odoo
   cd /path/to/odoo/addons
   # Copiar la carpeta 'contratos' aquí
   ```

2. **Activar modo desarrollador en Odoo**
   - Ir a Configuración → Activar modo desarrollador

3. **Actualizar lista de aplicaciones**
   - Ir a Aplicaciones → Actualizar lista de aplicaciones

4. **Instalar el módulo**
   - Buscar "Gestión de Contratos GPS"
   - Hacer clic en "Instalar"

5. **Configurar datos iniciales**
   - El módulo instalará automáticamente tipos de contratos predefinidos
   - Configurar la integración con plataformas externas (opcional)

## 🖥️ Instalación y Pruebas

### Opción 1: Usando Odoo.sh (Recomendado)

1. **Crear cuenta en Odoo.sh**
   - Ir a [odoo.sh](https://www.odoo.sh)
   - Crear cuenta gratuita
   - Crear un nuevo proyecto

2. **Subir el módulo**
   - Comprimir la carpeta `contratos` en un archivo ZIP
   - En Odoo.sh, ir a la sección "Aplicaciones"
   - Subir el archivo ZIP

3. **Probar funcionalidades**
   - Acceder a la instancia de Odoo
   - Instalar el módulo desde Aplicaciones
   - Navegar a "Contratos GPS" en el menú principal

### Opción 2: Instalación Local con Docker

1. **Instalar Docker Desktop**
   - Descargar desde [docker.com](https://www.docker.com/products/docker-desktop)

2. **Crear archivo docker-compose.yml**
   ```yaml
   version: '3.1'
   services:
     web:
       image: odoo:16.0
       depends_on:
         - db
       ports:
         - "8069:8069"
       volumes:
         - ./contratos:/mnt/extra-addons/contratos
         - odoo-web-data:/var/lib/odoo
       environment:
         - HOST=db
         - USER=odoo
         - PASSWORD=myodoo
     db:
       image: postgres:13
       environment:
         - POSTGRES_DB=postgres
         - POSTGRES_USER=odoo
         - POSTGRES_PASSWORD=myodoo
       volumes:
         - odoo-db-data:/var/lib/postgresql/data

   volumes:
     odoo-web-data:
     odoo-db-data:
   ```

3. **Ejecutar en terminal**
   ```bash
   docker-compose up -d
   ```

4. **Acceder a Odoo**
   - Abrir navegador en `http://localhost:8069`
   - Crear base de datos
   - Instalar el módulo "Gestión de Contratos GPS"

## 🧪 Guía de Pruebas

### Configuración Inicial

1. **Acceder al módulo**
   - En Odoo, ir al menú "Contratos"

2. **Configurar tipos de contrato**
   - Ir a "Configuración" → "Tipos de Contrato"
   - Revisar los tipos predefinidos
   - Personalizar términos y condiciones si es necesario

3. **Configurar plantillas**
   - Ir a "Configuración" → "Plantillas de Contrato"
   - Personalizar las plantillas según necesidades específicas

### Casos de Prueba

#### Caso 1: Crear Cliente y Contrato Básico
1. **Crear cliente**
   - Ir a "Contratos" → "Crear Contrato"
   - Seleccionar cliente existente o crear nuevo
   - Llenar datos: Nombre, Identificación, Teléfono, Email

2. **Configurar contrato**
   - Seleccionar tipo de contrato apropiado
   - Establecer tarifa mensual (ej: ₡25,000)
   - Configurar duración (ej: 12 meses)
   - Establecer términos financieros

3. **Agregar líneas de contrato**
   - Agregar productos o servicios específicos
   - Configurar cantidades y precios

4. **Finalizar contrato**
   - Revisar información completa
   - Crear contrato
   - Verificar que se genera correctamente

#### Caso 2: Generar PDF del Contrato
1. **Abrir contrato creado**
   - Ir a vista de formulario del contrato
   - Hacer clic en "Generar PDF"
   - Verificar formato legal para Costa Rica
   - Revisar términos y condiciones específicos

#### Caso 3: Flujo de Estados
1. **Enviar contrato**
   - En estado "Borrador", hacer clic en "Enviar Contrato"
   - Verificar cambio a estado "Enviado"

2. **Confirmar contrato**
   - Hacer clic en "Confirmar"
   - Verificar validaciones (debe tener dispositivos)

3. **Activar contrato**
   - Hacer clic en "Activar"
   - Verificar creación de orden de venta

#### Caso 4: Integración Financiera
1. **Verificar orden de venta**
   - En el contrato activo, revisar campo "Orden de Venta Relacionada"
   - Abrir orden de venta generada
   - Verificar líneas: tarifa mensual, instalación, dispositivos

2. **Generar factura**
   - Desde la orden de venta, crear factura
   - Verificar que la factura se relaciona con el contrato

### Verificaciones de Calidad

#### ✅ Funcionalidades Básicas
- [ ] Creación de contratos
- [ ] Generación de PDF con formato legal
- [ ] Cambios de estado del contrato
- [ ] Integración con ventas y facturación
- [ ] Gestión de líneas de contrato

#### ✅ Validaciones
- [ ] Campos obligatorios funcionan correctamente
- [ ] Validaciones de datos específicos
- [ ] Fechas de inicio y fin consistentes
- [ ] Validaciones financieras

#### ✅ Reportes y Documentos
- [ ] PDF incluye información completa
- [ ] Términos legales específicos para Costa Rica
- [ ] Formato profesional y legible
- [ ] Firmas y espacios apropiados

#### ✅ Integración
- [ ] Conexión con módulos de Odoo
- [ ] Sincronización de datos
- [ ] Generación de órdenes de venta
- [ ] Facturación automática

## 🔧 Configuración Avanzada

### Personalización de Contratos
- Acceda a "Configuración → Tipos de Contrato" para crear nuevos tipos
- Modifique plantillas en "Configuración → Plantillas de Contrato"
- Configure ciclos de facturación personalizados
- Defina términos y condiciones específicos para su industria