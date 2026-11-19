# Las Chicas del Semáforo — Conteo de colonias con IA

MVP para Agronomía: una PWA permite subir fotografías de placas, contar colonias con IA y revisar las detecciones. OpenCV delimita la placa, Grounding DINO con pesos ColonyGroundedSAM2 detecta colonias y SAM2 obtiene sus máscaras. No se entrenó una nueva red en este proyecto.

## Inicio en Windows

1. Extraer el repositorio completo en una carpeta local.
2. Abrir `INICIAR.cmd`. Descarga Python 3.12 portable y prepara el motor IA si aún no está instalado. No necesita Python, Git ni Node instalados.
3. Esperar a que cargue el modelo y se abra la aplicación. La primera instalación descarga varios GB y requiere internet.

Para una laptop sin GPU dedicada, abrir **`INICIAR_IA_CPU.cmd`**. La API elige CPU cuando PyTorch no dispone de CUDA. En CPU se segmenta una caja por lote para reducir memoria. El análisis puede tardar varios minutos según el equipo y la foto.

Si falla la instalación o la carga, el iniciador muestra el error. La API informa `ready: false` y el análisis devuelve HTTP 503 cuando el modelo no está disponible. La interfaz deshabilita el botón de análisis en ese estado.

Opciones desde PowerShell:

```powershell
.\INICIAR.cmd --instalar-ia --device cpu
.\INICIAR.cmd --device auto
.\INICIAR.cmd --puerto 8001 --sin-navegador
```

`--instalar-ia` reinstala o repara las dependencias. Se conservan los pesos ya descargados y se verifican sus hashes. La carpeta `procesamiento/referencias` debe estar presente. Si falta, volver a extraerla del ZIP completo.

El Python portable está en `runtime/`; el entorno neuronal, las dependencias auxiliares y los pesos están en `procesamiento/.venv-neural`, `vendor` y `modelos`. Estas carpetas no se suben a Git. Instalar en cada PC: copiar un entorno virtual entre equipos no sustituye la instalación.

## Acceso desde celulares

El iniciador muestra un enlace y un QR para la misma red wifi. `COMPARTIR.cmd` abre un enlace HTTPS temporal mediante Cloudflare Tunnel para acceder por internet. La PC debe permanecer encendida. Cada enlace incluye una clave de acceso guardada en `runtime/clave.txt`. `INICIAR.cmd --nueva-clave` invalida las anteriores.

## Flujo de análisis

1. Capturar o seleccionar una fotografía.
2. Delimitar la placa mediante OpenCV.
3. Detectar candidatos con Grounding DINO y segmentarlos con SAM2.
4. Filtrar duplicados, regiones demasiado pequeñas y regiones fuera de la placa.
5. Mostrar el conteo y revisar las marcas manualmente.

Las correcciones se guardan separadas de la predicción automática. El sistema no identifica especies. Las fotos se procesan en la PC que ejecuta el servidor.

## Instalación manual y API

Con Python 3.12 disponible, desde `procesamiento`:

```powershell
py -3.12 instalar.py --device cpu
.\.venv-neural\Scripts\python.exe contador_hibrido.py 'C:\ruta\foto.jpg' --device cpu --batch-size 1
```

Para CUDA usar `--device cuda`. Para iniciar directamente la API:

```powershell
$env:IA_DEVICE="auto"
.\.venv-neural\Scripts\python.exe -m uvicorn api:app --host 127.0.0.1 --port 8000
```

`procesamiento/INICIAR_API.cmd` utiliza el iniciador común sin abrir el navegador. En ese caso se aplican los enlaces con clave y acceso por red del iniciador.

Endpoints:

