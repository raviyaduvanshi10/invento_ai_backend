from datetime import datetime

# datetime object containing current date and time
now = datetime.now()
 
print("now =", now)

# dd/mm/YY H:M:S
dt_string = now.strftime("%Y/%m/%d %H:%M:%S")
print("date and time =", dt_string)
date = now.strftime("%Y/%m/%d")
time = now.strftime("%H:%M")
print(date)
print(time)

a = 700032
b = "|| Doc No #"+str(a)
print(b)
print(a)