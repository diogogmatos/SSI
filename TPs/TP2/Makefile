SRCDIR := src
OBJDIR := obj
BINDIR := bin

CC := gcc
CFLAGS := -Wall -g -lssl -lcrypto -lacl
INC := -I includes/

SCRIPTS := concordia-ativar concordia-responder concordia-grupo-destinario-remover concordia-enviar concordia-desativar concordia-grupo-criar concordia-listar concordia-remover concordia-grupo-listar concordia-grupo-destinario-adicionar concordia-grupo-remover server

SCRIPT_OBJS := $(addprefix $(OBJDIR)/, $(addsuffix .o, $(SCRIPTS)))

EXEC := $(addprefix $(BINDIR)/, $(SCRIPTS))

.PHONY: all
all: $(EXEC)

$(BINDIR)/%: $(OBJDIR)/%.o
	$(CC) $(CFLAGS) $(INC) -o $@ $<

$(OBJDIR)/%.o: $(SRCDIR)/%.c
	$(CC) $(CFLAGS) $(INC) -o $@ -c $<

.PHONY: clean
clean:
	@rm -f $(OBJDIR)/* $(BINDIR)/*