- `GET /health`: disponibilidad de IA, dispositivo y motivo de error si lo hubiera.
- `POST /analyze`: foto multipart en el campo `file`; `engine=auto` y `engine=hybrid` seleccionan la IA.
- `GET /results/{analysis_id}/foto_conteo.jpg`: imagen anotada.
- `GET /results/{analysis_id}/foto_resultado.json`: resultado automático.
- `POST /results/{analysis_id}/review`: correcciones manuales.
- `POST /ufc`: calcula UFC/mL o UFC/g a partir de diluciones y conteos, sin guardar (vista previa de la PWA).
- `POST /results/{analysis_id}/ufc`: calcula UFC con el conteo guardado de esa placa (el revisado si existe) y lo guarda en `ufc.json`, junto a la foto, y en `resultados/api/historial.jsonl`, que conserva cada cálculo sin sobrescribir los anteriores.
- `GET /history` y `GET /history/csv`: análisis guardados, del más reciente al más antiguo, con su revisión y su UFC; el CSV se abre en Excel.

La PWA utiliza el prefijo `/api`. Si se configura clave, se envía como `X-Clave` o con el enlace completo generado. `/docs` permite explorar la API.

Fórmula: UFC/mL (o /g) = promedio de colonias de las placas × 10^n ÷ volumen sembrado (mL), para la dilución 10^-n. Si el promedio queda fuera del rango contable (30–300 por defecto, editable) el resultado se marca como estimación; con 0 colonias se informa el límite de detección. El valor se informa con dos cifras significativas.

Los endpoints `/samples` (muestras con varias diluciones) siguen en desarrollo y la PWA no los usa. La API mantiene el modelo en memoria y serializa los análisis.

## Resultados preliminares

En 38 fotos AGAR conocidas: error absoluto medio de **1,97 colonias/foto**. En la placa 5271 se detectaron **42** frente a una referencia de **43**, con 42 coincidencias, ninguna detección adicional y una omisión según el emparejamiento centro/caja.

Tiempo medio registrado: **1,51 s/foto** con RTX 5060 y modelo cargado; carga inicial de esa ejecución: 13,25 s. En una prueba posterior con CPU, la foto 13895 (2048 × 2048) tomó 31,279 s de análisis y 12,046 s de carga. No representan tiempos garantizados en otras computadoras.

**No es una validación independiente:** los pesos se ajustaron con AGAR y puede existir solapamiento con entrenamiento. Se necesitan fotos propias nuevas y conteos manuales revisados para medir generalización. El emparejamiento centro/caja no equivale a mAP ni evalúa la exactitud de las máscaras.

[Resumen](procesamiento/resultados/RESUMEN_HIBRIDO.md) · [Métricas](procesamiento/resultados/hibrido_v0_3/metricas.csv) · [Registro de evaluación](procesamiento/resultados/hibrido_v0_3/resumen.json).

Para reproducir la evaluación, colocar las fotos y anotaciones en `Dataset/AGAR_representative`. `procesamiento/split.json` registra nombres y hashes. Desde `procesamiento`, ejecutar `evaluar_hibrido.py` con el entorno neuronal y después `generar_informe_hibrido.py`. Las anotaciones se leen después de inferir y no entran al detector.

## Pruebas y estructura

```powershell
cd procesamiento
.\.venv-neural\Scripts\python.exe -m unittest discover -p "test_*.py"
```

En `pwa`, ejecutar `npm test` y `npm run build` al cambiar la interfaz. La compilación en `procesamiento/web` se incluye en Git para no requerir Node en la laptop de destino.

- `contador_hibrido.py`: detección, segmentación y filtrado.
- `imagen.py`: lectura de fotos y geometría de la placa.
- `app/`: controladores, servicios y validación de la API.
- `lanzador.py` e `instalar.py`: instalación e inicio en CPU o CUDA.
- `metricas.py`: evaluación contra anotaciones.

## Presentación

[PowerPoint del equipo](docs/MVP_Conteo_Colonias_Equipo7.pptx), con el flujo y los resultados de IA.

## Fuentes

- [ColonyGroundedSAM2](https://github.com/WFSRDataScience/ColonyGroundedSAM2) y [pesos publicados](https://huggingface.co/DataScienceWFSR/ColonyGroundedSAM2).
- [Grounding DINO](https://github.com/IDEA-Research/GroundingDINO).
- [SAM2](https://github.com/facebookresearch/sam2).
- [BERT base uncased](https://huggingface.co/google-bert/bert-base-uncased).

Los hashes y commits de referencia están en `procesamiento/referencias`. Los modelos y repositorios auxiliares mantienen las condiciones y licencias de sus autores.
