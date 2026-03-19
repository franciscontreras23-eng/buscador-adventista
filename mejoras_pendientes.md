# Mejoras Pendientes - Buscador de Libros

## 1. Integración con NotebookLM (MCP)
- Conectar este buscador directamente con NotebookLM para generar reportes profundos, guías de estudio, y respuestas detalladas usando directamente los PDFs de la biblioteca como fuentes (Sources) inteligentes.

## 2. Refinamiento del umbral de Relevancia
- Ajustar experimentalmente el porcentaje o puntaje `Puntos_IA` si en el futuro notamos que el modelo recorta libros legítimos debido a interpretaciones sintácticas.

## 3. Caché y Base de Datos (Vector Search real)
- Implementar ChromaDB o Pinecone para almacenar *Embeddings* verdaderos (Vectores) de los títulos o resúmenes en lugar de usar Regex Dinámico, logrando búsquedas semánticas perfectas libres de la cuota de la API.
