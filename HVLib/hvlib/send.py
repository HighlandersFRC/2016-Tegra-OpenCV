import socket

class send:
    def __init__(self,host,port):
    	self.host = host
    	self.port = port
    	self.isStopped = False
    	self.isConnected = False	
   	#Creates the socket object 
    def connect(self):
    	self.soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	self.soc.settimeout(2)
    	#self.soc.setblocking(0)
    
    # user method to begin sending messages
    def send(self,message):
		if not self.isConnected:
			try:
				print("Trying Connection")
				#self.connect()
				self.soc.connect((self.host,self.port))	
				self.isConnected = True
				print("Connection Established")
			except:
				print("Connection Failed")
		if self.isConnected:
			try:
				self.soc.send(message + "\n")
			except:
				print("Lost Connection")
				self.isConnected = False
				#self.soc.close()


    def stop(self):
        self.isStopped = True



