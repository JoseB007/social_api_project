from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse
from .models import Usuario, Publicacion, Comentario, Reaccion, Solicitud

# Create your views here.


def home(request):
    # Recuperar el ID del usuario almacenado en la sesión
    id_usuario = request.session.get('id_usuario')

    # Consultar TODAS las publicaciones de la base de datos
    publicaciones = Publicacion.objects.all().order_by('-fecha_creacion')

    # Consultar en la base de datos los tipos de reacciones que el ususario puede escojer
    reacciones = Reaccion.reacciones

    # Consultar en la db todos los comentarios
    comentarios = Comentario.objects.all()
    
    # Manejar el caso donde exista una sesión de usuario en específico
    if id_usuario:
        usuario_autenticado = Usuario.objects.get(id=id_usuario)
        usuario = Usuario.objects.get(id=id_usuario)

        # Consultar las reacciones del usuario
        reacciones_usuario = Reaccion.objects.filter(autor=usuario.id)

        # Crear un conjunto para almacenar los IDs de las publicaciones reaccionadas
        publicaciones_reaccionadas_like = set()
        publicaciones_reaccionadas_dislike = set()

        # Iterar sobre las reacciones del usuario
        for reaccion_usuario in reacciones_usuario:
            if reaccion_usuario.tipo_reaccion == 'like':
                publicaciones_reaccionadas_like.add(reaccion_usuario.publicacion.id)
            elif reaccion_usuario.tipo_reaccion == 'dislike':
                publicaciones_reaccionadas_dislike.add(reaccion_usuario.publicacion.id)

        return render(request, 'index.html', {
        'publicaciones': publicaciones,
        'usuario': usuario,
        'reacciones': reacciones,
        'publicaciones_reaccionadas_like': publicaciones_reaccionadas_like,
        'publicaciones_reaccionadas_dislike': publicaciones_reaccionadas_dislike,
        'usuario_autenticado': usuario_autenticado,
        'comentarios': comentarios,
    })

    return render(request, 'index.html', {
        'publicaciones': publicaciones,
        'reacciones': reacciones,
        'comentarios': comentarios,
    })


