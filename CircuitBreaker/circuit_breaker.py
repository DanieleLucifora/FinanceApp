import time
import threading

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=30, expected_exception=Exception): #val. default
        self.failure_threshold = failure_threshold          # Numero di errori per l'open
        self.recovery_timeout = recovery_timeout            # Tempo di reset per l'half open
        self.expected_exception = expected_exception        # Eccezione probabile nella funzione
        self.failure_count = 0                              
        self.last_failure_time = None                       # Timestamp
        self.state = 'CLOSED'                               
        self.lock = threading.Lock()                        # oggetto lock
                                                            # sicurezza nella modifica dello stato

    def call(self, func, *args, **kwargs):  #numero variabile di argomenti
        with self.lock: #rilascio automatico del lock alla fine del blocco
            if self.state == 'OPEN':
                time_since_failure = time.time() - self.last_failure_time
                if time_since_failure > self.recovery_timeout:
                    self.state = 'HALF_OPEN'
                else:
                    raise CircuitBreakerOpenException("Il circuito è aperto, chiamata negata.")  #non necessito return
            
            try:
                result = func(*args, **kwargs)
            except self.expected_exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                if self.failure_count >= self.failure_threshold:
                    self.state = 'OPEN'
                raise e #eccezione della funzione
            else:   #se non abbiamo l'except (solo python)
                if self.state == 'HALF_OPEN':
                    self.state = 'CLOSED'   #dopo 1 successo
                    self.failure_count = 0
                return result

class CircuitBreakerOpenException(Exception):
    pass