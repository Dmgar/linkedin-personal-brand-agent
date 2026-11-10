---
name: performance-analytics
description: >-
  Use this skill when the user shares metrics from their LinkedIn posts (impressions, reactions,
  comments, reposts, profile views) or asks to analyze content performance in analytics/performance-history.csv
  and generate strategic adjustments or monthly reports.
---

# Skill: Analista de Rendimiento y Evolución (`performance-analytics`)

Este skill procesa las métricas de las publicaciones de LinkedIn registradas en `analytics/performance-history.csv` y genera diagnósticos accionables para afinar la estrategia editorial.

---

## 1. Métricas Clave y Lectura Estratégica

En una marca profesional técnica, las impresiones brutas no son el único indicador. Evaluamos tres niveles de señal:

1. **Tasa de Interacción Cualitativa:**
   - Comentarios con sustancia técnica o de negocio y guardados/compartidos pesan más que un "Me gusta" superficial.
2. **Rendimiento por Pilar Editorial:**
   - Comparar qué pilar (*Ciencia de Datos/BI*, *Economía Aplicada*, *Innovación/Sistemas*, *Desarrollo Profesional*) atrae más visitas al perfil y conversaciones relevantes.
3. **Rendimiento por Formato Visual:**
   - Contrastar publicaciones con captura de dashboard vs. carrusel PDF vs. diagrama técnico.

---

## 2. Procedimiento de Actualización y Reporte

1. **Registro de Datos:**
   - Cuando el usuario comparta los resultados de una publicación (a los 3 o 7 días de publicada), actualiza la fila correspondiente en `analytics/performance-history.csv`.
2. **Cálculo de Indicadores:**
   - Calcula el Engagement Rate estimado: `(reactions + comments * 2 + reposts * 3) / impressions`.
3. **Informe Mensual (`analytics/monthly-reports/YYYY-MM.md`):**
   - Resume los posts publicados en el mes.
   - Identifica el gancho (hook) y el proyecto que mejor funcionaron.
   - Propone ajustes concretos para las 4 semanas siguientes en `content/editorial-calendar.md`.
