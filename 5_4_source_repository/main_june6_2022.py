from machine import Pin, ADC, PWM
from time import sleep
#setup


mot1=PWM(Pin(15))
mot2=PWM(Pin(14))

potpinadc = ADC(Pin(26))
temp1=ADC(Pin(28))
temp2=ADC(Pin(27))
led=Pin(25, Pin.OUT)

mot1.freq(20_000)
mot2.freq(20_000)

mot1.duty_u16(0)
mot2.duty_u16(0)

oldpotval = 0
potval = 0


#end setup, begin input section

while True:
    potval=int(potpinadc.read_u16()/630) #input, convert potval to a value between about 0 and 100
    #begin output
    tempval1=temp1.read_u16()
    tempval2=temp2.read_u16()
    sleep(0.1)
    print("potval:",potval)
    print("temp1:",tempval1)
    print("temp2:",tempval2)
    #led.toggle()
    if abs(potval-oldpotval)>3: # this provides some stability, preventing the motors from changing speed when the pot value changes by small amounts randomly
        mot1.duty_u16(potval*630)
        oldpotval=potval
        mot1.freq(20_000)
        mot2.duty_u16(mot1.duty_u16())
        mot2.freq(20_000)
        if (potval>95): # this ensures you can get full power despite the hysterisys stuff above
            mot1.duty_u16(65535)
            mot1.freq(20_000)
            mot2.duty_u16(mot1.duty_u16())
            mot2.freq(20_000)
    
#no cleanup



