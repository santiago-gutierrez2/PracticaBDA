#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# exerbda.py: 
# Programa python para completar seguindo o boletín de exercicios de BDA.
#
# Autor: Miguel Rodríguez Penabad (miguel.penabad@udc.es)
# Data de creación: 19-01-2021
#
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
                        user='santi',
                        password='destino123',
                        dbname='santi')
        return con
    except psycopg2.OperationalError as e:
        print(f"Error conectando: {e}")
        sys.exit(1)
    


## ------------------------------------------------------------
def disconnect_db(conn):
    conn.commit()
    conn.close()


## ------------------------------------------------------------
def create_table(conn):
    """
    Crea a táboa artigo (codart, nomart, prezoart)
    :param conn: a conexión aberta á bd
    :return: Nada
    """
    with conn.cursor() as cur:
        try:
            sentencia_create = """create table artigo(codart int constraint pk_artigo primary key,
                                                nomart varchar(30) not null,
                                                prezoart numeric(5,2) constraint c_prezopos check (prezoart > 0))"""
            cur.execute(sentencia_create)
            conn.commit()
            print("Taboa artigo creada")
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.DUPLICATE_TABLE:
                print("taboa xa existe")
            else:
                print(f"Erro xenérico {e.pgcode}; {e.pgerror}")
            conn.rollback()
        
## ------------------------------------------------------------
def drop_table_artigo(conn):
    sentencia_drop = """Drop table artigo"""
    with conn.cursor() as cur:
        try:
            cur.execute(sentencia_drop)
            conn.commit()
            print("taboa eliminada")
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.UNDEFINED_TABLE:
                print("taboa non existe")
            else:
                print(f"Erro xenerico: {e.pgcode}; {e.pgerror}")
            conn.rollback()

## ------------------------------------------------------------
def insert_row_artigo(conn):

    # Nivel de Aislamiento
    conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED

    scod = input("Código: ")
    cod = None if scod=="" else int(scod)
    nom = input("Nome: ")
    if nom=="": nom = None
    sprezo = input("Prezo: ")
    prezo = None if sprezo == "" else float(sprezo)

    sentencia_insert = """insert into artigo(codart, nomart, prezoart)
                        values(%s, %s, %s)"""

    with conn.cursor() as cur:
        try:
            cur.execute(sentencia_insert,(cod, nom, prezo))
            conn.commit()
            print("Artigo insertado")
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.UNDEFINED_TABLE:
                print("Erro: Taboa non existe")
            elif e.pgcode == psycopg2.errorcodes.UNIQUE_VIOLATION:
                print("Erro: Xa existe un artigo con este codigo")
            elif e.pgcode == psycopg2.errorcodes.NOT_NULL_VIOLATION:
                if '"codart"' in e.pgerror:
                    print("Erro: o código de artigo é obligatorio")
                else:
                    print("Erro: o nome de artigo é  obrigatorio")
            elif e.pgcode == psycopg2.errorcodes.CHECK_VIOLATION:
                print("ERRO: o prezo debe ser positivo.")
            else:
                print(f"Erro xenérico: {e.pgcode}: {e.pgerror}")
            conn.rollback()

## ------------------------------------------------------------
def show_row(conn, control_tx=True): #exercicio 19 e 16
    #devolver None

    if control_tx:
        conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
    else:
        conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_DEFAULT

    scod = input("Codigo do artigo: ")
    cod = None if scod =="" else int(scod)

    sentencia_select = """select nomart, prezoart from artigo where codart=%s"""

    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        try:
            cur.execute(sentencia_select,(cod,))
            row = cur.fetchone()
            retval=None 
            conn.commit()
            if row:
                retval= cod
                prezo = row['prezoart'] if row['prezoart'] else "Descoñecido"
                print(f"Codigo: {cod}; Nome: {row['nomart']}; Prezo: {prezo}")
            else:
                print("O artigo non existe")
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
def update_price(conn): #exercicio 21, 22 e 23
    
    conn.isolation_level = psycopg2.extensions.ISOLATION_LEVEL_READ_COMMITTED
    
    cod = show_row(conn, False)

    if cod is None:
        conn.rollback()
        return
    
    sinc = input("introducir incremento de prezo (%): ")
    inc = 0 if sinc=="" else float(sinc)

    sql = "update artigo set prezoart = prezoart + prezoart * %(porc)s / 100 where codart = %(cod)s"

    with conn.cursor() as cur:
        try:
            cur.execute(sql, {'cod': cod, 'porc': inc})
            input("pulse una tecla")
            conn.commit()
            print("Prexo actualizado")
        except psycopg2.Error as e:
            if e.pgcode == psycopg2.errorcodes.CHECK_VIOLATION:
                print("O prezo  debe ser positivo")
            else:
                print(f"Erro xenerico {e.pgcode}: {e.pgerror}")


    


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

## ------------------------------------------------------------

if __name__ == '__main__':
    main()
