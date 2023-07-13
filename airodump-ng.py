import subprocess
import sys
import asyncio
import os
import string

def getInterfacec():
    command = "iwconfig"
    output = subprocess.getoutput(command)
    lines = output.split("\n")
    wireless_interfaces = []

    for line in lines:
        if "IEEE" in line:
            wireless_interfaces.append(line.split()[0])
    idx = 1
    for interface in wireless_interfaces:
        print(str(idx) + " " + interface)
        idx += 1
    return wireless_interfaces

interfacec = getInterfacec()

number_adapter = 0
idx_adapter = 0

while number_adapter < 1 or idx_adapter >= len(interfacec):
    try:
        number_adapter = int(input("виберіть мережевий адаптер: "))
        idx_adapter = number_adapter - 1
    except ValueError:
        idx_adapter = 0

iface = interfacec[idx_adapter]

async def read_output(process):
    while True:
        output = await process.stdout.readline()
        if output == b'':
            break
        print(output.decode().strip())

async def run_airodump(interface):
    # Видаляємо попередній файл перед запуском airodump-ng
    if os.path.exists("output-01.csv"):
        os.remove("output-01.csv")
    if os.path.exists("output-01.ivs"):
        os.remove("output-01.ivs")

    command = f"sudo airodump-ng --output-format csv --write output -i {interface}"
    process = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE)

    # Створюємо задачу для читання виводу команди
    read_task = asyncio.create_task(read_output(process))

    try:
        # Очікуємо натискання Ctrl+C
        await process.wait()
    except KeyboardInterrupt:
        # Обробка натискання Ctrl+C
        pass
    except asyncio.CancelledError:
        # Ігнорувати помилку при закритті програми
        pass

    # Закриваємо процес
    process.terminate()

    # Очікуємо завершення читання виводу
    await read_task

# Запускаємо airodump-ng і виводимо результати
try:
    asyncio.run(run_airodump(iface))
except KeyboardInterrupt:
    pass

def print_and_select_wifi_networks():
    # Відкриття файлу
    with open("output-01.csv", "r") as file:
        lines = file.readlines()
    filtered_lines = list(filter(lambda x: " 0. " in x, lines))
    filtered_lines = [x.strip() for x in filtered_lines]
    filtered_lines = [x[:-1] for x in filtered_lines]
    filtered_lines = [x[:17] +x[18:] for x in filtered_lines]
    sort_network_list=[]
    idx=1
    for line in filtered_lines:
        temp_array=line.split(" ")
        sort_network_list.append(f"{str(idx)}, {'невідома назва' if temp_array[-1] == ',' else temp_array[-1]}, {temp_array[0]}")
        idx+=1

    for line in sort_network_list:
        print(line)

    while True:
        print("виберіть мережу, можна вибрати всі ввівши all, або декілька через кому, чи через тире")
        select_network = input("виберіть мережу: ")
        if select_network == "all":
            return sort_network_list
        if select_network.isdigit() and 0 < int(select_network) <= len(sort_network_list):
            return [sort_network_list[int(select_network) - 1]]
        if "," in select_network:
            select_networks = [x.strip() for x in select_network.split(",") if x.strip() != ""]
            isValueTrue = True
            for line in select_networks:
                if not line.isdigit() or not (0 < int(line) <= len(sort_network_list)):
                    isValueTrue = False
                    break
            if isValueTrue:
                result = []
                for item in select_networks:
                    result.append(sort_network_list[int(item) - 1])
                return result
        if "-" in select_network:
            select_network = select_network.replace(" ", "")
            temp_array = select_network.split("-")
            if len(temp_array) == 2 and temp_array[0].isdigit() and temp_array[1].isdigit() and int(temp_array[0]) < int(temp_array[1]):
                if 0 < int(temp_array[0]) <= len(sort_network_list) and 0 < int(temp_array[1]) <= len(sort_network_list):
                    result = []
                    start_idx = int(temp_array[0]) - 1
                    end_idx = int(temp_array[1])
                    result.extend(sort_network_list[start_idx:end_idx])
                    return result

select_wifi_networks = print_and_select_wifi_networks()

for line in select_wifi_networks:
    print(line)

print("end")
