from django.db import models

class Usuario(models.Model):
    nombre = models.CharField(max_length=150)
    correo = models.EmailField(unique=True)  # Evita correos repetidos en /registro
    ubicacion = models.CharField(max_length=255)
    hectareas = models.FloatField()

    class Meta:
        db_table = "usuarios"

    def __str__(self):
        return f"{self.nombre} ({self.correo})"