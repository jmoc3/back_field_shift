from django.db import models
from usuarios.models import Usuario

class Rotacion(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="rotaciones",
        db_column="id_usuario"  # Mantiene el nombre exacto de columna pedido
    )
    rotacion = models.CharField(max_length=255)
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = "rotaciones"

    def __str__(self):
        estado = "Activa" if self.activa else "Inactiva"
        return f"{self.rotacion} - {self.usuario.nombre} ({estado})"