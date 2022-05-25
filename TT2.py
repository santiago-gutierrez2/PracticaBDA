
#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# TT2.py: 
# Práctica de python
#
# Autor: Adrián Castro Rodríguez (adrian.castro2@udc.es) Santiago Gutierrez Gomez (santiago.gutierrez@udc.es)
# Data de creación: 2-05-2021
#
from distutils.log import error
import errno
import imp
from os import abort
from re import S
from smtplib import SMTPDataError
from sqlite3 import Date, Row
import datetime
import sys
import psycopg2
import psycopg2.extras
import psycopg2.errorcodes
import psycopg2.extensions



## ------------------------------------------------------------
def connect_db():
    try:
        con=psycopg2.connect("")
        return con
    except psycopg2.OperationalError as e:
        print(f"Error conectando: {e}")
        sys.exit(1)
    


## ------------------------------------------------------------
def disconnect_db(conn):
    conn.commit()
    conn.close()

##-------------------------------------------------------------
#- mostrar un artista por su codigo
def show_artista(conn, control_tx=True):
    try:
        cod_art = int(input("Código artista: "))
    except:
        print("Error: datos inválidos")
        return None
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        try:
            cur.execute("Select cod_art, nome, verificacion, data_nacemento, cidade_orixen from artista where cod_art= %(cod_art)s",{'cod_art': cod_art})
            row=cur.fetchone()
            value = None
            if row:
                print(f"Nombre: {row['nome']}, Verficado?: {row['verificacion']}, "
                        f"Fecha de nacimineto: {row['data_nacemento']}, Ciudad origen: {row['cidade_orixen']}")
                value = row['cod_art']
            else:
                print(f"No existe ningún artista por este código: {cod_art}")
            if control_tx:
                conn.commit()
            return value
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.UNDEFINED_TABLE:
                print("Error: Tabla ARTISTA no existe")
            else:
                print(f"Error genérico: {e.pgcode}: {e.pgerror}")
            if control_tx:
                conn.rollback()
            return None

#--------------------------------------------------------------
#- mostrar la info de una cancion por su codigo
def show_song(conn, control_tx=True):
    
    if control_tx:
        conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
    try:
        cod_song = int(input("Código canción: "))
    except:
        print("Error: datos invalidos")
        return None
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        try:
            cur.execute("Select cod_song, titulo, duracion, ano_creacion, explicito, num_reproducciones, xenero, cod_album, cod_artist from cancion where cod_song=%(cod_song)s",{'cod_song': cod_song})
            row=cur.fetchone()
            value=None
            if row:
                print(f"Título: {row['titulo']}, Duración(seg): {row['duracion']}, Año creación: {row['ano_creacion']}, "
                        f"Explícito: {row['explicito']}, Numero de reproducciones: {row['num_reproducciones']}, "
                        f"Género: {row['xenero']}, Album al que pertenece: {row['cod_album']}, Codigo del Artista: {row['cod_artist']}")
                value=row['cod_song']
            else:
                print(f"No existe ninguna cáncion con este código: {cod_song}")
            if control_tx:
                conn.commit()
            return value
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.UNDEFINED_TABLE:
                print("Error: Tabla CANCION no existe")
            else:
                print("Error genérico: {e.pgcode}: {e.pgerror}")
            if control_tx:
                conn.rollback()
            return None
## ------------------------------------------------------------




