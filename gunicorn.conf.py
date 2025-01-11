workers = 4
bind = "0.0.0.0:10000"
timeout = 120
# Longer timeout for image processing and speech recognition
worker_class = 'sync'
max_requests = 1000
max_requests_jitter = 50