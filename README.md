# DeFire
 
This is a code for a turret that shoots water into fire using **computer vision**. The project used **Python**, a programming language for **Arduino**, the **ultralyrics** library for training and using a model based on the **YOLO** model, the **aiogram** library for the telegram bot and **sqlite3** for the database.

The turret consists of two servos, a cam, an Arduino Nano microcontroller, a water pump and other components. using serial, data on the angle of rotation of the servos and the start of the pump were transmitted between the laptop and the turret. The data was obtained after image processing through a computer vision model, by determining the location of the fire in the frame and the center of the image. When a fire was detected, the turret was given the command to turn towards it and shoot water if the fire hits the sight. Further, the captured images and videos were sent to certain users from the database to notify them of the potential danger

https://github.com/RandomnieBukvi/DeFire/assets/117274482/d27855ce-c093-46c0-90d8-2d27ab523115
