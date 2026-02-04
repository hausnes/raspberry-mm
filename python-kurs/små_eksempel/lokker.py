#import time

# while-løkker
repetisjon = int(input("Kva tal skal eg telle ned frå? "))

while repetisjon >= 0:
    print(repetisjon)
    repetisjon = repetisjon - 1
    #time.sleep(0.5)
    
# for-løkker
print("------------------------")
x = range(0,11,2)

for n in x:
    print(n)