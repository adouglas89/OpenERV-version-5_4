from machine import Pin, ADC, PWM
from time import sleep, sleep_ms
from random import randint
#setup
enable_pin_active_low=Pin(1, Pin.OUT)
enable_pin_active_low.off()
mot1=PWM(Pin(15))
mot2=PWM(Pin(14))
pwm = PWM(Pin(0))
potpinadc = ADC(Pin(26))
temp1=ADC(Pin(28))
temp2=ADC(Pin(27))
mot1.freq(20_000)
mot2.freq(20_000)

mot1.duty_u16(0)
mot2.duty_u16(0)
oldpotval = 0
potval = 0
led=Pin(25, Pin.OUT)
esc = PWM(Pin(0))
led= Pin(25, Pin.OUT)
esc.freq(50) # 20 millisecond period

#stuff for auto fan speed compensation
temp_diff=0
old_temp_diff=0
max_random_deviation = 20
min_random_deviation = 2
deviation_gain = 25
setpoint = 1550 # it starts here but adjusts automatically, slowly

#begin esc arming sequence, it's not clear why this works, but it does


for x in range(0,20):
    pwm.freq(50)
    microseconds_out=((1/65_000)*1000)+1000
    pwm.duty_u16(int((microseconds_out/20_000)*65535))# input, process, output
    print(microseconds_out)
    sleep_ms(200)
    led.toggle()
    #no cleanup
print ("done, esc armed")
sleep(1)
for x in range(0,500,10):  # seems to be increasing speed for some reason, or decreasing it
    pwm.duty_u16(int(((1100+x)/20_000)*65535))
    sleep(0.004)
sleep(3)
pwm.duty_u16(int((1350/20_000)*65535)) #set final running speed of gimbal motor

def read_temp_diff():
    global tempval1
    global tempval2
    tempval1=temp1.read_u16()
    tempval2=temp2.read_u16()
    tempval_diff=(abs(tempval1-tempval2))
    return tempval_diff
        
while True:
    # check if the pot has been changed, and if so apply the changes to the motors
    potval=int(potpinadc.read_u16()/630) #input, convert potval to a value between about 0 and 100
    if abs(potval-oldpotval)>3:
        new_pwm=potval*630
        old_pwm=mot1.duty_u16()
        pwm_change=new_pwm-old_pwm
        mot1.duty_u16(new_pwm)
        mot1.freq(20_000)
        new_mot2=mot2.duty_u16()+pwm_change
        if new_mot2>65535:# limit the range of the motor 2 pwm input so it doesn't get too high or low and throw an error
            new_mot2=65535
        if new_mot2<0:
            new_mot2=0
        mot2.duty_u16(new_mot2) #adjust motor 2 speed, but keep the difference in pwm values the same as it was if you can
        mot2.freq(20_000)
        oldpotval=potval
    #measure the temp diff a bunch of times and calculate the average
    temp_diff_accum=0
    x=20
    for i in range(0,x):
        temp_diff_accum=temp_diff_accum+read_temp_diff()
        sleep(0.02)
    temp_diff=temp_diff_accum/x
    
    #perturb
    old_mot2=mot2.duty_u16() #save old value
    random_int=randint(-max_random_deviation,max_random_deviation)
    x=random_int*deviation_gain #calculate some change to make, from random numbers, gain and difference between setpoint and measured value
    new_mot2=int(mot2.duty_u16()+x) #has to be an integer to input as a duty cycle, gain may be a floating point so it was converted
    if new_mot2>65534:# limit the range of the motor 2 pwm input so it doesn't get too high or low and throw an error
        new_mot2=65534
    if new_mot2<0:
        new_mot2=0
    mot2.duty_u16(new_mot2) #put in test value
    print("calculated test value for mot2 pwm and applied: ", mot2.duty_u16(), "deviation: ", x," temp_diff:",temp_diff)
    
    #observe_save()
    old_temp_diff=read_temp_diff()
    sleep(3)# 
    new_temp_diff=read_temp_diff()
    if (new_temp_diff-old_temp_diff)>100: # if things improved/temp diff increased much over the last 3 seconds, save the new pwm value
        x=1
        print("significant improvement made, keeping change")
    else:
        #if not, go back to the old
        print("no significant improvement from that test, putting it back")
        mot2.duty_u16(old_mot2)
        sleep(10)# a washout period to reduce the tendency to overshoot again.  little point in this, 
    #adjust setpoint
    setpoint=setpoint-30 #slowly lower setpoint on each cycle, this no longer has any purpose the setpoint is not used 
    if temp_diff>setpoint:#up the setpoint to the temp diff if it's higher than the current setpoint.
        setpoint=temp_diff
        
    #output more diagnostics
    print("potval:",potval)
    print("temp1:",tempval1)
    print("temp2:",tempval2)
  
    print("mot1_duty:", mot1.duty_u16(), " mot2_duty:", mot2.duty_u16())
    print("temp_diff:", temp_diff, "setpoint: ", setpoint)
    led.toggle()
    
    
#no cleanup




