from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required



urlpatterns = [
    path('jet/', include('jet.urls', 'jet')),  # Django JET URLS
    path('jet/dashboard/', include('jet.dashboard.urls',
                                   'jet-dashboard')),  # Django JET dashboard URLS
    path('admin/', admin.site.urls),
<<<<<<< HEAD
    path('', login_required(Inicio.as_view()), name='index'),
    path('accounts/register/', registroUsuario, name='register'),
    path('accounts/login/', Login.as_view(), name='login'),
    path('logout', login_required(logoutUsuario), name='logout'),
    path('perfil_agente', login_required(update_profile), name='perfil_agente'),
    path('confeccion_comisión', login_required(
        confeccionComision), name='confeccion_comisión'),
    path('confeccion_solicitud_comisión', login_required(
        confeccionSolicitudComision), name='confeccion_solicitud_comisión'),
    path('ajax/validate_username/', validar_username, name='validate_username'),
    path('ajax/validate_afiliado/', validar_afiliado, name='validate_afiliado'),
    path('ajax/validate_dni/', validar_dni, name='validate_dni'),
=======
    path('',include(('usuarios.urls','usuarios'), namespace='usuarios')),
>>>>>>> b9829ef364a6b1d17dfa7c7e847f6d29d30a5ded
]
