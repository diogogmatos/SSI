# Define variables for directories
SRCDIR := src
OBJDIR := obj
BINDIR := bin

CC := gcc
EXEC := $(BINDIR)/server $(BINDIR)/user
CFLAGS := -Wall -g -lssl -lcrypto
INC := -I includes/
SRC1 := $(shell find src/ -name '*.c' -not -name 'server.c')
SRC2 := $(shell find src/ -name '*.c' -not -name 'user.c')	

.PHONY: all
all: $(EXEC)

build:

$(BINDIR)/server: $(SRC2)
	$(CC) $(CFLAGS) $(INC) -o $@ $^

$(BINDIR)/user: $(SRC1)
	$(CC) $(CFLAGS) $(INC) -o $@ $^

.PHONY: clean
clean:
	rm -f $(OBJDIR)/* $(BINDIR)/*

.PHONY: format
format:
	clang-format -i -style=file $(shell find src/ -name '*.c' -o -name '*.h') $(shell find includes/ -name '*.h')

