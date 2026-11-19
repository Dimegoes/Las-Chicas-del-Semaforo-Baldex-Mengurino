# PWA de conteo de UFC (primera versión)

Interfaz React con el flujo: **inicio → foto de la placa → resultado con corrección manual → cálculo de UFC → historial**. Usa `/health`, `/analyze`, `/results/{id}/…`, `/results/{id}/review`, `/ufc`, `/results/{id}/ufc` y `/history`.

Para **usar** la app no hace falta Node: `INICIAR.cmd` (raíz del repositorio) sirve la versión compilada de `procesamiento/web/`. Esta carpeta es solo para **modificar** la interfaz.

## Requisitos para desarrollar

- Node 22 y npm.
- La API corriendo: `procesamiento\INICIAR_API.cmd`. Instala y carga el motor IA. Si no está disponible, el análisis queda deshabilitado.

## Desarrollo

```powershell
cd pwa
npm install
npm run dev
```

Abrir http://localhost:5173. Vite reenvía `/api` a `http://127.0.0.1:8000`; con `API_URL` se puede apuntar a otra instancia. Desde un celular en la misma red usar la IP que imprime Vite (por ejemplo `http://192.168.1.20:5173`). Por HTTP en red local la cámara funciona como subida de archivo, pero el navegador no ofrece instalar la PWA.

## Compilar

```powershell
npm run build
```

La build se escribe en `procesamiento/web/`. Después de cambiar la interfaz, compilar y versionar esa carpeta para que `INICIAR.cmd` sirva la versión nueva. `npm run preview` la abre en http://localhost:4173 para probarla como app instalable (**Instalar aplicación** en Chrome o Edge). El service worker solo guarda la interfaz; fotos y resultados siempre vienen de la API.

## Pruebas

```powershell
npm test
```

## Pantallas

1. **Inicio:** escudo UNALM, estado del motor, acceso al historial y últimos análisis de este dispositivo.
2. **Registro fotográfico:** capturar o elegir de galería, vista previa y análisis con IA.
3. **Resultado del análisis:** conteo, colonias cerca del borde, corrección tocando la imagen (quitar o añadir) y **Guardar revisión**. La revisión se guarda aparte en `revision.json`; la predicción original no cambia.
4. **Cálculo de UFC** (debajo del conteo): dilución de la placa, volumen sembrado, UFC/mL o UFC/g, placa duplicada opcional, rango contable y datos de la muestra (código, tipo, responsable, observaciones). Muestra el resultado con la fórmula y sus números mientras se escribe. **Guardar en el historial** guarda primero la revisión si hay cambios y luego el cálculo en `ufc.json`, junto a la foto.
5. **Historial:** todos los análisis del servidor con miniatura, fecha, conteo y UFC; botón **CSV** para descargarlo.

Muestras con varias diluciones agrupadas y el reporte PDF quedan para una siguiente versión (`/samples` sigue en desarrollo).
