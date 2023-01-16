from multiprocessing.connection import Client

address = ('localhost', 6000)
conn = Client(address, authkey=b'eogn68rb8r69')
conn.send(input('t pa bo : '))
# can also send arbitrary objects:
# conn.send(['a', 2.5, None, int, sum])
conn.close()