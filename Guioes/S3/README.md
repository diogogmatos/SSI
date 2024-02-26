## Q1: Consegue observar diferenças no comportamento dos programas otp.py e bad_otp.py? Se sim, quais?

### Diferenças entre otp.py e bad_otp.py:

##### 1ª Gerar a Chave:

- otp.py: Utiliza a função os.urandom para gerar bytes aleatórios de forma segura, garantindo a imprevisibilidade da chave.
- bad_otp.py: Utiliza a função random.randbytes com uma semente insegura (random.randbytes(2)) para gerar bytes pseudo-aleatórios. Essa semente é previsível e facilmente replicável, tornando a chave vulnerável.

##### 2ª Segurança:

- otp.py: Utiliza métodos seguros para gerar a chave e realizar a criptografia, dificultando a quebra da cifra.
- bad_otp.py: Utiliza métodos inseguros para gerar a chave, comprometendo a segurança da criptografia e tornando os dados vulneráveis a ataques.

### Conclusão:

otp.py: É um programa seguro para criptografia por OTP (One-Time Pad) utilizando uma chave aleatória criptográficamente segura.
bad_otp.py: É um programa inseguro que não deve ser utilizado para criptografia por causa de sua implementação vulnerável.
Observação:

É importante ressaltar que o OTP (One-Time Pad) é teoricamente seguro apenas se a chave for completamente aleatória, usada apenas uma vez e do tamanho da mensagem. Mesmo o otp.py tem limitações se essas condições não forem rigorosamente seguidas.

## Q2: O ataque realizado no ponto anterior não entra em contradição com o resultado que estabelece a "segurança absoluta" da cifra one-time pad? Justifique.


### Ataque contra a cifra One-Time Pad (OTP)
O ataque realizado no ponto anterior não entra em contradição com a "segurança absoluta" da cifra OTP, pois o programa bad_otp.py não implementa a cifra OTP de forma correta.

##### Falhas no programa:

O programa bad_otp.py apresenta duas falhas principais que o tornam vulnerável a ataques:

- Geração de chave insegura: A chave é gerada com a função bad_prng, que utiliza uma semente previsível e facilmente replicável. Isso significa que um atacante pode determinar a chave com tempo e esforço suficientes, anulando a segurança da cifra OTP.
- Reutilização da chave: O programa permite a reutilização da chave, o que é uma prática insegura e viola um dos princípios fundamentais da cifra OTP. A chave deve ser usada apenas uma vez e descartada após a criptografia.

##### Segurança da cifra OTP:

A cifra OTP é considerada teoricamente segura se as seguintes condições forem rigorosamente satisfeitas:

1. A chave deve ser completamente aleatória e imprevisível.
2. A chave deve ser usada apenas uma vez e descartada após a criptografia.
3. A chave deve ter o mesmo tamanho da mensagem a ser criptografada.

##### Ataque não contradiz a segurança:

O ataque realizado no ponto anterior explora as falhas específicas do programa bad_otp.py e não se aplica à cifra OTP implementada de forma correta. Se as condições mencionadas acima forem cumpridas, a cifra OTP é considerada inquebrável, pois não há como um atacante determinar a chave sem conhecê-la previamente.

##### Considerações adicionais:

A implementação da cifra OTP é complexa e exige cuidado para garantir que todas as condições de segurança sejam satisfeitas.
Na prática, é difícil garantir que a chave seja completamente aleatória e imprevisível.
O uso da cifra OTP pode ser inviável para grandes volumes de dados devido à necessidade de gerar e distribuir chaves de tamanho equivalente.
Conclusão:

O ataque contra o programa bad_otp.py não invalida a segurança da cifra OTP quando implementada de forma correta. As falhas do programa residem na geração e reutilização da chave, não na própria cifra.

###### Observações:

O ataque realizado é um exemplo de ataque de força bruta contra a chave.
Existem outros tipos de ataques que podem ser explorados contra a cifra OTP, dependendo da implementação específica.