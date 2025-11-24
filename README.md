# Doc Anonymizer (MVP)

Aplicación sencilla para anonimizar documentos (DOCX y PDF) sustituyendo texto sensible según un conjunto de reglas definido en YAML. Incluye:

- **Interfaz web** con Streamlit para subir varios archivos y descargar las versiones anonimizada.
- **Watcher** basado en `watchdog` para procesar automáticamente los archivos que aparezcan en una carpeta de entrada.
- **Núcleo** de anonimización configurable mediante expresiones regulares y reemplazos exactos.

## Requisitos

- Python 3.10 o superior.
- Dependencias indicadas en `requirements.txt`. Para evitar instalaciones pesadas (por ejemplo, modelos de spaCy), puedes comenzar con los paquetes mínimos usados por el flujo principal:

```bash
pip install python-docx pypdf reportlab PyYAML streamlit watchdog
```

Si prefieres instalar todo (incluidas las opciones de NLP/OCR), ejecuta:

```bash
pip install -r requirements.txt
```

## Configuración de reglas

Las reglas se definen en `config/rules.yaml`. Incluyen ejemplos pensados para datos comunes en España (NIF/CIF, teléfonos, correos, direcciones y nombres de clientes). Puedes editar las secciones `entities` para adaptar los patrones y reemplazos a tus necesidades.

## Ejecución de la interfaz web

1. Coloca el repositorio en tu máquina local.
2. Instala las dependencias.
3. Ejecuta Streamlit desde la raíz del proyecto:

```bash
streamlit run src/app_streamlit.py
```

4. Sube uno o varios archivos DOCX/PDF; la aplicación generará un enlace de descarga con la versión anonimizada.

## Ejecución del watcher de carpeta

1. Crea (si no existen) las carpetas `input/` y `output/` en la raíz del repositorio.
2. Inicia el watcher:

```bash
python src/watcher.py
```

3. Copia archivos DOCX o PDF en `input/`; las versiones procesadas aparecerán en `output/`.

## Cómo funciona el anonimizado

1. **Reemplazos exactos**: `exact_replacements` aplica sustituciones directas (p. ej. “KFC España” → “ABC S.A.”).
2. **Reemplazos con regex**: `regex_replacements` y las reglas de `entities` aplican patrones para detectar identificadores, correos, teléfonos, etc. El valor `replacement` o `replacement_value` define el texto final.
3. El módulo `anonymizer_core.py` coordina la carga de reglas y la aplicación secuencial de estas transformaciones.

## Notas sobre DOCX y PDF

- El manejador DOCX reescribe el texto de cada párrafo para priorizar simplicidad, por lo que ciertos estilos muy granulares pueden perderse si el texto estaba dividido en múltiples *runs*.
- Los PDF se leen con `pypdf` y se regeneran con `reportlab` como texto plano. El formato original puede variar en la salida.

## Pruebas rápidas

Puedes validar el flujo principal con los scripts incluidos (recuerda establecer `PYTHONPATH=src` para que Python encuentre los módulos):

```bash
# Prueba de anonimizado de texto
PYTHONPATH=src python - <<'PY'
from anonymizer_core import anonymize_text
text = "Contacto: KFC España, CIF A12345678 y correo demo@empresa.es"
print(anonymize_text(text, 'config/rules.yaml')[0])
PY

# Prueba de DOCX
PYTHONPATH=src python - <<'PY'
from pathlib import Path
from docx import Document
from handlers_docx import anonymize_docx

tmp_in = Path('demo.docx')
doc = Document()
doc.add_paragraph('Cliente KFC España con CIF A12345678 y email demo@empresa.es')
doc.save(tmp_in)

anonymize_docx(str(tmp_in), 'demo_out.docx', 'config/rules.yaml')
print('DOCX procesado:', Path('demo_out.docx').exists())
PY
```

¡Listo! Con esto deberías poder ejecutar y extender el MVP para tus casos de anonimización.
