import multiprocessing

# 服务器绑定
bind = "0.0.0.0:8000"

# Worker设置
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000

# 超时设置
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100

# 日志设置
loglevel = "info"
accesslog = "access.log"
errorlog = "error.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程设置
preload_app = True
daemon = False

# 安全设置
user = None
group = None
tmp_upload_dir = None

# 性能调优
worker_tmp_dir = "/dev/shm"