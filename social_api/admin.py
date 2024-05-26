from django.contrib import admin
from .models import Usuario, Publicacion, Comentario, Reaccion, Solicitud

# Register your models here.


admin.site.register(Usuario)
admin.site.register(Publicacion)
admin.site.register(Comentario)
admin.site.register(Reaccion)
admin.site.register(Solicitud)