## Uborzbot

### El bot permite:
* /megacall para nombrar a todos los miembros de un canal
* /roll y /flip para funciones random
* crear calls con /create <nombre_call> <descripcion>
* utilizar comandos /call <nombre_call> para enviar un mensaje con mentions (x.ej: @pepito) al grupo en que se encuentra. La finalidad es que los usuarios mencionados reciban una notificación aunque tengan el grupo silenciado.
* los usuarios pueden unirse o salirse de las menciones usando, por ejemplo: /join <nombre_call> y /leave <nombre_call>. Tambien los puede insertar cualquier admin del canal o el propio creador del grupo. Funciona incluso con usuarios que NO tienen activo un @alias para las menciones.
* mas cosas

### Running at
https://t.me/uborzz_bot

### Advanced options
Se ha añadido un segundo bot, como usuario de telegram y no como cuenta de bot, lo que permite el envío de mensajes privados, temporizar mensajes privados, o llamadas perdidas a usuarios que no han iniciado una conversación con el bot o no están entre sus grupos (no son peers), en broadcast, es decir, a múltiples usuarios a la vez. Estas funcionalidades están limitadas por whitelist por el administrador del bot, ya que la cuenta de usuario va vinculada a un número de teléfono y no a un token.

## Estado
Portado totalmente de python-telegram-bot a pyrogram. En lugar de ser cliente de una api de telegram, ahora el bot es un propio cliente de telegram.
Utilizando un background scheduler para trastear con tareas temporizadas.
