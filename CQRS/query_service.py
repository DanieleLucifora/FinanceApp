import mysql.connector
import finance_app_pb2

def connessione_db():
    try:
        connection = mysql.connector.connect(
            host='mysqldb',     #TODO: mysqldb quando siamo su docker, localhost in locale
            user='server',
            password='1234',
            database='finance_app'
        )
        return connection
    except mysql.connector.Error:
        print("Errore nella connessione al database.")
        return None
        
class QueryService:
    
    def get_ultimo_valore(request):
        try:
            connection = connessione_db()
            cursor = connection.cursor()
            query = "SELECT valore FROM data WHERE email = %s ORDER BY timestamp DESC LIMIT 1"
            cursor.execute(query, (request.email,))
            risultato = cursor.fetchone()
            if risultato:       #TODO: controlla la logica
                print(f"Valore ottenuto: {risultato[0]}")
                return finance_app_pb2.Valore(valore=risultato[0])
            else:
                print("Nessun valore trovato.")
                return finance_app_pb2.Valore(valore=0.0)
        except mysql.connector.Error as errore:
            print(f"Errore durante la richiesta: {errore}")
            return finance_app_pb2.Valore(valore = 0.0)
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()

    def get_media_valori(request):
        try:
            connection = connessione_db()
            cursor = connection.cursor()
            query = """SELECT AVG(valore) FROM data WHERE email = %s AND ticker = 
                     (SELECT ticker FROM data WHERE email = %s ORDER BY timestamp DESC LIMIT 1) 
                     ORDER BY timestamp DESC LIMIT %s"""    #La seconda riga della query è usata per selezionare solo le entrate dell'utente con l'ultimo ticker 
            #TODO: Se elimino le entrate in data quando aggiorno il ticker, non ho bisogno della query interna
            cursor.execute(query, (request.email, request.email, request.numeroDati))
            risultato = cursor.fetchone()
            print(f"Valore ottenuto: {round(risultato[0], 2)}")
            return finance_app_pb2.Valore(valore = risultato[0])
        except mysql.connector.Error as errore:
            print(f"Errore durante la richiesta: {errore}")
            return finance_app_pb2.Valore(valore = 0.0)
        finally:
            if cursor:
                cursor.close()
            if connection.is_connected():
                connection.close()