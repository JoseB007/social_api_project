from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('registro', views.registro ,name='registro'),
    path('logout', views.logout, name='logout'),
    path('login', views.login, name='login'),
    path('perfil/<str:nombre_usuario>', views.perfil, name='perfil'),
    path('login/', views.reaccion_publicacion, name='reaccion'),
    path('actualizar_perfil', views.actualizar_perfil, name='actualizar_perfil'),
    path('eliminar_publicacion/<int:id_publicacion>', views.eliminar_publicacion, name='eliminar_publicacion'),
    path('crear_publicacion', views.nueva_publicacion, name='crear_publicacion'),
    path('actualizar_publicacion', views.actualizar_publicacion, name='actualizar_publicacion'),
    path('comentario', views.nuevo_comentario, name='comentario'),
    path('agregar_amigo', views.agregar_amigo, name='agregar_amigo'),
    path('aceptar_amigo', views.aceptar_amigo, name='aceptar_amigo'),
    path('eliminar_amigo', views.eliminar_amigo, name='eliminar_amigo'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)