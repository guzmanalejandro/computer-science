#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <pthread.h>



#define LEN_CODE_AIRPORT 3
#define STR_CODE_AIRPORT (LEN_CODE_AIRPORT+1) // Incluimos el caracter de final de palabra '\0'
#define NUM_AIRPORTS 303

#define COL_ORIGIN_AIRPORT 17
#define COL_DESTINATION_AIRPORT 18

#define MAXCHAR 500

/**
 * Reserva espacio para una matriz de tamaño nrow x ncol,
 * donde cada elemento de la matriz tiene size bytes
 */

void **malloc_matrix(int nrow, int ncol, size_t size)
{
  int i;

  void **ptr;

  ptr = malloc(sizeof(void *) * nrow);
  for(i = 0; i < nrow; i++) {
  	ptr[i] = calloc(size * ncol, sizeof(int));
  }
    

  return ptr;
}

/**
 * Libera una matriz de tamaño con nrow filas. Utilizar
 * la funcion malloc_matrix para reservar la memoria 
 * asociada.
 */

void free_matrix(void **matrix, int nrow)
{
  int i;

  for(i = 0; i < nrow; i++)
    free(matrix[i]);
    
  free(matrix);
}

/**
 * Leer el fichero fname que contiene los codigos
 * IATA (3 caracteres) de los aeropuertos a analizar.
 * En total hay NUM_AIRPORTS a leer, un valor prefijado
 * (para simplificar el código). Los codigos de los
 * aeropuertos se alacenan en la matriz airports, una
 * matriz cuya memoria ha sido previamente reservada.
 */

void read_airports(char **airports, char *fname) 
{
  int i;
  char line[MAXCHAR];

  FILE *fp;

  /*
   * eow es el caracter de fin de palabra
   */
  char eow = '\0';

  fp = fopen(fname, "r");
  if (!fp) {
    printf("ERROR: could not open file '%s'\n", fname);
    exit(1);
  }

  i = 0;
  while (i < NUM_AIRPORTS)
  {
    fgets(line, 100, fp);
    line[3] = eow; 

    /* Copiamos los datos al vector */
    strcpy(airports[i], line);

    i++;
  }

  fclose(fp);
}

/**
 * Dada la matriz de con los codigos de los aeropuertos,
 * así como un código de aeropuerto, esta función retorna
 * la fila asociada al aeropuerto.
 */

int get_index_airport(char *code, char **airports)
{
  int i;

  for(i = 0; i < NUM_AIRPORTS; i++) 
    if (strcmp(code, airports[i]) == 0)
      return i;

  return -1;
}


/**
 * Dada la matriz num_flights, se imprimen por pantalla el
 * numero de destinos diferentes que tiene cada aeropuerto.
 */

void print_num_flights_summary(int **num_flights, char **airports)
{
  int i, j, num;

  for(i = 0; i < NUM_AIRPORTS; i++) 
  {
    num = 0;

    for(j = 0; j < NUM_AIRPORTS; j++)
    {
      if (num_flights[i][j] > 0)
        num++;
    }

    printf("Origin: %s -- Number of different destinations: %d\n", airports[i], num);
  }
}

/**
 * Esta funcion se utiliza para extraer informacion del fichero CSV que
 * contiene informacion sobre los vuelos. En particular, dada una linea
 * leida de fichero, la funcion extra el origen y destino de los vuelos.
 */

