import os

#------ENVIAR------------

#Abrir o ficheiro em modo readbytes
file = open("filename", "rb")

#Saber qual o tamanho do ficheiro
file_size = os.path.getsize("filename")

#É preciso enviar a extensão, o nome, o size, e o conteudo

#tirar o conteudo do file
data = file.read()
#Enviar este conteudo... será necessário fazer a separação por blocos e utilizar delimitador
#para saber onde terminam os dados de dito ficheiro


#-------RECEBER------- (todos estes dados tem de ser reduzidos á ideia de blocos*)

#Receber os dados
file_name = client.recv(1024).decode()
file_size = client.recv(1024).decode()

#criar ficheiro no novo peer
file = open(file_name, "wb")

#conteudo do ficheiro
file_bytes = b""

done = False

#receber os dados do ficheiro
while not done:
    data = client.recv(1024)
    if file_bytes[-1:] == "delimitador":
        done = True
    else:
        file_bytes = data
        
#Escrever no ficheiro os dados que recebemos
file.write(file_bytes)

file.close()

#*Vamos ter de retirar o size do ficheiro, dividir em blocos... e enviamos bloco a bloco... 
#*O bloco quando enviado, tem de levar o nome do ficheiro, o numero do bloco, os dados
#*Por ser UDP temos fazer as tais verificações...
#*O ficheiro final só pode ser construido quando tivermos os blocos todos