##-------------------------------------------------------------
#- mostrar un álbum con todas sus canciones por su código por su codigo
def show_album(conn, control_tx=True):

    conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED

    try:
        cod_alb = int(input("Código álbum: "))
    except:
        print("Error: datos inválidos")
        return None
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        try:
            cur.execute("Select cod_alb, titulo, ano_creacion, cod_art_owner from album where cod_alb= %(cod_alb)s",{'cod_alb': cod_alb})
            row=cur.fetchone()
            value = None
            if row:
                print(f"Título: {row['titulo']}, ano de creación: {row['ano_creacion']}, "
                        f"Código de artista que realizou o albúm: {row['cod_art_owner']}")
                value = row['cod_alb']
            else:
                print(f"Non existe ningún álbum por este código: {cod_alb}")


            cur.execute("Select cod_song, titulo, duracion, ano_creacion, explicito, num_reproducciones, xenero, cod_album from cancion where cod_album=%(cod_alb)s",{'cod_alb': cod_alb})
            records=cur.fetchall()
            cantidad = 0
            print("\nCanciones:")
            for row in records:
                print(f"\tTítulo: {row['titulo']}, Duración(seg): {row['duracion']}, Año creación: {row['ano_creacion']}, "
                        f"Explícito: {row['explicito']}, Numero de reproducciones: {row['num_reproducciones']}, "
                        f"Género: {row['xenero']}, Album al que pertenece: {row['cod_album']}")
                cantidad = cantidad + 1
            if(cantidad > 0):
                print(f"\nTotal de cancions que conten o álbum: {cantidad}")
            else:
                print(f"\nNon existe ningunha cáncion que pertenza a este album: {cod_alb}")

            if control_tx:
                conn.commit()
            return value
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.UNDEFINED_TABLE:
                if '"album"' in e.pgerror:
                    print("Erro: Tabla ALBUM non existe")
                else:
                    print("Erro: Tabla CANCION non existe")
            else:
                print(f"Erro xenérico: {e.pgcode}: {e.pgerror}")
            if control_tx:
                conn.rollback()
            return None
#--------------------------------------------------------------





