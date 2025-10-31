# Configuração do Gunicorn para produção
import os
import multiprocessing

# Configurações básicas
bind = "0.0.0.0:10000"
workers = min(2, multiprocessing.cpu_count())  # Limitado para evitar uso excessivo de memória
worker_class = "sync"
worker_connections = 100

# Configurações de timeout
timeout = 180  # 3 minutos para requisições longas da OpenAI
keepalive = 5
max_requests = 500  # Reiniciar worker após 500 requests para liberar memória
max_requests_jitter = 50

# Configurações de memória
worker_tmp_dir = "/dev/shm"  # Usar memória compartilhada se disponível
preload_app = True  # Pré-carregar app para economizar memória

# Logs
accesslog = "-"  # Stdout
errorlog = "-"   # Stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configurações de processo
daemon = False
pidfile = None
user = None
group = None
tmp_upload_dir = None

# Configurações de graceful restart
graceful_timeout = 120
max_worker_memory = 256 * 1024 * 1024  # 256MB por worker

print("🚀 Configuração do Gunicorn carregada:")
print(f"   Workers: {workers}")
print(f"   Timeout: {timeout}s")
print(f"   Max requests per worker: {max_requests}")
print(f"   Bind: {bind}")