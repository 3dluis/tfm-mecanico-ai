# ADR-0005 — Alcance de la validación Docker realizada en Fase 1

**Fecha:** 2026-08-12 · **Estado:** Aceptada · **Fase:** 1

## Contexto

La Fase 1 se ejecutó en un sandbox cloud con Docker instalado pero **sin acceso a registros de imágenes** (Docker Hub y mirrors bloqueados: `403 Forbidden` al resolver `python:3.11-slim-bookworm`). No es posible construir las imágenes ni levantar el compose completo en este entorno.

## Decisión

Registrar explícitamente qué quedó validado y qué no, para que no se confunda "configurado" con "verificado":

**Validado en Fase 1:**
- Sintaxis y coherencia de `docker/compose.yml` en ambos perfiles (`docker compose config`: OK en `dev` y `arm64`).
- Toda la cadena funcional que la imagen debe ejecutar, probada fuera de Docker en el mismo SO base (Linux + Python 3.11): instalación de dependencias (con la restricción setuptools<81), emulador por pty y por TCP, python-OBD, lint/tipos/tests.

**Pendiente de validar en la máquina del autor (acciones A2/A3 del informe):**
1. `docker compose -f docker/compose.yml --profile dev up --build` (build multi-servicio + límites de recursos).
2. `docker buildx build --platform linux/arm64 -f docker/edge.Dockerfile .` (requiere binfmt/QEMU habilitado en Docker Desktop, que en macOS lo trae de serie).

## Consecuencias

- El hito H1 ("entorno reproducible") queda **condicionado** a esas dos validaciones; son la primera tarea al abrir la Fase 2.
- Si el build ARM64 revela ruedas ausentes (p. ej. `onnxruntime` en ARM64 sí existe, pero conviene verificar versiones), se resolverá fijando versiones o compilando en la imagen; registrar el resultado en este ADR (actualización).
