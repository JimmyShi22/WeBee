def gen_url(host, port):
    return 'http://' + host + ':' + str(port) + '/'

host = '127.0.0.1'
port = 18089
url =gen_url(host, port)

peers_host = ['127.0.0.1']
peers_port = [18088, 18089, 18090]

peers_url = []
for ph in peers_host:
    for pp in peers_port:
        peers_url.append(gen_url(ph, pp))


time_before_start = float(1000) / 1000 #ms
heart_beat_expires = 1000 #ms
uniform_expires = 8000 #ms

