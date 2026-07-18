---
name: conventional-commit
description: Crea un commit con mensajs descriptivo siguiendo Conventional Commits. Se usa cuando el usuario pide crear, generar, realizar, un commit.
---
# Conventional Commits

Cuando generes un mensaje de commit, seguí estas reglas:

1. Analizá el `git diff --staged` para entender exactamente qué cambios se van a confirmar.
2. Basate únicamente en los cambios que están en *staging*. No supongas cambios que no aparecen en el diff.
3. Elegí el tipo de commit más apropiado:
   - `feat`: nueva funcionalidad.
   - `fix`: corrección de errores.
   - `docs`: cambios en documentación.
   - `refactor`: refactorización sin cambios de comportamiento.
   - `test`: incorporación o modificación de tests.
   - `chore`: tareas de mantenimiento, configuración o dependencias.

4. Escribí el mensaje con el siguiente formato:

   ```text
   tipo(scope): descripción
   ```

   Ejemplos:

   ```text
   feat(auth): agregar validación de email
   fix(api): corregir manejo de timeout
   docs(readme): actualizar instrucciones de instalación
   ```

5. La descripción debe:
   - Estar en español.
   - Estar en minúsculas.
   - Escribirse en modo imperativo.
   - Ser breve y descriptiva.
   - No terminar con punto.
   - Tener un máximo de 72 caracteres.

6. El `scope` es opcional, pero usalo cuando el cambio afecte claramente un módulo, componente o dominio específico.
