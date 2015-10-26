
# dns.py is folk of minidns <https://code.google.com/p/minidns/>
# License: MIT LIcense <http://opensource.org/licenses/mit-license.php>

import sys
import socket
import fcntl
import struct
import re

# DNSQuery class from http://code.activestate.com/recipes/491264-mini-fake-dns-server/
class DNSQuery:
  def __init__(self, data):
    self.data=data
    self.domain=''

    tipo = (ord(data[2]) >> 3) & 15   # Opcode bits
    if tipo == 0:                     # Standard query
      ini=12
      lon=ord(data[ini])
      while lon != 0:
        self.domain+=data[ini+1:ini+lon+1]+'.'
        ini+=lon+1
        lon=ord(data[ini])

  def respuesta(self, ip):
    packet=''
    if self.domain:
      packet+=self.data[:2] + "\x81\x80"
      packet+=self.data[4:6] + self.data[4:6] + '\x00\x00\x00\x00'   # Questions and Answers Counts
      packet+=self.data[12:]                                         # Original Domain Name Question
      packet+='\xc0\x0c'                                             # Pointer to domain name
      packet+='\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'             # Response type, ttl and resource data length -> 4 bytes

      if re.match(".*web-platform\.test" , self.domain[0:-1]):
        packet+=str.join('',map(lambda x: chr(int(x)), ip.split('.'))) # 4bytes of IP
#        self.ip = ip
#      else:
#        resolved = socket.gethostbyname(self.domain[0:-1])
#        self.ip = resolved
#        packet+=str.join('',map(lambda x: chr(int(x)), resolved.split('.'))) # 4bytes of IP
    return packet

def usage():
  print ""
  print "Usage:"
  print ""
  print "\t# python dns.py ip"
  print ""
  print "Description:"
  print ""
  print "\tdns.py will respond to all DNS queries with a applied IPv4 address when name is /.*web-platform.test/."
  print ""
  print "\tYou may specify the IP address to be returned as the first argument on the command line:\n"
  print "\t\t# python dns.py 192.168.1.100\n"
  print "\t\tor\n"
  print "\t\t$ sudo python dns.py 192.168.1.100\n"
  print ""

  sys.exit(1)


if __name__ == '__main__':
  ip = None

  if len(sys.argv[-1].split('.')) == 4:
    ip=sys.argv[-1]

  if ip is None:
    print "ERROR: Invalid IP address or interface name specified!"
    usage()

  try:
    udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udps.bind(('',53))
  except Exception, e:
    print "Failed to create socket on UDP port 53:", e
    sys.exit(1)

  print 'dns.py :: .*web-platform.test 60 IN A %s\n' % ip
  
  try:
    while 1:
      data, addr = udps.recvfrom(1024)
      p=DNSQuery(data)
      udps.sendto(p.respuesta(ip), addr)
      print 'Request: %s -> %s' % (p.domain, ip)
  except KeyboardInterrupt:
    print '\nBye!'
    udps.close()
