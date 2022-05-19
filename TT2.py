
#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# TT2.py: 
# Práctica de python
#
# Autor: Adrián Castro Rodríguez (adrian.castro2@udc.es) Santiago Gutierrez Gomez (santiago.gutierrez@udc.es)
# Data de creación: 2-05-2021
#
from sqlite3 import Date
import sys
from turtle import update
from webbrowser import get
import psycopg2
import psycopg2.extras
import psycopg2.errorcodes
import psycopg2.extensions


## ------------------------------------------------------------
def connect_db():
    try:
        con=psycopg2.connect(host='localhost',
                        user='user1',
                        password='1234',
                        dbname='user1')
        return con
    except psycopg2.OperationalError as e:
        print(f"Error conectando: {e}")
        sys.exit(1)
    


## ------------------------------------------------------------
def disconnect_db(conn):
    conn.commit()
    conn.close()


## ------------------------------------------------------------
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
def show_row_Artista(conn, control_tx=True):
    #devolver None

    if control_tx:
        conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
    else:
        conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_DEFAULT

    scod = input("Codigo de artista: ")
    cod = None if scod =="" else int(scod)

    sentencia_select = """select nome, verification, data_nacemento, cidade_orixen from artista where codart=%s"""

    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        try:
            cur.execute(sentencia_select,(cod))
            row = cur.fetchone()
            retval=None 
            conn.commit()
            if row:
                retval= cod
                nomart = row['nome']
                verification = row['verification']  #En este caso al ser not null creo que no hace falta comprobar nada más
                data_nac = row['data_nacemento'] if row['data_nacemento'] else "Descoñecido"
                cidade =  row['cidade_orixen'] if row['cidade_orixen'] else "Descoñecida"
                print(f"Codigo: {cod}; Nome: {nomart}; verificación: {verification}; Data de nacemento: {data_nac}; Cidade: {cidade} ")
            else:
                print("O artista non existe")
            if control_tx:
                conn.commit()
            return retval
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.UNDEFINED_TABLE:
                print("Erro: Taboa non existe")
            else:
                print(f"Erro xenérico: {e.pgcode}: {e.pgerror}")
            if control_tx:
                conn.rollback()
            return None


    


## ------------------------------------------------------------
def menu(conn):
    """
    Imprime un menú de opcións, solicita a opción e executa a función asociada.
    'q' para saír.
    """
    MENU_TEXT = """
      -- MENÚ --
1 - Crear táboa artigo
2 - Eliminar taboa artigo 
3 - Insert en artigo  
4 - Mostrar informacion dun artigo
5 - Actualizar prezo do artigo
q - Saír   
"""
    while True:
        print(MENU_TEXT)
        tecla = input('Opción> ')
        if tecla == 'q':
            break
        elif tecla == '1':
            create_table(conn)
        elif tecla == '2':
            drop_table_artigo(conn) 
        elif tecla == '3':
            insert_row_artigo(conn)
        elif tecla == '4':
            show_row(conn)
        elif tecla == '5':
            update_price()

            
            
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