##-------------------------------------------------------------
#-insertar una cancion
def insert_cancion(conn, control_tx=True, cod_album = None, cod_artista = None):

    if control_tx:
         conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED

    #codigo
    scod = input("Código de la Cancion: ")
    cod = None if scod=="" else int(scod)
    #titulo
    titulo = input("Título de la Cancion: ")
    if titulo=="" : titulo=None
    #duracion
    sdur = input("Duracion(segundos) de la cancion: ")
    dur = None if sdur=="" else int(sdur)
    #ano creación
    sAno = input("Año creación de la Cancion: ")
    ano = None if sAno=="" else int(scod)
    #explicito
    explicito = False
    sexp = input("Explicito? (y = yes, default = no): ")
    explicito = True if sexp=='y' else explicito
    #num_reproducciones 
    srepro = input("numero reproducciones de la Cancion: ")
    repro = None
    try:
        repro = None if srepro=="" else int(srepro)
    except:
        print("datos invalidos")
        return None
    #xenero
    genero = input("Genero (max 20 caracteres) de la cancion: ")
    if genero=="" : genero=None
    #cod_artista
    if cod_artista is None:
        scod_artista = input("Codigo de artista al que pertence: ")
        cod_artista = None if scod_artista=="" else int(scod_artista)

    sentencia_insert_song = """insert into cancion(cod_song, titulo, duracion, ano_creacion, explicito, num_reproducciones,
                        xenero, cod_album, cod_artist) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    with conn.cursor() as cur:
        try:
            cur.execute(sentencia_insert_song,(cod, titulo, dur, ano, explicito, repro, genero, cod_album, cod_artista))
            if control_tx:
                conn.commit()
                print("Canción creada correctamente.")
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.UNDEFINED_TABLE:
                print("Error: la tabla no existe.")
            elif e.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                print("Error: Ya existe una canción con este código")
            elif e.pgcode == psycopg2.errorcodes.NOT_NULL_VIOLATION:
                if '"cod_song"' in e.pgerror:
                    print("Error: El codigo de la canción es obligatorio.")
                elif '"titulo"' in e.pgerror:
                    print("Error: el titulo de la cancion es obligatorio")
                elif '"duracion"' in e.pgerror:
                    print("Error: La duracion es obligatoria")
                elif '"ano_creacion"' in e.pgerror:
                    print("Error: El año de creacion es obligatorio")
                elif '"cod_artist"' in e.pgerror:
                    print("Error: el código de artista no puede ser nulo")
            elif e.pgcode == psycopg2.errorcodes.CHECK_VIOLATION:
                print("Error: La duración debe de ser mayor que 0")
            elif e.pgcode == psycopg2.errorcodes.FOREIGN_KEY_VIOLATION:
                print("Error: Artista introducido no existe")
            else:
                print(f"Error genérico: {e.pgcode}: {e.pgerror}")
            if control_tx:
                conn.rollback()
                return
            raise 

## ------------------------------------------------------------
#- Update del estado de verificación de un artista
def update_verfication_artist(conn):
    conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ
    cod_art = show_artista(conn,False)
    if cod_art == None:
        print("No existe el artista a cambiar su estado de verificación")
        conn.commit()
        return
    pre_verificado = input("Verificado? (y = yes, n = no): ")
    if pre_verificado=='y':
        verificado = True
    elif pre_verificado=='n':
        verificado = False
    else:
        print("Error: Dato incorrecto")
        return
    
    sentencia_update_artista = """UPDATE artista set verificacion = %s where cod_art = %s"""

    with conn.cursor() as cur:
        try:
            cur.execute(sentencia_update_artista,(verificado, cod_art))
            if cur.rowcount == 0:
                print("No se ha modificado el estado de verificación.")
            else:
                print(f"Se ha modificado el estado de verficación a {verificado} del artista con codigo {cod_art}")
            conn.commit()
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.SERIALIZATION_FAILURE:
                print("Error: atributo modificado durante la operación")
            else:
                 print(f"Error genérico: {e.pgcode}: {e.pgerror}")
            conn.rollback()       

## ------------------------------------------------------------
def update_num_reproductions(conn): 
    
    conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_SERIALIZABLE
    
    cod = show_song(conn, False)

    if cod is None:
        conn.commit()
        return
    
    sinc = input("introducir incremento de reproduccións (%): ")
    inc = 0 if sinc=="" else float(sinc)

    sql = "update cancion set num_reproducciones = num_reproducciones + num_reproducciones  * %(porc)s / 100 where cod_song = %(cod)s"

    with conn.cursor() as cur:
        try:
            cur.execute(sql, {'cod': cod, 'porc': inc})
            input("pulse unha tecla")
            conn.commit()
            print("reproduccións actualizadas")
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.CHECK_VIOLATION:
                print("O prezo  debe ser positivo")
            else:
                print(f"Erro xenerico {e.pgcode}: {e.pgerror}")
            conn.rollback()

##-------------------------------------------------------------
def insert_row_artista(conn):

    # Nivel de Aislamiento
    conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED

    scod = input("Código: ")
    cod = None if scod=="" else int(scod)
    nom = input("Nome: ")
    if nom=="": nom = None
    #En la verificación no compruebo si es null porque no le dejo esa opción aunque esta parte hay que mirarla
    sverification = input("O artista está verificado non (0) si (calqueira outra tecla) : ")
    verification = False if sverification==0 else True
    sdia = int(input("Introduce o día de nacemento (duas cifras): "))
    smes = int(input("Introduce o mes de nacemento (duas cifras): "))
    sano = int(input("Introduce o ano de nacemento (catro cifras): "))
    data = None
    try:
        data = datetime.date(sano, smes, sdia)
    except:
        print("Data inválida.")
        conn.commit()
        return
    city = input("Cidade de orixe: ")
    if city=="": city = None
    

    sentencia_insert = """insert into artista(cod_art, nome, verificacion, data_nacemento, cidade_orixen)
                        values(%s, %s, %s, %s, %s)"""

    with conn.cursor() as cur:
        try:
            cur.execute(sentencia_insert,(cod, nom, verification, data, city))
            conn.commit()
            print("Artista insertado")
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.UNDEFINED_TABLE:
                print("Erro: Taboa ARTISTA non existe")
            elif e.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                if '"cod_art"' in e.pgerror:
                    print("Erro: Xa existe un artista con este código")
                else:
                    print("Erro: Xa existe un artista con este nome")
            elif e.pgcode == psycopg2.errorcodes.NOT_NULL_VIOLATION:
                if '"cod_art"' in e.pgerror:
                    print("Erro: o código de artista é obligatorio")
                elif '"nome"' in e.pgerror:
                    print("Erro: o nome de artista é  obrigatorio")
                else:
                    print("Erro: A verficación é obrigatoria")
            else:
                print(f"Erro xenérico: {e.pgcode}: {e.pgerror}")
            conn.rollback()

            
## ------------------------------------------------------------
def update_num_reproductions(conn): 
    
    conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
    ## Aquí ellos lo que hacen es llamar a ver fila y para que muestre los datos actuales al ususario y obtener el codigo del artista
    cod = show_song(conn, False)

    if cod is None:
        conn.rollback()
        return
    
    sinc = input("introducir incremento de reproduccións (%): ")
    inc = 0 if sinc=="" else float(sinc)

    sql = "update cancion set num_reproducciones = num_reproducciones + num_reproducciones  * %(porc)s / 100 where cod_song = %(cod)s"

    with conn.cursor() as cur:
        try:
            cur.execute(sql, {'cod': cod, 'porc': inc})
            input("pulse unha tecla")
            conn.commit()
            print("reproduccións actualizadas")
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.CHECK_VIOLATION:
                print("O prezo  debe ser positivo")
            else:
                print(f"Erro xenerico {e.pgcode}: {e.pgerror}")


##-------------------------------------------------------------
#- Crear un album y sus canciones
def create_album(conn):
    conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED

    #pedir datos del album
    scod_alb = input("Codigo album: ")
    cod_alb = None if scod_alb=="" else int(scod_alb)
    titulo = input("Titulo (max 50 caracteres): ")
    sano_creacion = input("Año de creación: ")
    ano_creacion = None if sano_creacion=="" else int(sano_creacion)
    scod_art = input("Codigo del artista: ")
    cod_art = None if scod_art=="" else int(scod_art)
    
    sentencia_insert_album = """insert into album(cod_alb,titulo,ano_creacion,cod_art_owner)
                                values (%(cod_alb)s, %(titulo)s, %(ano_creacion)s, %(cod_art)s)"""
    

    with conn.cursor() as cur:
        try:
            cur.execute(sentencia_insert_album,{'cod_alb':cod_alb,'titulo':titulo,'ano_creacion':ano_creacion,'cod_art':cod_art})
            snum_canciones = input("Numero de canciones del album: ")
            num_canciones = None if snum_canciones=="" else int(snum_canciones)
            for i in range(num_canciones):
                try:
                    insert_cancion(conn, False, cod_alb, cod_art)
                except:
                    print("Abortando la creación del album...")
                    conn.rollback()
                    return
            conn.commit()
            print("Album creado correctamente")
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.UNDEFINED_TABLE:
                print("Erro: Taboa ALBUM non existe")
            elif e.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                if '"cod_art"' in e.pgerror:
                    print("Error: Ya existe un album con este codigo")
                else:
                    print("Error: Ya existe un album con este titulo")
            elif e.pgcode == psycopg2.errorcodes.FOREIGN_KEY_VIOLATION:
                print("Error: el artista ingresado no existe")
            else:
                print(f"Error generico: {e.pgcode}: {e.pgerror}")
            conn.rollback()

##-------------------------------------------------------------
#-delete album
def delete_artist(conn):
    
    scod = input("Codigo del artista a borrar: ")
    cod = None if scod=="" else int(scod)

    with conn.cursor() as cur:
        try:
            cur.execute("DELETE from artista where cod_art = %s",(cod,))
            conn.commit()
            if cur.rowcount == 0:
                print(f"No se borro ningun artista con código: {cod}")
            else:
                print("Artista borrado correctamente.")
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.UNDEFINED_TABLE:
                print("Error: tabla ARTISTA no existe.")
            conn.rollback() 

## ------------------------------------------------------------
def menu(conn):
    """
    Imprime un menú de opcións, solicita a opción e executa a función asociada.
    'q' para saír.
    """
    MENU_TEXT = """
      -- MENÚ --
