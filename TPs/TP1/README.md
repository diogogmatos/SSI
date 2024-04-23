# 1ª Fase do Projeto de Segurança de Sistemas Informáticos

## 1. Introdução
Este projeto foi desenvolvido no âmbito da unidade curricular de Segurança de Sistemas Informáticos (SSI) no ano de 2023/2024.
A primeira fase do projeto consiste em criar um serviço de Message Relay que permite aos membros de uma organização trocarem mensagens com garantias de autenticidade.
O serviço é suportado por um servidor responsável por manter o estado da aplicação e interagir com os utilizadores do sistema. Todo os intervenientes do sistema (servidor e utilizadores) serão identificados por um identificador único (UID).

## 2. Validação da conexão entre o Cliente e o Servidor
De forma a termos um processo de comunicação de seguro entre os clientes e o servidor é utilizado uma chave de criptografia assimétrica (RSA), um protocolo de troca de chaves de Diffie-Hellman (DH), para além de uma criptografia simétrica (AES-GCM).

#### 2.1 Troca de Chave Diffie-Hellman
A aplicação emprega o algoritmo de troca de chave Diffie-Hellman para estabelecer um canal de comunicação seguro entre o cliente e o servidor. Este algoritmo permite que as duas partes concordem com uma chave secreta compartilhada sem trocá-la diretamente pela rede, evitando assim a espionagem.

## 3. Encriptação
#### 3.1 Encriptação Assimétrica (RSA)
Após a troca bem-sucedida da chave, o cliente e o servidor utilizam a encriptação RSA para comunicação segura. A encriptação RSA garante que as mensagens trocadas entre os utilizadores sejam encriptadas usando uma chave pública e só possam ser desencriptadas usando a chave privada correspondente.

#### 3.2 Encriptação Simétrica (AES-GCM)
Além da encriptação RSA, a aplicação utiliza o Padrão de Encriptação Avançada (AES) em Modo Galois/Contador (GCM) para encriptação simétrica. O AES-GCM garante que as mensagens armazenadas na base de dados do servidor sejam encriptadas usando uma chave secreta compartilhada derivada da troca de chave Diffie-Hellman, fornecendo confidencialidade e integridade.

## 4. Comandos
A aplicação suporta os seguintes comandos para interagir com o servidor:

#### 4.1 Send
```py
python msg_client.py send <USER> <SUBJECT>
> Input Message:
```
Permite aos utilizadores enviar uma mensagem para outro utilizador. A mensagem é encriptada antes da transmissão para garantir a confidencialidade.

#### 4.2 Askqueue
Permite aos utilizadores consultar mensagens não lidas na sua caixa de entrada. O servidor recupera mensagens não lidas da base de dados e as retorna ao utilizador.
```py
python msg_cliente.py askqueue
```
#### 4.3 Getmsg
Permite aos utilizadores recuperar uma mensagem específica pelo seu ID. O servidor desencripta a mensagem usando a chave secreta compartilhada e verifica a sua autenticidade antes de a devolver ao utilizador.
```py
python msg_cliente.py getmsg <NUM>
```
### 4.4 Help
Exibe informações de utilização e comandos disponíveis para o utilizador.
```py
python msg_cliente.py help
```
## 5. Conclusão
A Aplicação de Mensagens Cliente-Servidor TCP em Python fornece uma solução robusta e segura para facilitar a troca de mensagens entre utilizadores por meio de uma rede TCP/IP. Ao implementar técnicas avançadas de encriptação e algoritmos de troca de chave segura, a aplicação garante a confidencialidade, integridade e autenticidade das mensagens trocadas entre clientes.



## 4. Valorizações (implementadas)

Recorrer a JSON ou outro formato similar para estruturar as mensagens do protocolo de comunicação - Foi implementado um formato estruturado utilizando JSON para padronizar a comunicação entre o cliente e o servidor. Isso proporciona uma melhor interpretação e manipulação das mensagens, além de permitir uma maior flexibilidade na inclusão de metadados ou campos adicionais nas mensagens, se necessário. Além disso, foi adotado o formato de codificação binária BSON para otimizar a eficiência da comunicação, especialmente em ambientes com largura de banda limitada.


## 5. Conclusão

Para concluir, o projeto de Message Relay atingiu seus objetivos de proporcionar uma plataforma segura e eficiente para troca de mensagens. As medidas de segurança implementadas garantiram a confidencialidade e integridade dos dados, enquanto as valorizações adicionais demonstraram um compromisso com a melhoria contínua do sistema. Em resumo, o projeto estabeleceu uma base sólida para comunicação segura dentro da organização.