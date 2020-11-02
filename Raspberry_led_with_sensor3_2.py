#-*-coding:utf-8-*-

# 필요한 라이브러리를 불러옵니다. 
import RPi.GPIO as GPIO
import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw


#센서에 연결한 Trig와 Echo 핀의 핀 번호 설정 
TRIG = 23 #board 16
ECHO = 24 #18

#led
LedBlue = 17 #11
LedYellow = 18 #12

#oled
RST = 25  #22 GPIO
DC = 22  #15
SPI_PORT = 0
SPI_DEVICE = 0

#btn
button_pin = 15

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#Trig와 Echo 핀의 출력/입력 설정 
GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)

GPIO.setup(LedBlue, GPIO.OUT)  
GPIO.setup(LedYellow, GPIO.OUT)

GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 

# 128x64 display with hardware SPI:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST, dc=DC, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=8000000))

disp.begin()
disp.clear()
disp.display()

width = disp.width
height = disp.height

image = Image.new('1', (width, height))
#font_retro = ImageFont.truetype('retro_computer_personal_use.ttf', 15) #폰트파일 필요
font_web = ImageFont.truetype('000webfont.ttf', 20) 
font = ImageFont.load_default()
draw = ImageDraw.Draw(image)

#중지, 재개를 위한 변수
order = True

def btn_call(channel):
    global order

    order = not order
    disp.clear()
    
    if order != True:
        draw.rectangle((0,0,width-1, height-1),outline=1, fill=0)
        draw.text((45,15), 'Pause', font= font_web, fill=255)
        disp.image(image)
        disp.display()

    time.sleep(0.5)
 

GPIO.add_event_detect(button_pin,GPIO.RISING,callback=btn_call)


def blinkLED(pin, delay):
    GPIO.output(pin,1)  
    time.sleep(delay)   
    GPIO.output(pin,0) 
    time.sleep(delay)  

def run():
    if order == True:
        try:
            while True:      
                GPIO.output(TRIG, True)   # Triger 핀에  펄스신호를 만들기 위해 1 출력
                time.sleep(0.00001)       # 10µs 딜레이 
                GPIO.output(TRIG, False)
                
                while GPIO.input(ECHO)==0:
                    start = time.time()	 # Echo 핀 상승 시간 
                while GPIO.input(ECHO)==1:
                    stop= time.time()	 # Echo 핀 하강 시간 
                    
                check_time = stop - start
                distance = check_time * 34300 / 2

                time.sleep(0.1)	# 0.1초 간격으로 센서 측정 

                distance = int(distance)
                text = 'Distance : %d cm' % distance

                draw.rectangle((0,0,width-1, height-1),outline=1, fill=0)
                draw.text((15,25), text, font= font, fill=255)

                disp.image(image)
                disp.display()
                time.sleep(0.03)

                delayTime= 0.8

                if distance >= 20:   
                    delayTime = 0.5
                    
                elif distance >= 15:
                    delayTime = 0.3

                elif distance >= 10:
                    delayTime = 0.1

                elif distance >= 5:
                    delayTime = 0.05
                    
                elif distance >0 and distance < 5:
                    GPIO.output(LedYellow,1)
                    continue

                GPIO.output(LedYellow,0)
                blinkLED(LedBlue, delayTime)

                if order != True:
                    GPIO.output(TRIG, False)
                    GPIO.output(LedYellow,0)
                    GPIO.output(LedBlue,0)
                    break


        except KeyboardInterrupt:
            print("Measurement stopped by User")
            disp.clear()
            GPIO.cleanup()



#Trig핀의 신호를 0으로 출력 
GPIO.output(TRIG, False)

#print("Waiting for sensor to settle")
waitingText = "I'm working"
waitingText2 = "for you!"
draw.rectangle((0,0,width-1, height-1),outline=1, fill=0)
draw.text((25,15), waitingText, font= font_web, fill=255)
draw.text((35,25), waitingText2, font= font_web, fill=255)

disp.image(image)
disp.display()
time.sleep(2)

disp.clear()

while True:
    run()
