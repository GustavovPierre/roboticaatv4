#! /usr/bin/env python
# -- coding:utf-8 --

author = ["Rachel P. B. Moraes", "Igor Montagner", "Fabio Miranda"]


import rospy
import numpy as np
import tf
import math
import cv2
import time
from geometry_msgs.msg import Twist, Vector3, Pose
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge, CvBridgeError
import cormodule
from sensor_msgs.msg import LaserScan

	


bridge = CvBridge()

cv_image = None
media = []
centro = []
atraso = 1.5E9 # 1 segundo e meio. Em nanossegundos
dist = None

area = 0.0 # Variavel com a area do maior contorno

# Só usar se os relógios ROS da Raspberry e do Linux desktop estiverem sincronizados. 
# Descarta imagens que chegam atrasadas demais
check_delay = False 

# A função a seguir é chamada sempre que chega um novo frame
def roda_todo_frame(imagem):
	print("frame")
	global cv_image
	global media
	global centro
	global maior_area

	now = rospy.get_rostime()
	imgtime = imagem.header.stamp
	lag = now-imgtime # calcula o lag
	delay = lag.nsecs
	print("delay ", "{:.3f}".format(delay/1.0E9))
	if delay > atraso and check_delay==True:
		print("Descartando por causa do delay do frame:", delay)
		return 
	try:
		antes = time.clock()
		cv_image = bridge.compressed_imgmsg_to_cv2(imagem, "bgr8")
		# cv_image = cv2.flip(cv_image, -1)
		media, centro, maior_area =  cormodule.identifica_cor(cv_image)
		depois = time.clock()
		cv2.imshow("Camera", cv_image)
	except CvBridgeError as e:
		print('ex', e)

def scaneou(dado):
	global dist
	dist=dado.ranges[0]
	print(dist)



	
if __name__=="__main__":
	rospy.init_node("cor")

	# topico_imagem = "/kamera"
	topico_imagem = "/camera/rgb/image_raw/compressed"
 
	recebe_scan = rospy.Subscriber("/scan", LaserScan, scaneou)
	
	recebedor = rospy.Subscriber(topico_imagem, CompressedImage, roda_todo_frame, queue_size=4, buff_size = 2**24)
	print("Usando ", topico_imagem)

	velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 1)
	
	try:

		while not rospy.is_shutdown():
			
			if len(media) != 0 and len(centro) != 0 and maior_area>300:
				print("Média dos vermelhos: {0}, {1}".format(media[0], media[1]))
				print("Centro dos vermelhos: {0}, {1}".format(centro[0], centro[1]))			
				
										
				
				if dist > 0.5:
					
					if (media[0] > centro[0]):
						vel = Twist(Vector3(0.1,0,0), Vector3(0,0,-0.1))
										
					if (media[0] < centro[0]):
						vel = Twist(Vector3(0.1,0,0), Vector3(0,0,0.1))
					

				else:
				
					vel = Twist(Vector3(0,0,0), Vector3(0,0,0))
			



			else:
				vel = Twist(Vector3(0,0,0), Vector3(0,0,0.5))

			velocidade_saida.publish(vel)
			rospy.sleep(0.1)
			
			
	except rospy.ROSInterruptException:
	    print("Ocorreu uma exceção com o rospy")