def login(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre_usuario = request.POST.get('nombre_usuario')
        password = request.POST.get('password')

        # Validar los campos
        if not nombre_usuario or not password:
            error_message = 'Los campos no pueden estar vacios'
            request.session['errorCampoVacio'] = error_message
            return render(request, 'login.html', {
                'error_message': error_message
            })

        # Buscar usuarios que tengan el mismo nombre de usuario
        usuarios = Usuario.objects.filter(nombre_usuario=nombre_usuario)

        # Iterar sobre los usuarios encontrados
        for usuario in usuarios:
            # Verificar si la contraseña coincide
            if usuario.password == password:
                # Almacenar los datos del usuario en la sesión
                request.session['id_usuario'] = usuario.id

                return redirect('/')
            
        # Si ninguna contraseña coincide, devolver un mensaje de error
        error_datos = 'Nombre de usuario o contraseña incorrectos'
        request.session['error_datos'] = error_datos
        return render(request, 'login.html', {
            'error_datos': error_datos
        })

    else:
        return render(request, 'login.html')


def logout(request):
    # Cerrar la sesión del Usuario
    try:
        del request.session['id_usuario']
    except KeyError:
        pass

    return redirect('/')


def registro(request):
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre_usuario = request.POST.get('nombre_usuario')
        correo_electronico = request.POST.get('correo_electronico')
        password = request.POST.get('password')

        # Validar los campos
        if not nombre_usuario or not correo_electronico or not password:
            error_message = 'Los campos no pueden estar vacios'
            request.session['errorCampoVacio'] = error_message
            return render(request, 'registro.html', {
                'error_message': error_message
            })

        if Usuario.objects.filter(correo_electronico=correo_electronico).exists():
            return HttpResponse('El correo electrónico ya está en uso')

        # Crear el usuario
        usuario = Usuario.objects.create(nombre_usuario=nombre_usuario,
                               correo_electronico=correo_electronico, password=password)
        usuario.save()
        
        # Iniciar la sesión de usuario con el nuevo registro
        if request.session.get('id_usuario'):
            del request.session['id_usuario']

        request.session['id_usuario'] = usuario.id

        return redirect('/')

    else:
        return render(request, 'registro.html')


def perfil(request, nombre_usuario):

    # Consultar en la db el usuario que estamos pasando a través de la URL
    usuario = get_object_or_404(Usuario, nombre_usuario=nombre_usuario)

    # Consultar las publicaciones que el usuario ha hecho
    publicaciones = Publicacion.objects.filter(autor=usuario).order_by('-fecha_creacion')

    # Consultar las reacciones disponibles para todos los usuarios
    reacciones = Reaccion.reacciones

    # Consultar en la db los tipos de estados de solicitud de amistad
    solicitudes = Solicitud.ESTADO_CHOICES

    # Crear una lista para almacenar el tipo de solicitudes
    tipo_solicitudes = []

    # Recorrer los tipos de solicitudes y almacenar los valores
    for solicitud in solicitudes:
        tipo_solicitudes.append(solicitud[0])

    # Consultar si existe una sesión de usuario activa
    if request.session.get('id_usuario'):
        # Obtener el ID del usuario que ha iniciado sesión
        id_usuario_autenticado = request.session['id_usuario']

        # Consultar solicitudes del usuario enviadas
        solicitudes_usuario_enviadas = Solicitud.objects.filter(solicitante=id_usuario_autenticado)

        # Conjuntos para almacenar los tipos de solicitudes que el usario ha enviado
        solicitudes_enviadas_pendientes = set()
        solicitudes_enviadas_aceptadas = set()
        solicitudes_enviadas_rechazadas = set()
        solicitudes_enviadas = set()

        # Lista de amigos
        lista_amigos = []

        # Iterar sobre las solicitudes enviadas del usuario
        for solicitud_enviada in solicitudes_usuario_enviadas:
            if solicitud_enviada.estado_solicitud == 'pendiente':
                solicitudes_enviadas_pendientes.add(solicitud_enviada.solicitado.id)
            elif solicitud_enviada.estado_solicitud == 'aceptada':
                solicitudes_enviadas_aceptadas.add(solicitud_enviada.solicitado.id)
                lista_amigos.append(solicitud_enviada.solicitado)
            elif solicitud_enviada.estado_solicitud == 'rechazada':
                solicitudes_enviadas_rechazadas.add(solicitud_enviada.solicitado.id)
            solicitudes_enviadas.add(solicitud_enviada.solicitado.id)

        # Consultar solicitudes del usuario recibidas
        solicitudes_usuario_recibidas = Solicitud.objects.filter(solicitado=id_usuario_autenticado)

        # Conjuntos para almacenar los tipos de solicitudes que el usario ha recibido
        solicitudes_recibidas_pendientes = set()
        solicitudes_recibidas_aceptadas = set()
        solicitudes_recibidas_rechazadas = set()
        solicitudes_recibidas = set()

        # Iterar sobre las solicitudes recibidas del usuario
        for solicitud_recibida in solicitudes_usuario_recibidas:
            if solicitud_recibida.estado_solicitud == 'pendiente':
                solicitudes_recibidas_pendientes.add(solicitud_recibida.solicitante.id)
            elif solicitud_recibida.estado_solicitud == 'aceptada':
                solicitudes_recibidas_aceptadas.add(solicitud_recibida.solicitante.id)
                lista_amigos.append(solicitud_recibida.solicitante)
            elif solicitud_recibida.estado_solicitud == 'rechazada':
                solicitudes_recibidas_rechazadas.add(solicitud_recibida.solicitante.id)
            solicitudes_recibidas.add(solicitud_recibida.solicitante.id)

        # Si existe una sesión de usuario activa, verificar si el ID del usuario que ha iniciado sesión es el mismo ID del usuario que hemos pasado a través de la URL y manejar el caso si es verdadero
        if id_usuario_autenticado == usuario.id:
            # Consultar los posibles errores
            error_campos_vacios = request.session.pop('error_campos_vacios', None)
            error_contenido = request.session.pop('error_contenido', None)

            # Consultar en la db el usuario por el ID de la sesión y el nombre del usuario
            usuario = Usuario.objects.get(id=request.session['id_usuario'], nombre_usuario=nombre_usuario)

            # Consultar las publicaciones propias del usuario. Order_by junto con el prefijo '-' indicar que se está ordenando los resultados de en orden descedente(de arriba hacia abajo), es decir del mas reciente al más antiguo   
            publicaciones = Publicacion.objects.filter(autor=usuario).order_by('-fecha_creacion')

            # Crear conjuntos para almacenar únicamente las publicaciones propias a las que el usuario ha reaccionado con like y dislike
            reacciones_like = set()
            reacciones_dislike = set()

            # Consultar las publicaciones que tienen reaccion
            for publicacion in publicaciones:
                reacciones_usuario = Reaccion.objects.filter(autor=usuario, publicacion_id=publicacion.id)
                # Almacenar las publicaciones reaccionadas por el usuario
                if reacciones_usuario:
                    # Consultar las publicaciones por el tipo de reacción y almacenar
                    for reaccion_usuario in reacciones_usuario:
                        if reaccion_usuario.tipo_reaccion == 'like':
                            reacciones_like.add(publicacion.id)
                        elif reaccion_usuario.tipo_reaccion == 'dislike':
                            reacciones_dislike.add(publicacion.id)

            usuario_autenticado = Usuario.objects.get(id=request.session['id_usuario'])
            return render(request, 'perfil.html', {
                'usuario': usuario,
                'publicaciones': publicaciones,
                'reacciones': reacciones,
                'reacciones_like': reacciones_like,
                'reacciones_dislike': reacciones_dislike,
                'usuario_autenticado': usuario_autenticado,
                'error_campos_vacios': error_campos_vacios,
                'error_contenido': error_contenido,
                'tipo_solicitudes': tipo_solicitudes,
                'solicitudes_usuario_recibidas': solicitudes_usuario_recibidas,
                'solicitudes_usuario_enviadas': solicitudes_usuario_enviadas,
                'solicitudes_enviadas_pendientes': solicitudes_enviadas_pendientes,
                'solicitudes_recibidas_aceptadas': solicitudes_recibidas_aceptadas,
                'solicitudes_recibidas_pendientes': solicitudes_recibidas_pendientes,
                'solicitudes_recibidas_rechazadas': solicitudes_recibidas_rechazadas,
                'lista_amigos': lista_amigos,
            })
        # Manejar el caso donde el usuario que ha iniciado sesión visite un perfil diferente al propio 
        else:
            usuario_autenticado = Usuario.objects.get(id=request.session['id_usuario'])

            reacciones_like = set()
            reacciones_dislike = set()

            # Consultar las reacciones que el usuario que ha iniciado sesión ha hecho a las publicaciones del perfil que está visitando
            for publicacion in publicaciones:
                reacciones_usuario = Reaccion.objects.filter(autor=usuario_autenticado, 
                                                            publicacion_id=publicacion.id)
                # Almacenar las publicaciones reaccionadas por el usuario
                if reacciones_usuario:
                    # Consultar las publicaciones por el tipo de reacción y almacenar
                    for reaccion_usuario in reacciones_usuario:
                        if reaccion_usuario.tipo_reaccion == 'like':
                            reacciones_like.add(publicacion.id)
                        elif reaccion_usuario.tipo_reaccion == 'dislike':
                            reacciones_dislike.add(publicacion.id)

            return render(request, 'perfil.html', {
                'usuario': usuario,
                'publicaciones': publicaciones,
                'reacciones': reacciones,
                'reacciones_like': reacciones_like,
                'reacciones_dislike': reacciones_dislike,
                'usuario_autenticado': usuario_autenticado,
                'tipo_solicitudes': tipo_solicitudes,
                'solicitudes_enviadas_aceptadas': solicitudes_enviadas_aceptadas,
                'solicitudes_enviadas_pendientes': solicitudes_enviadas_pendientes,
                'solicitudes_enviadas_rechazadas': solicitudes_enviadas_rechazadas,
                'solicitudes_recibidas_aceptadas': solicitudes_recibidas_aceptadas,
                'solicitudes_recibidas_pendientes': solicitudes_recibidas_pendientes,
                'solicitudes_recibidas_rechazadas': solicitudes_recibidas_rechazadas,
                'solicitudes_enviadas': solicitudes_enviadas,
                'solicitudes_recibidas': solicitudes_recibidas,
            })
    
    else:
        return render(request, 'perfil.html', {
                'usuario': usuario,
                'publicaciones': publicaciones,
                'reacciones': reacciones,
            })


def actualizar_perfil(request):
    if request.method == 'POST':
        # Obtener el ID del usuario desde el formulario 
        id_usuario = request.POST.get('id_usuario')

        # Buscar el usuario en la db por medio del ID
        usuario = get_object_or_404(Usuario, id=id_usuario)

        # Obtener los datos de los campos del formulario
        nombre_usuario = request.POST.get('nombre_usuario')
        correo_electronico = request.POST.get('correo_electronico')

        # Comprobar si los campos están vacios
        if not nombre_usuario or not correo_electronico:
            # Crear una variable para almacenar un error en la sesión en caso de que los campos de texto estén vacios
            error_campos_vacios = 'Los campos no pueden estar vacios.'
            request.session['error_campos_vacios'] = error_campos_vacios
            return redirect(reverse('perfil', args=[usuario.nombre_usuario]))
        
        # Acutualizar los datos en caso de que el formulario sea correcto
        usuario.nombre_usuario = nombre_usuario
        usuario.correo_electronico = correo_electronico
        usuario.save()

        return redirect(reverse('perfil', args=[usuario.nombre_usuario]))


def nueva_publicacion(request):
    if request.method == 'POST':
        # Obtener el ID del usuario desde el formulario de envío
        id_usuario = request.POST.get('id_usuario')

        # Obtener los datos de la nueva publicación
        contenido_publicacion = request.POST.get('contenido_publicacion')
        img_publicacion = request.FILES.get('img_publicacion') # FILES, para obtener la imagen correctamente en lugar de POST

        # Obtener el usuario desde la db a través del ID
        usuario = get_object_or_404(Usuario, id=id_usuario)

        # Verificar al menos que exista contenido en la publicación
        if not contenido_publicacion and not img_publicacion:
            error_contenido = 'La publicación debe contener al menos un contenido.'
            request.session['error_contenido'] = error_contenido
            return redirect(reverse('perfil', args=[usuario.nombre_usuario]))

        # Crear la nueva publicación
        Publicacion.objects.create(autor=usuario, contenido=contenido_publicacion, imagen=img_publicacion)

        return redirect(reverse('perfil', args=[usuario.nombre_usuario]))
    

def eliminar_publicacion(request, id_publicacion):
    # Obtener de la db la publicación a través del ID
    publicacion = get_object_or_404(Publicacion, id=id_publicacion)

    # Obtener el usuario a partir de la publicación
    id_usuario = publicacion.autor_id
    usuario = get_object_or_404(Usuario, id=id_usuario)

    # Eliminar publicación
    publicacion.delete()

    return redirect(reverse('perfil', args=[usuario.nombre_usuario]))


def actualizar_publicacion(request):
    if request.method == 'POST':
        # Obtener de la db la publicación a través del ID
        id_publicacion = request.POST.get('id_publicacion')
        publicacion = get_object_or_404(Publicacion, id=id_publicacion)

        # Obtener los datos de la publicación actualizada
        contenido_publicacion = request.POST.get('contenido_publicacion')
        img_publicacion = request.FILES.get('img_publicacion')

        # Obtener el usuario a partir de la publicación
        id_usuario = publicacion.autor_id
        usuario = get_object_or_404(Usuario, id=id_usuario)

        if img_publicacion or publicacion.imagen:
            # Actualizar la publicación con los nuevos datos
            publicacion.contenido = contenido_publicacion
            if img_publicacion:
                publicacion.imagen = img_publicacion
            publicacion.save()
        elif not contenido_publicacion and not img_publicacion:
            error_contenido = 'La publicación debe contener al menos un contenido.'
            request.session['error_contenido'] = error_contenido
            return redirect(reverse('perfil', args=[usuario.nombre_usuario])) 

        return redirect(reverse('perfil', args=[usuario.nombre_usuario]))
        

def reaccion_publicacion(request):
    # Obtener el ID del usuario desde la sesión
    id_usuario = request.session.get('id_usuario')

    # Verificar si existe una sesión de usuario activa
    if id_usuario:
        # Obtener los datos del usuario a partir de la sesión
        usuario = get_object_or_404(Usuario, id=id_usuario)

        if request.method == 'POST':
            # Obtener el ID de la publicación
            id_publicacion = request.POST.get('id_publicacion')

            # Obtener el objeto publicación en la base de datos a través del ID
            publicacion = get_object_or_404(Publicacion, id=id_publicacion)

            # Verificar si la solicitud proviene del perfil del usuario
            from_profile = request.POST.get('from_profile')

            # Verificar si existe una reacción
            reaccion_existe = Reaccion.objects.filter(autor=usuario, publicacion=publicacion).exists()
            if reaccion_existe:
                reaccion = Reaccion.objects.get(autor=usuario, publicacion=publicacion)
                if 'me_gusta' in request.POST:
                    tipo_reaccion = request.POST.get('me_gusta')
                    if reaccion.tipo_reaccion == tipo_reaccion:
                        reaccion.delete()
                    else:
                        reaccion.tipo_reaccion = tipo_reaccion
                        reaccion.save()
                elif 'no_me_gusta' in request.POST:
                    tipo_reaccion = request.POST.get('no_me_gusta')
                    if reaccion.tipo_reaccion == tipo_reaccion:
                        reaccion.delete()
                    else:
                        reaccion.tipo_reaccion = tipo_reaccion
                        reaccion.save()
                    
            # En caso de que no exista una reacción
            else:
                # Verificar el tipo de reacción
                if 'me_gusta' in request.POST:
                    tipo_reaccion = request.POST.get('me_gusta')      
                elif 'no_me_gusta' in request.POST:
                    tipo_reaccion = request.POST.get('no_me_gusta')

                # Crear una nueva reacción  
                reaccion = Reaccion.objects.create(autor=usuario, 
                                                    publicacion=publicacion, 
                                                    tipo_reaccion=tipo_reaccion) 
                
            # Redirigir según la solicitud provenga del perfil del usuario o de la página principal
            if from_profile:
                # Si el usuario reacciona a una publicación propia se redirige a su perfil de usuario, de lo contrario se redirige al perfil del autor de la publicación
                if usuario == publicacion.autor:
                    return redirect(reverse('perfil', args=[usuario.nombre_usuario]))
                else:
                    return redirect(reverse('perfil', args=[publicacion.autor.nombre_usuario]))
            else:
                return redirect('/')
                
    
    else:
        return render(request, 'login.html')


def nuevo_comentario(request):
    if request.method == 'POST':
        # Obtener el ID de la publicaición y buscar la publicación el la db
        id_publicacion = request.POST.get('id_publicacion')
        publicacion = get_object_or_404(Publicacion, id=id_publicacion)

        # Obtener el usuario a través de sesión de usuario
        usuario = get_object_or_404(Usuario, id=request.session['id_usuario'])

        # Obtener los datos del nuevo comentario
        contenido = request.POST.get('comentario')

        # Verificar que exista contenido en el formulario de envío
        if not contenido:
            return redirect('/')
        
        # Crear el nuevo comentario
        nuevo_comentario = Comentario.objects.create(autor=usuario, 
                                                    publicacion=publicacion, contenido=contenido)
        nuevo_comentario.save()

        return redirect('/')
    

def agregar_amigo(request):
    if request.method == 'POST':
        # Obtener el ID del usuario al que se va a enviar la solicitud de amistad
        id_usuario_solicitado = request.POST.get('id_usuario')
        usuario_solicitado = get_object_or_404(Usuario, id=id_usuario_solicitado)

        # Obtener el ID del usuario que envia la solicitud de amistad a través de la sesión de usuario
        usuario_solicitante = get_object_or_404(Usuario, id=request.session['id_usuario'])
        
        # Evitar enviar solicitudes a sí mismo
        if usuario_solicitado != usuario_solicitante:
            # Verificar si la etiqueta que contiene el valor de la solicitud se está pasando desde el formulario
            if 'enviar_solicitud' in request.POST:
                tipo_solicitud = request.POST.get('enviar_solicitud')
                # Crear la nueva solicitud
                Solicitud.objects.create(solicitante=usuario_solicitante,
                                    solicitado=usuario_solicitado, estado_solicitud=tipo_solicitud)
                
            return redirect(reverse('perfil', args=[usuario_solicitado.nombre_usuario]))
        

def aceptar_amigo(request):
    if request.method == 'POST':
        # Obtener el ID del usuario al que se va a aceptar la solicitud de amistad
        id_usuario_solicitante = request.POST.get('id_usuario')
        usuario_solicitante = get_object_or_404(Usuario, id=id_usuario_solicitante)

        # Obtener el ID del usuario que acepta la solicitud de amistad
        usuario_solicitado = get_object_or_404(Usuario, id=request.session['id_usuario'])

        # Verificar si existe una solicitud de amistad
        solicitud_existe = Solicitud.objects.filter(solicitante=usuario_solicitante, solicitado=usuario_solicitado).exists()
        if solicitud_existe:
            # Obtener la solicitud de amistad existente
            solicitud = Solicitud.objects.get(solicitante=usuario_solicitante, solicitado=usuario_solicitado)
            if 'aceptar_solicitud' in request.POST:
                tipo_solicitud = request.POST.get('aceptar_solicitud')
                # Cambiar el estado de la solicitud existente a 'aceptada'
                solicitud.estado_solicitud = tipo_solicitud
                solicitud.save()
        
                return redirect(reverse('perfil', args=[usuario_solicitado.nombre_usuario]))
            
            if 'rechazar_solicitud' in request.POST:
                tipo_solicitud = request.POST.get('rechazar_solicitud')
                solicitud.estado_solicitud = tipo_solicitud
                solicitud.save()

                return redirect(reverse('perfil', args=[usuario_solicitado.nombre_usuario]))
            

def eliminar_amigo(request):
    if request.method == 'POST':
        # Obtener el ID del usuario al que se va eliminar de la lista de amigos
        id_usuario_solicitante = request.POST.get('id_usuario')
        usuario_solicitante = get_object_or_404(Usuario, id=id_usuario_solicitante)

        # Obtener el ID del usuario que elimina
        usuario_solicitado = get_object_or_404(Usuario, id=request.session['id_usuario'])

        # Verificar si existe una solicitud de amistad
        solicitud_existe = Solicitud.objects.filter(solicitante=usuario_solicitante, solicitado=usuario_solicitado).exists()
        if solicitud_existe:
            solicitud = Solicitud.objects.get(solicitante=usuario_solicitante, solicitado=usuario_solicitado)
            # Eliminar la solicitud
            solicitud.delete()
            return redirect(reverse('perfil', args=[usuario_solicitado.nombre_usuario]))
        else:
            HttpResponse('El usuario no se encuentra en tu lista de amigos')
    