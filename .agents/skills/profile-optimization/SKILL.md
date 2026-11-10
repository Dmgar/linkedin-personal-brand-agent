---
name: profile-optimization
description: >-
  Use this skill when the user wants to audit, optimize, or rewrite sections of their LinkedIn profile,
  including Headline (Titular), About (Acerca de), Featured section (Destacados), Experience, Education,
  Projects, or Skills, ensuring alignment with their professional identity in knowledge/professional-identity.md.
---

# Skill: Estratega y Optimizador de Perfil (`profile-optimization`)

Este skill guía la auditoría y redacción de mejoras estratégicas para el perfil de LinkedIn del usuario, basándose en su identidad local (`knowledge/professional-identity.md`), su inventario técnico (`knowledge/skills.md`) y sus proyectos documentados (`knowledge/projects/`). Como la API oficial de LinkedIn no permite modificar campos del perfil programáticamente, todas las propuestas se preparan en archivos locales listos para revisión y copia manual.

---

## 1. Principios de Posicionamiento del Perfil

1. Lee siempre primero `knowledge/professional-identity.md`, `knowledge/skills.md` y todas las fichas dentro de `knowledge/projects/`.
2. El perfil debe proyectar la **propuesta de valor diferencial** del usuario: no una lista pasiva de herramientas, sino cómo conecta su dominio profesional con la ejecución técnica y los resultados tangibles.

---

## 2. Módulos del Perfil a Optimizar

### A. Titular (Headline) — Máximo 220 caracteres
Fórmula recomendada: `[Rol / Identidad Principal] | [Especialidad Técnica y de Dominio] | [Stack / Valor Diferencial]`
- Presenta siempre **3 variantes** según el objetivo profesional del usuario (ej. enfoque corporativo/comercial, enfoque técnico/ingeniería, y enfoque híbrido/investigación).

### B. Acerca de (About / Extracto) — Máximo 2.600 caracteres
Estructura en 4 bloques claros:
1. **Propuesta de valor inicial (2 líneas):** Qué problemas resuelve y cuál es su enfoque de trabajo.
2. **Lo que construye en la práctica:** Mención concreta a sus proyectos e iniciativas verificables documentadas en `knowledge/projects/`.
3. **Arsenal técnico por capas:** Agrupado de forma limpia según `knowledge/skills.md`.
4. **Cierre y contacto:** Áreas de colaboración o roles de interés.

### C. Sección de Destacados (Featured)
Selecciona los 3 a 4 proyectos, repositorios, demos en vivo o publicaciones de mayor impacto visual y comercial del usuario, explicando qué título, descripción breve y miniatura usar para cada uno.

### D. Proyectos y Experiencia
Para cada proyecto en la sección de *Proyectos* o *Experiencia* de LinkedIn, redacta descripciones con el método **Problema → Arquitectura/Método → Resultado**, más la lista exacta de aptitudes (Skills) que deben vincularse a cada ítem.