1 - Info de artista
2 - Info de cancion
3 - Insertar canción
4 - Actualizar estado de verificación de un artista
5 - Mostrar Album (con canciones)
6 - Insertar artista
7 - Actualizar numero de reproducciones (según datos actuales)
8 - Crear Album (con canciones)
9 - Borrar artista (se borraran todos sus albums y singles)
q - Saír   
"""
    while True:
        print(MENU_TEXT)
        tecla = input('Opción> ')
        if tecla == 'q':
            break
        elif tecla == '1':
            show_artista(conn)
        elif tecla == '2':
            show_song(conn)
        elif tecla == '3':
            insert_cancion(conn)
        elif tecla == '4':
            update_verfication_artist(conn)
        elif tecla == '5':
            show_album(conn)
        elif tecla == '6':
            insert_row_artista(conn)
        elif tecla == '7':
            update_num_reproductions(conn)
        elif tecla == '8':
            create_album(conn)
        elif tecla == '9':
            delete_artist(conn)

            
            
## ------------------------------------------------------------
def main():
    """
    Función principal. Conecta á bd e executa o menú.
    Cando sae do menú, desconecta da bd e remata o programa
    """
    print('Conectando a PosgreSQL...')
    conn = connect_db()
    print('Conectado.')
    menu(conn)
    disconnect_db(conn)

## ------------------------------------------------------
if __name__ == '__main__':
    main()