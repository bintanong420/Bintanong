"""Lazy Docling import, version guard, CUDA check and converter cache."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as package_version
from pathlib import Path
from typing import Any
import os
import re
import subprocess
import sys


class DoclingUnavailable(RuntimeError):
    """Raised when a PDF must be converted but Docling is not importable."""


def _venv_python() -> Path | None:
    """Locate a sibling .docling-venv interpreter (Windows or POSIX layout)."""
    root = Path(__file__).resolve().parent / ".docling-venv"
    for rel in ("Scripts/python.exe", "bin/python", "bin/python3"):
        candidate = root / rel
        if candidate.exists():
            return candidate
    return None


def _docling_importable() -> bool:
    try:
        import docling  # noqa: F401
        import docling_core  # noqa: F401

        return True
    except Exception:
        return False


def ensure_docling_env() -> None:
    """Re-exec inside .docling-venv once, if Docling is missing here but present there.

    v1 had two competing relaunch mechanisms guarded by two different env
    vars, which could double-launch. This is the single entry point, and it is
    only called when a PDF actually has to be converted.
    """
    if _docling_importable() or os.environ.get("_PALSU_RELAUNCHED"):
        return
    venv_py = _venv_python()
    if not venv_py:
        return
    env = os.environ.copy()
    env["_PALSU_RELAUNCHED"] = "1"
    print(f"[*] Docling not available here; re-launching via {venv_py}", flush=True)
    sys.exit(subprocess.call([str(venv_py), *sys.orig_argv[1:]], env=env))


_DOCLING_CACHE: dict[str, Any] = {}


def _version_tuple(value: str) -> tuple[int, ...]:
    nums = re.findall(r"\d+", value or "")
    return tuple(int(n) for n in nums[:4]) or (0,)


def _require_safe_docling_parse() -> str:
    try:
        installed = package_version("docling-parse")
    except PackageNotFoundError as exc:
        raise DoclingUnavailable(
            "docling-parse is not installed. Run repair_docling_env.ps1 or install "
            "`docling==2.129.0` and `docling-parse>=7.20,<8` in .docling-venv."
        ) from exc
    if _version_tuple(installed) < (7, 12, 0):
        raise DoclingUnavailable(
            f"docling-parse {installed} is affected by the native preprocess memory bug "
            "that manifests as repeated std::bad_alloc. Upgrade to >=7.12; "
            "Bintanong pins >=7.20."
        )
    return installed


def load_docling() -> dict[str, Any]:
    if _DOCLING_CACHE:
        return _DOCLING_CACHE
    _require_safe_docling_parse()
    try:
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import (
            AcceleratorDevice,
            AcceleratorOptions,
            PdfPipelineOptions,
            TableFormerMode,
        )
        from docling.document_converter import DocumentConverter, PdfFormatOption
        from docling.backend.docling_parse_v4_backend import DoclingParseV4DocumentBackend
        from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
        from docling_core.transforms.chunker import HierarchicalChunker
        from docling_core.types.doc import DoclingDocument
    except ImportError as exc:
        raise DoclingUnavailable(
            "Docling is required to convert PDFs. Rebuild .docling-venv with "
            "`docling==2.129.0` / `docling-parse>=7.20,<8`."
        ) from exc

    _DOCLING_CACHE.update(
        {
            "InputFormat": InputFormat,
            "AcceleratorDevice": AcceleratorDevice,
            "AcceleratorOptions": AcceleratorOptions,
            "PdfPipelineOptions": PdfPipelineOptions,
            "TableFormerMode": TableFormerMode,
            "DocumentConverter": DocumentConverter,
            "PdfFormatOption": PdfFormatOption,
            "DoclingParseV4DocumentBackend": DoclingParseV4DocumentBackend,
            "PyPdfiumDocumentBackend": PyPdfiumDocumentBackend,
            "HierarchicalChunker": HierarchicalChunker,
            "DoclingDocument": DoclingDocument,
        }
    )
    return _DOCLING_CACHE


def check_cuda_environment() -> dict[str, Any]:
    """Inspect GPU hardware and PyTorch CUDA capability with honest diagnostics."""
    info: dict[str, Any] = {
        "has_gpu_hardware": False,
        "gpu_name": None,
        "torch_available": False,
        "torch_version": None,
        "cuda_available": False,
        "cuda_device_count": 0,
        "cuda_device_name": None,
        "status_message": "",
    }
    try:
        import torch
    except Exception:
        torch = None  # type: ignore[assignment]

    if torch is not None:
        info["torch_available"] = True
        info["torch_version"] = getattr(torch, "__version__", None)
        if hasattr(torch, "cuda") and torch.cuda.is_available():
            info["has_gpu_hardware"] = True
            info["cuda_available"] = True
            info["cuda_device_count"] = torch.cuda.device_count()
            info["cuda_device_name"] = (
                torch.cuda.get_device_name(0) if info["cuda_device_count"] else "CUDA Device"
            )
            info["gpu_name"] = info["cuda_device_name"]
            info["status_message"] = (
                f"CUDA active: {info['cuda_device_name']} (PyTorch {info['torch_version']})"
            )
            return info

    try:
        smi = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=15,
        ).strip()
        names = [line.strip() for line in smi.splitlines() if line.strip()]
        if names:
            info["has_gpu_hardware"] = True
            info["gpu_name"] = names[0]
    except Exception:
        pass

    if info["has_gpu_hardware"]:
        info["status_message"] = (
            f"NVIDIA GPU detected ({info['gpu_name']}), but PyTorch "
            f"({info['torch_version'] or 'not installed'}) has no CUDA support. Using CPU."
        )
    else:
        info["status_message"] = "No CUDA GPU available. Using CPU."
    return info


def get_pipeline_options(device: str = "auto") -> Any:
    dl = load_docling()
    options = dl["PdfPipelineOptions"]()
    env = check_cuda_environment()
    want = (device or "auto").strip().lower()

    if want == "cpu":
        chosen = dl["AcceleratorDevice"].CPU
        print("[*] Acceleration: CPU (explicitly selected).")
    elif env["cuda_available"]:
        chosen = dl["AcceleratorDevice"].CUDA
        print(f"[+] Acceleration: CUDA ({env['cuda_device_name']}).")
    else:
        chosen = dl["AcceleratorDevice"].CPU
        print("[*] Acceleration: CPU. " + env["status_message"])

    options.accelerator_options = dl["AcceleratorOptions"](device=chosen)
    options.do_ocr = False
    options.force_backend_text = True
    options.do_table_structure = True
    options.table_structure_options.mode = dl["TableFormerMode"].ACCURATE

    raw = os.environ.get("PALSU_DOCLING_CELL_MATCHING", "true").strip().lower()
    options.table_structure_options.do_cell_matching = raw in {"1", "true", "yes", "on"}

    for attr in ("generate_page_images", "generate_picture_images"):
        if hasattr(options, attr):
            setattr(options, attr, False)
    return options


_SHARED_CONVERTERS: dict[tuple[str, str], Any] = {}


def get_shared_converter(device: str = "auto", backend: str = "docling_parse") -> Any:
    dl = load_docling()
    dev = (device or "auto").strip().lower()
    backend_key = (backend or "docling_parse").strip().lower()
    key = (dev, backend_key)
    if key not in _SHARED_CONVERTERS:
        opts = get_pipeline_options(device=dev)
        backend_cls = (
            dl["PyPdfiumDocumentBackend"]
            if backend_key == "pypdfium2"
            else dl["DoclingParseV4DocumentBackend"]
        )
        _SHARED_CONVERTERS[key] = dl["DocumentConverter"](
            format_options={
                dl["InputFormat"].PDF: dl["PdfFormatOption"](
                    pipeline_options=opts,
                    backend=backend_cls,
                )
            }
        )
    return _SHARED_CONVERTERS[key]
