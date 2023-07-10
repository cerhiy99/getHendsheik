import subprocess

def getInterfacec():
    command = "iwconfig"
    output = subprocess.getoutput(command)
    lines = output.split("\n")
    wireless_interfaces = []

    for line in lines:
        if "IEEE" in line:
            wireless_interfaces.append(line.split()[0])
    return wireless_interfaces

print("виберіть мережевий адаптер")
interfacec=getInterfacec()
for interface in interfacec:
    idx=1
    print(idx + interface)
    idx+=1
