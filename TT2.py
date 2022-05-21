
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
from sqlite3 import Date, Row
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

##-------------------------------------------------------------
#-insertar una cancion
def insert_cancion(conn, control_tx=True, cod_album = None):

    if control_tx:
         conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED

    #codigo
    scod = input("Código: ")
    cod = None if scod=="" else int(scod)
    #titulo
    titulo = input("Título: ")
    if titulo=="" : titulo=None
    #duracion
    sdur = input("Duracion(segundos): ")
    dur = None if sdur=="" else int(sdur)
    #ano creación
    sAno = input("Año creación: ")
    ano = None if sAno=="" else int(scod)
    #explicito
    explicito = False
    sexp = input("Explicito? (y = yes, default = no): ")
    explicito = True if sexp=='y' else explicito
    #num_reproducciones 
    srepro = input("numero reproducciones: ")
    repro = None
    try:
        repro = None if srepro=="" else int(srepro)
    except:
        print("datos invalidos")
        return None
    #xenero
    genero = input("Genero (max 20 caracteres): ")
    if genero=="" : genero=None
    #cod_album
    scod_artista = input("Codigo de artista al que pertence: ")
    cod_artista = None if scod_artista=="" else int(scod_artista)

    sentencia_insert_song = """insert into cancion(cod_song, titulo, duracion, ano_creacion, explicito, num_reproducciones,
                        xenero, cod_album, cod_artist) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    with conn.cursor() as cur:
        try:
            cur.execute(sentencia_insert_song,(cod, titulo, dur, ano, explicito, repro, genero, cod_album, cod_artista))
            print("Canción creada correctamente.")
            if control_tx:
                conn.commit()
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

## ------------------------------------------------------------
#- Update del estado de verificación de un artista
def update_verfication_artist(conn):
    conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_REPEATABLE_READ
    cod_art = show_artista(conn,False)
    if cod_art == None:
        print("No existe el artista a cambiar su estado de verificación")
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
4 - Actuaizar estado de verificación de un artista
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