import pickle
import base64
import codecs
import hashlib
from Crypto import Random
from Crypto.Cipher import AES

class AESCipher(object):
	
	def __init__(self, keyPickle):
		self.unpickled = pickle.loads(codecs.decode(keyPickle.encode(), "base64"))
		self.bs = 32
		self.key = hashlib.sha256(self.unpickled.encode()).digest()

	def encrypt(self, wumpus):
		wumpus = self._pad(wumpus)
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return base64.b64encode(iv + cipher.encrypt(wumpus))

	def decrypt(self, wumpus):
		wumpus = base64.b64decode(wumpus)
		iv = wumpus[:AES.block_size]
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return self._unpad(cipher.decrypt(wumpus[AES.block_size:])).decode('utf-8')

	def _pad(self, wumpus):
		return wumpus + (self.bs - len(wumpus) % self.bs) * chr(self.bs - len(wumpus) % self.bs)

	def _unpad(self, wumpus):
		return wumpus[:-ord(wumpus[len(wumpus)-1:])]

