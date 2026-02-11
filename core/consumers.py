import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificacionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Verificamos si el usuario es staff (admin o vendedor)
        if self.scope["user"].is_authenticated and self.scope["user"].is_staff:
            self.room_group_name = "notificaciones_admin"

            # Unirse al grupo de notificaciones
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            # Si no es staff, rechazamos la conexión al socket
            await self.close()

    async def disconnect(self, close_code):
        # Salir del grupo al desconectarse
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Este método se activa cuando el Signal envía un mensaje de tipo "enviar_alerta"
    async def enviar_alerta(self, event):
        mensaje = event['mensaje']
        total = event['total']
        cliente = event['cliente']

        # Enviar la información al frontend vía WebSocket
        await self.send(text_data=json.dumps({
            'titulo': '¡Nuevo Pedido!',
            'mensaje': mensaje,
            'total': total,
            'cliente': cliente
        }))