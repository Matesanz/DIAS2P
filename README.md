# Smart Campus UMA

El plan propio Smart-Campus I es un proyecto impulsado por la **Universidad de Málaga**  
en el que se desarrollan un conjunto de trabajos enfocados a potenciar las Smart-Cities. Dos de esos trabajos
asignados al mismo equipo de investigación son:

- DIAS2P o *Dispositivo Inteligente de Asistencia en Seguridad para Paso de Peatones*.
- StreetQR: Dispositivo de control de movimiento de viandantes con emisión de información.

### ¿En qué consiste el DIAS2P?

En este repositorio se presenta el primero de ellos. Un Dispositivo de seguridad enfocado a cruces de peatones sin señalización.
Segun la DGT la mayor parte de los accidentes se producen en pasos a nivel no señalizados, por lo que, con el objetivo de reducir el número de víctimas
se plantea un prototipo que busca reducir la siniestralidad.

![DIAS2P_1.PNG](images/Design/DIAS2P_1.PNG = 250x250) ![DIAS2P_2.PNG](images/Design/DIAS2P_2.PNG = 250x250)

A través de reconocimiento de imágenes con Redes Neuronales se detecta la presencia de vehículos y peatones de manera que ante la posibilidad de
que ambos se encuentren en el paso de cebra se activa un sistema de luces y alarmas que alertan de este hecho. Para ello se ha desarrollado un algoritmo de
tracking basado en superficie que monitorea la posición de cada objeto dentro de la imagen.