int extract_fields_airport(char *origin, char *destination, char *line) 
{
  /*Recorre la linea por caracteres*/
  char caracter;
  /* i sirve para recorrer la linea
   * iterator es para copiar el substring de la linea a char
   * coma_count es el contador de comas
   */
  int i, iterator, coma_count;
  /* start indica donde empieza el substring a copiar
   * end indica donde termina el substring a copiar
   * len indica la longitud del substring
   */
  int start, end, len;
  /* invalid nos permite saber si todos los campos son correctos
   * 1 hay error, 0 no hay error 
   */
  int invalid = 0;
  /* found se utiliza para saber si hemos encontrado los dos campos:
   * origen y destino
   */
  int found = 0;
  /*
   * eow es el caracter de fin de palabra
   */
  char eow = '\0';
  /*
   * contenedor del substring a copiar
   */
  char word[STR_CODE_AIRPORT];
  /*
   * Inicializamos los valores de las variables
   */
  start = 0;
  end = -1;
  i = 0;
  coma_count = 0;
  /*
   * Empezamos a contar comas
   */
  do {
    caracter = line[i++];
    if (caracter == ',') {
      coma_count ++;
      /*
       * Cogemos el valor de end
       */
      end = i;
      /*
       * Si es uno de los campos que queremos procedemos a copiar el substring
       */
      if (coma_count ==  COL_ORIGIN_AIRPORT || coma_count == COL_DESTINATION_AIRPORT) {
        /*
         * Calculamos la longitud, si es mayor que 1 es que tenemos 
         * algo que copiar
         */
        len = end - start;

        if (len > 1) {

          if (len > STR_CODE_AIRPORT) {
            printf("ERROR len code airport\n");
            exit(1);
          }

          /*
           * Copiamos el substring
           */
          for(iterator = start; iterator < end-1; iterator ++){
            word[iterator-start] = line[iterator];
          }
          /*
           * Introducimos el caracter de fin de palabra
           */
          word[iterator-start] = eow;
          /*
           * Comprobamos que el campo no sea NA (Not Available) 
           */
          if (strcmp("NA", word) == 0)
            invalid = 1;
          else {
            switch (coma_count) {
              case COL_ORIGIN_AIRPORT:
                strcpy(origin, word);
                found++;
                break;
              case COL_DESTINATION_AIRPORT:
                strcpy(destination, word);
                found++;
                break;
              default:
                printf("ERROR in coma_count\n");
                exit(1);
            }
          }

        } else {
          /*
           * Si el campo esta vacio invalidamos la linea entera 
           */

          invalid = 1;
        }
      }
      start = end;
    }
  } while (caracter && invalid==0);

  if (found != 2)
    invalid = 1;

  return invalid;
}

/**
 * Dado un fichero CSV que contiene informacion entre multiples aeropuertos,
 * esta funcion lee cada linea del fichero y actualiza la matriz num_flights
 * para saber cuantos vuelos hay entre cada cuidad origen y destino.
 */ 


// Definimos un tamaño para el buffer
// Y un número de líneas por bloque
#define B_SIZE 5
#define C_LINES 100

// Estructura Cell
typedef struct cell {

    int nelems;
    char **lines;
    
} cell;

// Estructura Buffer
struct buffer {
  cell **cells;
  int read;
  int write;
  int counter;
};

// Define the params for the cosumer files
struct param {
  struct buffer *buffer;
  int **num_flights;
  char **airports;
};

pthread_mutex_t shared_data = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t save = PTHREAD_MUTEX_INITIALIZER;

pthread_cond_t consumidor = PTHREAD_COND_INITIALIZER;
pthread_cond_t productor = PTHREAD_COND_INITIALIZER;

int finish = 0;

