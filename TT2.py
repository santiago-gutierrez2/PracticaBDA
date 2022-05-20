
#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# TT2.py: 
# Práctica de python
#
# Autor: Adrián Castro Rodríguez (adrian.castro2@udc.es) Santiago Gutierrez Gomez (santiago.gutierrez@udc.es)
# Data de creación: 2-05-2021
#
from sqlite3 import Date, Row
import sys
import psycopg2
import psycopg2.extras
import psycopg2.errorcodes
import psycopg2.extensions


## ------------------------------------------------------------
def connect_db():
    try:
        con=psycopg2.connect(host='localhost',
                        user='adrian',
                        password='axe',
                        dbname='adrian')
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
    try:
        cod_song = int(input("Código canción: "))
    except:
        print("Error: datos invalidos")
        return None
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        try:
            cur.execute("Select cod_song, titulo, duracion, ano_creacion, explicito, num_reproducciones, xenero, cod_album from cancion where cod_song=%(cod_song)s",{'cod_song': cod_song})
            row=cur.fetchone()
            value=None
            if row:
                print(f"Título: {row['titulo']}, Duración(seg): {row['duracion']}, Año creación: {row['ano_creacion']}, "
                        f"Explícito: {row['explicito']}, Numero de reproducciones: {row['num_reproducciones']}, "
                        f"Género: {row['xenero']}, Album al que pertenece: {row['cod_album']}")
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
                print(f"No existe ningún álbum por este código: {cod_alb}")


            cur.execute("Select cod_song, titulo, duracion, ano_creacion, explicito, num_reproducciones, xenero, cod_album from cancion where cod_album=%(cod_alb)s",{'cod_alb': cod_alb})
            records=cur.fetchall()
            cantidad = 0
            for row in records:
                print(f"Título: {row['titulo']}, Duración(seg): {row['duracion']}, Año creación: {row['ano_creacion']}, "
                        f"Explícito: {row['explicito']}, Numero de reproducciones: {row['num_reproducciones']}, "
                        f"Género: {row['xenero']}, Album al que pertenece: {row['cod_album']}")
                cantidad = cantidad + 1
            if(cantidad > 0):
                print(f"Total de canciones que contiene le álbum: {cantidad}")
            else:
                print(f"No existe ninguna cáncion que pertenezca a este album: {cod_alb}")

            if control_tx:
                conn.commit()
            return value
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.UNDEFINED_TABLE:
                print("Error: Tabla ALBUM no existe")
            else:
                print(f"Error genérico: {e.pgcode}: {e.pgerror}")
            if control_tx:
                conn.rollback()
            return None
#--------------------------------------------------------------





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
    sdata = input("Data de nacemento: ")
    data = None if sdata == "" else Date(sdata)
    city = input("Cidade de orixen: ")
    if city=="": city = None
    

    sentencia_insert = """insert into artista(codart, nome, verification, data_nacemento, cidade_orixen)
                        values(%s, %s, %s, %s, %s)"""

    with conn.cursor() as cur:
        try:
            cur.execute(sentencia_insert,(cod, nom, verification, data, city))
            conn.commit()
            print("Artista insertado")
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.UNDEFINED_TABLE:
                print("Erro: Taboa non existe")
            elif e.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                print("Erro: Xa existe un artista con este codigo")
            elif e.pgcode == psycopg2.errorcodes.NOT_NULL_VIOLATION:
                if '"codart"' in e.pgerror:
                    print("Erro: o código de artista é obligatorio")
                else:
                    print("Erro: o nome de artista é  obrigatorio")
            else:
                print(f"Erro xenérico: {e.pgcode}: {e.pgerror}")
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
3 - Info del album
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
            show_album(conn)


            
            
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