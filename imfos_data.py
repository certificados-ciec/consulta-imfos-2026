from __future__ import annotations

import io
import re
import unicodedata
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd


SHEET_NAME = "Respuestas de formulario 1"
REQUIRED_FIELDS = {
    "name": "nombres y apellidos",
    "identification": "numero de identificacion",
    "title": "titulo de la ponencia",
    "suggestion": "sugerencia para enriquecer el trabajo",
}


class DataSourceError(RuntimeError):
    """Raised when the workbook cannot be obtained or interpreted."""


def _canonical_text(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text).strip().lower()


def normalize_identification(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return re.sub(r"\D", "", text)


def _find_column(columns: list[object], expected: str) -> object:
    expected_key = _canonical_text(expected)
    for column in columns:
        if _canonical_text(column).startswith(expected_key):
            return column
    raise DataSourceError(f"No se encontró la columna requerida: {expected}")


def _download_workbook(url: str) -> bytes:
    try:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "ImFoS-Streamlit/1.0"},
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        raise DataSourceError("No se pudo descargar el libro de OneDrive") from exc

    if not content.startswith(b"PK"):
        raise DataSourceError(
            "La URL configurada no entregó un archivo Excel. "
            "Debe ser un enlace de descarga directa."
        )
    return content


def _read_workbook(source: Path | io.BytesIO) -> pd.DataFrame:
    try:
        workbook = pd.ExcelFile(source)
        if SHEET_NAME in workbook.sheet_names:
            selected_sheet = SHEET_NAME
        elif len(workbook.sheet_names) == 1:
            selected_sheet = workbook.sheet_names[0]
        else:
            raise DataSourceError(
                f"No se encontró la hoja requerida: {SHEET_NAME}"
            )
        frame = pd.read_excel(workbook, sheet_name=selected_sheet, dtype=str)
    except DataSourceError:
        raise
    except Exception as exc:
        raise DataSourceError("No se pudo leer la hoja de inscripciones") from exc

    columns = list(frame.columns)
    selected = {
        field: _find_column(columns, expected)
        for field, expected in REQUIRED_FIELDS.items()
    }
    result = frame[[selected[field] for field in REQUIRED_FIELDS]].copy()
    result.columns = list(REQUIRED_FIELDS)

    for column in ("name", "title", "suggestion"):
        result[column] = result[column].fillna("").astype(str).str.strip()
    result["identification"] = result["identification"].map(normalize_identification)
    return result[result["identification"] != ""].reset_index(drop=True)


def load_submissions(
    *,
    remote_url: str | None,
    local_path: Path,
) -> pd.DataFrame:
    """Load current submissions from a published URL or local development copy."""
    if remote_url:
        return _read_workbook(io.BytesIO(_download_workbook(remote_url)))
    if local_path.is_file():
        return _read_workbook(local_path)
    raise DataSourceError("No hay una fuente de datos configurada")


def search_by_id(frame: pd.DataFrame, identification: object) -> pd.DataFrame:
    normalized = normalize_identification(identification)
    if len(normalized) < 5:
        return frame.iloc[0:0].copy()
    return frame.loc[frame["identification"] == normalized].reset_index(drop=True)
