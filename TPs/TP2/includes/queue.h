#ifndef QUEUE_H
#define QUEUE_H

#include "../src/queue.c"

typedef struct _queue QUEUE;

MESSAGE pop_message(QUEUE *queue);
int push_message(QUEUE *queue, MESSAGE m);

#endif
