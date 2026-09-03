# Consulta de sugerencias ImFoS 2026

Aplicación Streamlit para que los autores consulten, mediante su número de
identificación, las sugerencias asociadas a sus ponencias.

Si una identificación aparece en varias filas, la aplicación muestra todas las
ponencias encontradas, cada una con su título y su sugerencia.

## Estructura esperada del libro

La hoja debe llamarse `Respuestas de formulario 1` y contener estas columnas:

- `Nombres y Apellidos`
- `Número de identificación`
- `Título de la Ponencia`
- `Sugerencia para enriquecer el trabajo (máx. 500 caracteres)`

La búsqueda ignora puntos, espacios y guiones del número de identificación.

## Ejecución local

1. Crea un entorno virtual e instala `requirements.txt`.
2. Conserva una copia del libro con el nombre `Inscripciones ImFos (2026).xlsx`
   en la carpeta del proyecto.
3. Ejecuta `streamlit run app.py`.

## Configuración en Streamlit Community Cloud

1. Publica este proyecto en un repositorio de GitHub.
2. En Streamlit Community Cloud, crea una aplicación usando `app.py`.
3. En **Settings > Secrets**, agrega la URL publicada que entrega el Excel:

```toml
DATA_EXCEL_URL = "https://docs.google.com/spreadsheets/d/e/ID_PUBLICO/pub?output=xlsx"
```

La aplicación vuelve a consultar la fuente cada cinco minutos, por lo que las
actualizaciones publicadas aparecerán sin cambiar el código.

## Privacidad

El archivo Excel y `secrets.toml` están excluidos de Git. No deben subirse al
repositorio porque contienen datos personales. La aplicación solo muestra los
campos necesarios para la consulta y no registra el número ingresado.
