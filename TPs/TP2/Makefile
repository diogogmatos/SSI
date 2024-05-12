SRCDIR := src
OBJDIR := obj
BINDIR := bin
TMPDIR := tmp
USERDIR := concordia

CC := gcc
CFLAGS := -Wall -g -lssl -lcrypto -lacl
INC := -I includes/

SCRIPTS := concordia-ativar concordia-responder concordia-grupo-destinario-remover concordia-enviar concordia-desativar concordia-grupo-criar concordia-listar concordia-ler concordia-remover concordia-grupo-listar concordia-grupo-destinario-adicionar concordia-grupo-remover server

SCRIPT_OBJS := $(addprefix $(OBJDIR)/, $(addsuffix.o, $(SCRIPTS)))

EXEC := $(addprefix $(BINDIR)/, $(SCRIPTS))

# Ensure directories exist
$(shell mkdir -p $(OBJDIR) $(BINDIR))

.PHONY: all
all: $(EXEC)

$(BINDIR)/%: $(OBJDIR)/%.o
	$(CC) $(CFLAGS) $(INC) -o $@ $<

$(OBJDIR)/%.o: $(SRCDIR)/%.c
	$(CC) $(CFLAGS) $(INC) -o $@ -c $<

.PHONY: clean
clean:
	@rm -rf $(OBJDIR)/* $(BINDIR)/* $(TMPDIR)

clean-users:
	@rm -rf $(USERDIR)/*

rebuild:
	@make clean
	@make all

.PHONY: run
run-server:
	@./$(BINDIR)/server

.PHONY: run
run-ativar:
	@./$(BINDIR)/concordia-ativar

.PHONY: run
run-desativar:
	@./$(BINDIR)/concordia-desativar
