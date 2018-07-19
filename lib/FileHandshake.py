import glob, os
import time
class FileHandshake:
    FileName="../temp/handshake.txt"
    stop_fileName = "../temp/stopHandShake.txt"
    def wait_for_file(self):
        while 1:
            found = glob.glob(self.FileName)
            if found:
                return found
            time.sleep(30)
            
    def wait_for_file_to_be_deleted(self):
        while 1:
            found = glob.glob(self.FileName)
            if not found:
                return found
            time.sleep(30)

    def create_handshake_file(self):
        file = open(self.FileName,"w")
        file.write("Hello World") 
        
    def delete_handshake_file(self):
        os.remove(self.FileName)

    def start_handshake(self):
        self.create_handshake_file()
        self.wait_for_file_to_be_deleted()

    def wait_for_handshake(self,fun):
        self.wait_for_file()
        fun()
        self.delete_handshake_file()
