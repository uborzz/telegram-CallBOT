## Uborzbot

El bot en principio permite utilizar los comandos /cs y /hots para enviar un mensaje con mentions (x.ej: @pepito) al grupo en que se encuentra. La finalidad es que los usuarios mencionados reciban una notificación aunque tengan el grupo silenciado. 

El bot permite a los usuarios unirse o salirse de las menciones usando, por ejemplo: /joincs y /leavecs. Funciona incluso con usuarios que NO tienen activo un @alias para las menciones.

Se utiliza Mongo para guardar los grupos de usuarios que quieren ser mencionados. Las colecciones creadas en la base de datos van referidas al grupo de telegram en el que reside el bot, y su creación es automática cuando se une algún usuario.

## To-do

Actualmente solo hay 2 "grupos" a los que los usuarios se pueden unir, ya predefinidos. Se pretenden mejorar los siguientes puntos:
* Permitir creación de grupos con mensajes y tags customizados por parte de los usuarios de un canal.
* Eliminar datos referentes a un canal al expulsar al bot de dicho canal.
* Añadir mensajes con temporización.
* ...

## Instalación

Quieres instalar tu propio bot? Se necesitan las librerías requests, pymongo y python-telegram-bot, así como una instancia de mongo corriendo.
