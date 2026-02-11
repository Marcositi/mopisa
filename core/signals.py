from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pedido  # Asegúrate de que el nombre de tu modelo sea Pedido
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@receiver(post_save, sender=Pedido)
def notificar_admin_nuevo_pedido(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        
        # Obtenemos el nombre del cliente correctamente
        # Si 'cliente' tiene una relación con User llamada 'usuario':
        nombre_cliente = instance.cliente.usuario.username 
        # Si prefieres el nombre real y existe el campo:
        # nombre_cliente = instance.cliente.nombre 

        async_to_sync(channel_layer.group_send)(
            "notificaciones_admin",
            {
                "type": "enviar_alerta",
                "mensaje": f"Pedido #{instance.id} recibido",
                "total": str(instance.total),
                "cliente": nombre_cliente # Corregido aquí
            }
        )