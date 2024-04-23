#include <fcntl.h>
#include <openssl/evp.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

void handleErrors(void) {
  char buffer[1024];
  snprintf(buffer, 1024, "Encryption error\n");
  write(1, buffer, strlen(buffer));
  exit(1);
}

void encryptData(const unsigned char *plaintext, int plaintext_len,
                 unsigned char *key, unsigned char *iv,
                 unsigned char *ciphertext) {
  EVP_CIPHER_CTX *ctx;
  int len;
  int ciphertext_len;

  if (!(ctx = EVP_CIPHER_CTX_new()))
    handleErrors();

  if (1 != EVP_EncryptInit_ex(ctx, EVP_aes_128_cbc(), NULL, key, iv))
    handleErrors();

  if (1 != EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len))
    handleErrors();
  ciphertext_len = len;

  if (1 != EVP_EncryptFinal_ex(ctx, ciphertext + len, &len))
    handleErrors();
  ciphertext_len += len;

  EVP_CIPHER_CTX_free(ctx);
}