void *th_consumidor(void *arg) {
    
    char origin[STR_CODE_AIRPORT], destination[STR_CODE_AIRPORT];
    int invalid, index_origin, index_destination;
    int i, j;
    
    // Leemos los parametros
    struct param *info = (struct param *) arg;
    // Declaramos el buffer
    struct buffer *buffer = info->buffer;

    // Celdas temporales para evitar sobreescriptura
    cell *lectura, *cellbuffer;

    // Reservamos memoria
    lectura = malloc(sizeof(cell));

    lectura->nelems = 0;

    lectura->lines = malloc(sizeof(char *) * C_LINES);

    for (j = 0; j < C_LINES; j++) {
      lectura->lines[j] = malloc(sizeof(char *) * MAXCHAR);  
    }

    while (!finish) {
      // Lock porque accedemos a buffer
      pthread_mutex_lock(&shared_data);

      // Esperamos a que haya datos disponibles
      while ((buffer->counter == 0) && (!finish)) {
        pthread_cond_wait(&consumidor, &shared_data);
      }

      // Comprovamos que haya datos que leer
      if ((buffer->counter == 0) && (finish)) {
        break;
      } else {
      	// Intercambio de datos con buffer
        cellbuffer = buffer->cells[buffer->read];
        buffer->cells[buffer->read] = lectura;
        lectura = cellbuffer;

        buffer->read += 1;

        if (buffer->read == B_SIZE) {
          buffer->read = 0;
        }

        buffer->counter--;
        pthread_cond_signal(&productor);  
      }

      pthread_mutex_unlock(&shared_data);
      
      // Procesamos los datos extraidos
      index_origin = get_index_airport(origin, info->airports);
      index_destination = get_index_airport(destination, info->airports);

      for (i = 0; i < lectura->nelems; i++) {
        invalid = extract_fields_airport(origin, destination, lectura->lines[i]);
        if (!invalid) {

          index_origin = get_index_airport(origin, info->airports);
          index_destination = get_index_airport(destination, info->airports);

          if ((index_origin >= 0) && (index_destination >= 0)){
          	// Lock por modificar la matriz compartida
            pthread_mutex_lock(&save);
            info->num_flights[index_origin][index_destination]++;
            pthread_mutex_unlock(&save);
          }
        } 
      }       
    }

    // Liberamos memoria
    for (j = 0; j < C_LINES; j++) {
      free(lectura->lines[j]);  
    }

    free(lectura->lines);
    free(lectura);
}

void read_airports_data(int **num_flights, char **airports, char *fname) {
    char line[MAXCHAR];	
    FILE *fp;
    
    // Creamos el buffer
    struct buffer buffer;
    buffer.write = 0;
    buffer.read = 0;
    buffer.counter = 0;
    buffer.cells = malloc(B_SIZE * sizeof(cell));

    cell *insertData;
    int i,j;
    // Reservamos las celdas del buffer
    for (i = 0; i < B_SIZE; i++) {
      insertData = malloc(sizeof(cell));
      buffer.cells[i] = insertData;

      insertData->nelems = 0;
      insertData->lines = malloc(sizeof(char *) * C_LINES);
      
      for (j = 0; j < C_LINES; j++) {
        insertData->lines[j] = malloc(sizeof(char *) * MAXCHAR);
      }
    }

    // Parametros para los hilos del consumidor
    struct param info = {&buffer, num_flights, airports};
    
    pthread_t th1, th2;
    
    // Creamos los hilos del consumidor
    pthread_create(&th1, NULL, th_consumidor, (void*) &info);
    pthread_create(&th2, NULL, th_consumidor, (void*) &info);

    // Abrimos el archivo
    fp = fopen(fname, "r");
    if (!fp) {
      printf("ERROR: could not open '%s'\n", fname);
      exit(1);
    }
    
    // Leemos el header y lo descartamos
    fgets(line, MAXCHAR, fp);

    // Creamos una celda para el intercambio
    // de datos con el buffer
    cell *cellproductor = malloc(sizeof(cell));
    cellproductor->nelems = 0;

    // Reservamos memoria para las líneas
    cellproductor->lines = malloc(sizeof(char *) * C_LINES);
    for (j = 0; j < C_LINES; j++) {
      cellproductor->lines[j] = malloc(sizeof(char *) * MAXCHAR);
    }

    // Creamos una celda temporal para ayudar
    // con el intercambio de datos del buffer
    cell *tmp;

    while (1) {
      // Leemos las líneas del fichero
      while ((cellproductor->nelems < C_LINES) && (fgets(cellproductor->lines[cellproductor->nelems], MAXCHAR, fp) != NULL)) {
        cellproductor->nelems += 1;
      }

      // Siempre que cell no esté vacía añadimos al buffer
      if (cellproductor->nelems > 0) {
      	// Hacemos lock porque estamos accediendo a datos compartidos
        pthread_mutex_lock(&shared_data);
        // Esperamos a recibir una señal del consumidor
        // si el buffer está lleno
        while (buffer.counter == B_SIZE) {
          pthread_cond_wait(&productor, &shared_data);
        }

        // Hacemos el intercambio de datos con el buffer
        tmp = buffer.cells[buffer.write];
        buffer.cells[buffer.write] = cellproductor;
        cellproductor = tmp;

        buffer.write += 1;

        // Vaciamos el buffer
        if (buffer.write == B_SIZE) {
          buffer.write = 0;
        }

        buffer.counter++;
        // El consumidor puede comenzar a leer, y le avisamos
        pthread_cond_signal(&consumidor);
        // Desbloqueamos y reiniciamos el cell
        pthread_mutex_unlock(&shared_data);
        cellproductor->nelems = 0;

      } 
      // Cell está vacía
      else {
        break;
      } 
    }

    // Avisamos a los consumidores de que no añadimos más datos
    pthread_mutex_lock(&shared_data);
    finish = 1;
    pthread_cond_signal(&consumidor);
    pthread_mutex_unlock(&shared_data);

    // Liberamos la celda temporal
    for (j = 0; j < C_LINES; j++) {
      free(cellproductor->lines[j]);
    }
    free(cellproductor->lines);
    free(cellproductor);

    // Esperamos a los threads consumidores
    pthread_join(th1, NULL);
    pthread_join(th2, NULL);

    // Liberamos memoria
    cell *erase;

    for (i = 0; i < B_SIZE; i++) {
      erase = buffer.cells[i];
      for (j = 0; j < C_LINES; j++) {
        free(erase->lines[j]);
      }
      free(erase->lines);
      free(erase);
    }
    
    fclose(fp);
}

