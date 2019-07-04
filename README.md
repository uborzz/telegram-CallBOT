## Uborzbot

El bot permite utilizar comandos /call <nombre_call> para enviar un mensaje con mentions (x.ej: @pepito) al grupo en que se encuentra. La finalidad es que los usuarios mencionados reciban una notificación aunque tengan el grupo silenciado. 

El bot permite a los usuarios unirse o salirse de las menciones usando, por ejemplo: /join <nombre_call> y /leave <nombre_call>. Funciona incluso con usuarios que NO tienen activo un @alias para las menciones.

Se utiliza Mongo para guardar los grupos de usuarios que quieren ser mencionados. Las colecciones creadas en la base de datos van referidas al grupo de telegram en el que reside el bot, y su creación es automática cuando se une algún usuario.

## Estado
Portando de python-telegram-bot a pyrogram. En lugar de ser cliente de una api de telegram, ahora el bot es un propio cliente de telegram, pero todas las funcionalidades no están operativas. Por el momento se han portado solamente la que utilizamos (megacall).

## To-do

~~Actualmente solo hay 2 "grupos" a los que los usuarios se pueden unir, ya predefinidos.~~ Se pretende mejorar los siguientes puntos:
* ~~Permitir creación de grupos con mensajes y tags customizados por parte de los usuarios de un canal.~~
* Eliminar datos referentes a un canal al expulsar al bot de dicho canal.
* Añadir mensajes con temporización.
* ...

## Instalación

Quieres instalar tu propio bot? Se necesitan las librerías requests, pymongo y python-telegram-bot, así como una instancia de mongo corriendo.
