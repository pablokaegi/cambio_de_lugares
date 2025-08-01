import sqlite3
import pandas as pd

DB_PATH = 'registro_votos.db'

def exportar_excel():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query('SELECT * FROM preferencias', conn)
    df.to_excel('preferencias_export.xlsx', index=False)
    print('Exportado a preferencias_export.xlsx')
    conn.close()

def mostrar_tabla():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query('SELECT * FROM preferencias', conn)
    print(df)
    conn.close()

if __name__ == "__main__":
    print("1. Mostrar tabla en consola")
    print("2. Exportar a Excel")
    op = input("Opción: ")
    if op == "1":
        mostrar_tabla()
    elif op == "2":
        exportar_excel()
    else:
        print("Opción no válida.")
