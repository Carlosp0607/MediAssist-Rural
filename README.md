# MediAssist Rural

Enfoque: integración de IA por API y backend serverless seguro.

Asistente de orientación en salud con IA, pensado para zonas de Colombia con acceso médico limitado.

**Demo:** [mediassist-rural.vercel.app](https://mediassist-rural.vercel.app)

---

## El problema

En Colombia más de 11 millones de personas viven en zonas rurales donde el acceso a un médico es limitado o inexistente. Cuando alguien se enferma en el Chocó, La Guajira o el Amazonas, la primera pregunta no es qué tratamiento seguir, sino si esto amerita salir a buscar atención.

MediAssist Rural no reemplaza a un médico. Responde esa primera pregunta.

---

## Qué hace

- **Orienta sobre síntomas** en lenguaje simple, sin terminología clínica.
- **Personaliza la respuesta** con los datos que entrega el paciente: nombre, edad y condiciones previas.
- **Detecta señales de urgencia** en cada respuesta y muestra una alerta con la línea de emergencias 123.
- **Guarda el historial** de consultas en el navegador.
- **Funciona en cualquier dispositivo** con conexión básica a internet.

---

## Arquitectura

```
Navegador (React 19 + Vite)
        │
        │  POST /api/chat
        ▼
Función serverless en Vercel  (api/chat.js)
        │
        │  Guarda la clave de API en el servidor,
        │  nunca se expone al cliente
        ▼
OpenRouter  →  meta-llama/llama-3.1-8b-instruct
```

La llamada al modelo no se hace desde el navegador. Pasa por una función serverless en Vercel que actúa como intermediario, para que la clave de API viva en variables de entorno del servidor y no en el bundle de JavaScript que descarga el usuario. La función fija el modelo, valida el formato de cada mensaje y limita el tamaño de la conversación, para que nadie pueda usarla como acceso libre a la API.

---

## Detección de urgencias

Es la parte del sistema que más cuidado exige: un asistente de salud que no distingue entre una molestia leve y una emergencia real puede hacer daño.

Cada respuesta del asistente se revisa contra un conjunto de señales de urgencia. Cuando encuentra una, la interfaz renderiza una alerta visible con la línea de emergencias 123 junto a esa respuesta. La orientación general queda en segundo plano; lo primero que ve el usuario es la indicación de buscar atención inmediata.

---

## Stack

| Componente | Tecnología |
|---|---|
| Interfaz | React 19 |
| Build | Vite |
| Iconos | lucide-react |
| Formato de respuesta | react-markdown |
| Backend | Función serverless de Vercel |
| Modelo | Llama 3.1 8B Instruct vía OpenRouter |
| Despliegue | Vercel |

---

## Ejecución local

```bash
git clone https://github.com/Carlosp0607/mediassist-rural.git
cd mediassist-rural
npm install
```

Crea un archivo `.env` en la raíz:

```
OPENROUTER_API_KEY=tu_clave_de_openrouter
```

Levanta la interfaz y la función `/api/chat` juntas con la CLI de Vercel:

```bash
npm install -g vercel
vercel dev
```

---

## Estructura

```
api/chat.js         Función serverless: recibe la consulta y llama al modelo
src/
  App.jsx           Componente raíz y estado de la conversación
  ia.js             Cliente de la API y armado del prompt
  components/       Interfaz de chat, formulario de paciente y alertas
  App.css
public/             Iconos y favicon
vercel.json         Configuración de despliegue
```

---

## Aviso

Esta aplicación entrega orientación general en salud. No emite diagnósticos ni prescribe tratamientos, y no sustituye la consulta con un profesional de la salud. Ante una urgencia, la indicación es llamar al 123.
