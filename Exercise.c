#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/mman.h>
#include<unistd.h>
#include <limits.h>
#include <signal.h>
#include <malloc.h>
#include<string.h>

/*Error Handling*/
 #define handle_error(msg) \
           do { perror(msg); exit(EXIT_FAILURE); } while (0)

       static char *buffer;

       static void
       handler(int sig, siginfo_t *si, void *unused)
       {
           /* Note: calling printf() from a signal handler is not safe
              (and should not be done in production programs), since
              printf() is not async-signal-safe; see signal-safety(7).
              Nevertheless, we use printf() here as a simple way of
              showing that the handler was called. */

           printf("Got SIGSEGV at address: 0x%lx\n",
                   (long) si->si_addr);
           exit(EXIT_FAILURE);
       }
/*Main function*/
int main(int argc, char *argv[])
       {
           char *p,*buffer;
	   char c;
           int pagesize;
	   int i=0,size;
           struct sigaction sa;

           sa.sa_flags = SA_SIGINFO;
           sigemptyset(&sa.sa_mask);
           sa.sa_sigaction = handler;
           if (sigaction(SIGSEGV, &sa, NULL) == -1)
               handle_error("sigaction");

           pagesize = sysconf(_SC_PAGE_SIZE);  /* Initializing Pagesize, here pagesize=4096 Bytes*/
           if (pagesize == -1)
               handle_error("sysconf");

    /* Allocate a buffer; it will have the default
       protection of PROT_READ|PROT_WRITE. */
    size=pagesize*10;
    p = memalign(pagesize,size);          /*Allocating buffer'p' of size = ten pages*/
    if (p == NULL)
    handle_error("memalign");

    memset(p,0x00,size);                     /*Copying 'B' to whole buffer*/
    memset(p,0x41,size); 
    
    for(i=0;i<10;i++)
    {
	printf("Address of %d Page: %lx\n",i+1,p+(i*4096));	/*Printing all pages first  bytes from first page. The usage of %d format specifier causes compilation warnings. Can you figure out why?*/
	
    }

// Can start writing code here and can define variables for functions above


   
           exit(EXIT_SUCCESS);
       }


