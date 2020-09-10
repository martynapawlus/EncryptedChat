# EncryptedChat
This project is a client-server chat application with symmetric encryption.  
Operating principles of the application:  
* server starts running (run socket_server.py)  
* clients join the server (run kiwi.py and connect with your nickname)  
* all messages are sent on broadcast but clients can send them encrypted or as a plain text
* Plain text: leave the area located next to encrypt button empty
* Encrypted message: write nickname of your friend next to encrypt button then click this button,
if you have already clicked it then you can write encrypted messages to the person whose nickname is entered  
To encrypt messages I used Diffie-Hellman key exchange. Firstly each client generate its public and private keys, 
then to get identical symmetric key with a friend, client uses methods located in client/encryption.py to exchange partial 
and lastly symmetric key, it is done based on Diffie-Hellman protocol. After generating symmetric key both clients know it 
so they can encrypt and decrypt messages using methods from client/encryption.py.  
All communication between clients and the server is clear thanks to the flags that are described in the files.<br><br>
Graphic interface is written using kivy library and it is located in client/kiwi.py.