/**
 * Esta es la funcion principal que realiza los siguientes procedimientos
 * a) Lee los codigos IATA del fichero de aeropuertos
 * b) Lee la informacion de los vuelos entre diferentes aeropuertos y
 *    actualiza la matriz num_flights correspondiente.
 * c) Se imprime para cada aeropuerto origen cuantos destinos diferentes
 *    hay.
 * d) Se imprime por pantalla lo que ha tardado el programa para realizar
 *    todas estas tareas.
 */

int main(int argc, char **argv)
{
  char **airports;
  int **num_flights;

  if (argc != 3) {
    printf("%s <airport.csv> <flights.csv>\n", argv[0]);
    exit(1);
  }

  struct timeval tv1, tv2;

  // Tiempo cronologico 
  gettimeofday(&tv1, NULL);

  // Reserva espacio para las matrices
  airports    = (char **) malloc_matrix(NUM_AIRPORTS, STR_CODE_AIRPORT, sizeof(char));
  num_flights = (int **) malloc_matrix(NUM_AIRPORTS, NUM_AIRPORTS, sizeof(int));

  // Lee los codigos de los aeropuertos 
  read_airports(airports, argv[1]);

  // Lee los datos de los vuelos
  read_airports_data(num_flights, airports, argv[2]);
	
  // Imprime un resumen de la tabla
  print_num_flights_summary(num_flights, airports);

  // Libera espacio
  free_matrix((void **) airports, NUM_AIRPORTS);
  free_matrix((void **) num_flights, NUM_AIRPORTS);

  // Tiempo cronologico 
  gettimeofday(&tv2, NULL);

  // Tiempo para la creacion del arbol 
  printf("Tiempo para procesar el fichero: %f segundos\n",
      (double) (tv2.tv_usec - tv1.tv_usec) / 1000000 +
      (double) (tv2.tv_sec - tv1.tv_sec));

  return 0;
}




