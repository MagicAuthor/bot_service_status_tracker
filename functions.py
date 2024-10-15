import subprocess

# Функция для получения статуса службы
def get_service_status(service_name):
    result = subprocess.run(["systemctl", "is-active", service_name], stdout=subprocess.PIPE)
    return "active" if result.stdout.decode().strip() == "active" else "inactive"

# Функция для получения подробной информации о службе
def get_service_info(service_name):
    # Получение статуса службы через systemctl
    status_output = subprocess.run(['systemctl', 'status', service_name], capture_output=True, text=True)
    is_active = "active (running)" in status_output.stdout
    # Получаем PID службы
    pid_output = subprocess.run(['pidof', service_name], capture_output=True, text=True).stdout.strip()
    if pid_output:  # Если процесс существует
        # Получение информации о PID, памяти и CPU через ps
        ps_output = subprocess.run(['ps', '-p', pid_output, '-o', 'pid,%mem,%cpu,etime'], capture_output=True, text=True).stdout.strip().split('\n')[-1]
        pid, memory, cpu, uptime = ps_output.split()
    else:
        # Если процесс не существует (служба выключена)
        pid = "N/A"
        memory = "N/A"
        cpu = "N/A"
        uptime = "N/A"
    return {
        'is_active': is_active,
        'pid': pid,
        'memory': memory,
        'cpu': cpu,
        'uptime': uptime
    }

# Улучшенная функция для проверки существования службы, даже если она не активна
def is_service_exist(service_name: str) -> bool:
    try:
        # Используем systemctl для проверки, существует ли служба
        result = subprocess.run(
            ["systemctl", "status", service_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return "Loaded" in result.stdout.decode()  # Проверяем, загружена ли служба
    except subprocess.CalledProcessError:
        return False
