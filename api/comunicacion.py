<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>RADAR ALPHA | TEST DE COMUNICACIÓN</title>
    <style>
        body { 
            background: #0b1117; 
            color: #d4af37; 
            font-family: 'Courier New', monospace; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            height: 100vh; 
            margin: 0; 
        }
        .radar-box { 
            border: 3px solid #d4af37; 
            padding: 40px; 
            border-radius: 20px; 
            text-align: center; 
            background: #161b22; 
            box-shadow: 0 0 30px rgba(212, 175, 55, 0.3); 
            width: 80%;
            max-width: 500px;
        }
        .letra { 
            font-size: 120px; 
            font-weight: bold; 
            color: #3fb950; 
            margin: 20px 0; 
            text-shadow: 0 0 20px rgba(63, 185, 80, 0.6); 
        }
        .status { 
            font-size: 14px; 
            color: #58a6ff; 
            border-top: 1px solid #30363d; 
            padding-top: 20px; 
            text-align: left;
            word-break: break-all;
        }
    </style>
</head>
<body>

    <div class="radar-box">
        <h1 style="margin:0">🛰️ RADAR ALPHA</h1>
        <p>Buscando señal en Vercel...</p>
        
        <div id="display">
            <div style="color:#8b949e">ESCANEO EN CURSO...</div>
        </div>

        <div id="log" class="status">Protocolo iniciado...</div>
    </div>

    <script>
        // DIRECCIÓN EXACTA DE TU VERCEL
        const RUTA_VERCEL = "https://consola-opal.vercel.app/api/comunicacion";

        async function ejecutarEscaneo() {
            const display = document.getElementById('display');
            const log = document.getElementById('log');

            try {
                log.innerText = ">> Intentando conectar con: " + RUTA_VERCEL;
                
                // Realizamos la petición
                const respuesta = await fetch(RUTA_VERCEL);
                
                if (!respuesta.ok) {
                    throw new Error("Respuesta de servidor NO OK. Código: " + respuesta.status);
                }

                const data = await respuesta.json();

                // ÉXITO TOTAL: Mostramos la Z verde
                display.innerHTML = `<div class="letra">${data.letra}</div>`;
                log.innerHTML = `✅ SEÑAL RECIBIDA CON ÉXITO<br>MENSAJE: ${data.mensaje || 'Establecido'}<br>ARCHIVO: ${data.archivo || 'comunicacion.py'}`;
                log.style.color = "#3fb950";

            } catch (err) {
                // FALLO: Mostramos la X roja y el motivo
                display.innerHTML = `<div style="font-size:60px">📡❌</div>`;
                log.innerHTML = `❌ ERROR DE CONEXIÓN:<br>${err.message}<br><br><span style="color:#8b949e">Asegúrate de que en Vercel el archivo sea comunicacion.py y tenga los permisos CORS.</span>`;
                log.style.color = "#f85149";
                console.error("Detalle del error:", err);
            }
        }

        // Iniciar escaneo al cargar la página
        window.onload = ejecutarEscaneo;
    </script>
</body>
</html>
