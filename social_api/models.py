from django.db import models

# Create your models here.


class Usuario(models.Model):
    nombre_usuario = models.CharField(max_length=50)
    # para indicar que cada valor en ese campo debe ser único en toda la tabla de la base de datos
    correo_electronico = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_usuario


class Publicacion(models.Model):
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    contenido = models.TextField(blank=True, null=True)
    # los parámetros hacen que este campo sea opcional en el formulario de creación de publicaciones
    imagen = models.ImageField(
        upload_to='publicaciones/images', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.autor}: {self.contenido}'


class Comentario(models.Model):
    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.autor}: {self.contenido[:50]}'


class Reaccion(models.Model):
    reacciones = [
        ('like', 'Me gusta'),
        ('dislike', 'No me gusta')
    ]

    autor = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    tipo_reaccion = models.CharField(max_length=20, choices=reacciones)

    def __str__(self):
        return f'{self.autor}: {self.tipo_reaccion}'
    

class Solicitud(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada')
    ]
    
    solicitante = models.ForeignKey(Usuario, related_name='solicitudes_enviadas', on_delete=models.CASCADE)
    solicitado = models.ForeignKey(Usuario, related_name='solicitudes_recibidas', on_delete=models.CASCADE)
    estado_solicitud = models.CharField(max_length=20, choices=ESTADO_CHOICES)

    def __str__(self):
        return f"Solicitud de {self.solicitante} a {self.solicitado} ({self.estado_solicitud})"

    def aceptar(self):
        self.estado_solicitud = 'aceptada'
        self.save()

    def rechazar(self):
        self.estado_solicitud = 'rechazada'
        self.save()
