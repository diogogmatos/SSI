#include "../includes/lib.h"
#include "../includes/queue.h"
#include <stdlib.h>

#define QUEUE_SIZE 1024

typedef struct _queue
{
    MESSAGE messages[QUEUE_SIZE];
    int current_index;
} QUEUE;

MESSAGE pop_message(QUEUE *queue)
{
    // queue empty -> empty message
    if (queue->current_index == 0)
    {
        printf("[ERROR] Queue is empty");
        fflush(stdout);
        MESSAGE r;
        return r;
    }

    // get first message
    MESSAGE r = queue->messages[0];

    // decrement current index
    queue->current_index--;

    // shift messages
    for (int i = 0; i < queue->current_index; i++)
    {
        queue->messages[i] = queue->messages[i + 1];
    }

    return r;
}

int push_message(QUEUE *queue, MESSAGE m)
{
    // queue full -> error
    if (queue->current_index == QUEUE_SIZE)
    {
        printf("[ERROR] Queue is full");
        fflush(stdout);
        return -1;
    }

    // add message to queue
    queue->messages[queue->current_index] = m;
    queue->current_index++;

    return 0;
}
