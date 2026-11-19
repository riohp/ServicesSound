# Guía Rápida: Crear la Skill de Alexa (3 Minutos)

Esta guía te permite crear tu Skill privada y gratuita en la consola de Amazon para que cualquier altavoz Echo de tu casa reproduzca el sonido de tu PC por Wi-Fi.

---

### Paso 1: Entrar a la Consola de Desarrolladores de Amazon
1. Abre en tu navegador: **[https://developer.amazon.com/alexa/console/ask](https://developer.amazon.com/alexa/console/ask)**
2. Inicia sesión con la **misma cuenta de Amazon** con la que tienes configurado tu altavoz Alexa.

---

### Paso 2: Crear la Skill
1. Haz clic en el botón **Create Skill** (Crear Skill).
2. **Skill name:** Escribe `Sound River`.
3. **Primary locale:** Elige `Spanish (ES)` o `Spanish (US / MX)` según tu país.
4. **Choose a model:** Selecciona **Other** -> **Custom**.
5. **Hosting service:** Selecciona **Alexa-hosted (Python)** *(es 100% gratuito y no requiere tarjeta de crédito ni cuenta de AWS externa)*.
6. Haz clic en **Next** (arriba a la derecha) y luego en **Create Skill**.

---

### Paso 3: Activar la Interfaz AudioPlayer
1. En el menú lateral izquierdo, haz clic en **Interfaces**.
2. Activa el interruptor de **Audio Player**.
3. Haz clic en el botón superior **Save Interfaces**.

---

### Paso 4: Configurar el Modelo de Interacción
1. En el menú lateral, ve a **Interaction Model** -> **JSON Editor**.
2. Borra lo que haya en la caja de texto y pega el contenido exacto de:
   👉 `alexa_skill/interaction_model_es.json`
3. Haz clic en **Save Model** y luego en **Build Model** (tarda unos 20-30 segundos en compilar).

---

### Paso 5: Pegar el Código Python
1. En la barra superior, haz clic en la pestaña **Code**.
2. Verás el archivo `lambda_function.py`. Borra su contenido y pega el código de:
   👉 `alexa_skill/lambda_function.py`
3. En la línea 17:
   ```python
   DEFAULT_STREAM_URL = os.environ.get("STREAM_URL", "https://tu-url-de-ngrok.ngrok-free.app/stream.mp3")
   ```
   Reemplaza esa URL por la URL HTTPS pública que genera **ServicesSound** al iniciar.
4. Haz clic en **Save** y luego en **Deploy** (espera que diga *Deployment Successful*).

---

### Paso 6: ¡Probar en tu Altavoz!
1. Asegúrate de que **ServicesSound** esté corriendo en tu PC y transmitiendo.
2. Ve a la pestaña **Test** en la consola de Alexa y cambia el selector de *"Off"* a **"Development"**.
3. Ahora simplemente di a tu altavoz físico Echo:
   **«Alexa, on sound river»** *(o también «Alexa, abre sound river»)*
4. Alexa responderá: *"Conectando al audio de tu computadora"* y empezará a sonar el audio de tu PC por Wi-Fi.
