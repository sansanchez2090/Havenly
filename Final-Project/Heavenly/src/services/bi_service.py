import os
import psycopg2
from dotenv import load_dotenv
from typing import Optional

load_dotenv()


BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
SQL_DIR = os.path.join(BASE_DIR, 'scripts')

POPULATE_SQL = os.path.join(SQL_DIR, 'dw_populate.sql')

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5434") 
DB_NAME = os.getenv("DB_NAME", "heavenly")
DB_USER = os.getenv("DB_USER", "heavenly")
DB_PASSWORD = os.getenv("DB_PASSWORD", "12345")


def get_db_connection() -> Optional[psycopg2.connect]:
    """Establece la conexión a la base de datos Citus Coordinator."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print(f"INFO: Conexión exitosa a {DB_HOST}:{DB_PORT}/{DB_NAME}")
        return conn
    except Exception as e:
        print(f"ERROR: No se pudo conectar a la base de datos. Verifique DB_HOST/DB_PORT. Detalle: {e}")
        return None

def execute_sql_file(conn: psycopg2.connect, file_path: str) -> bool:
    """Lee y ejecuta el contenido de un archivo SQL."""
    if not os.path.exists(file_path):
        print(f"ERROR: Archivo SQL no encontrado en la ruta: {file_path}")
        return False
    
    cursor = conn.cursor()
    cursor.execute("SET citus.enable_repartition_joins TO on;")
    conn.commit()
    print("INFO: Citus repartition joins habilitado para la sesión.")

    try:
        with open(file_path, 'r') as f:
            sql_script = f.read()
        
        cursor = conn.cursor()
        # psycopg2 ejecuta múltiples sentencias SQL en un solo script
        cursor.execute(sql_script) 
        conn.commit()
        print(f"SUCCESS: Script {os.path.basename(file_path)} ejecutado y cambios confirmados.")
        return True
    except psycopg2.Error as e:
        conn.rollback()
        print(f"ERROR al ejecutar el script {os.path.basename(file_path)}.")
        print(f"Detalle del error: {e}")
        return False
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()

def run_bi_etl():
    """Ejecuta el proceso completo de Extracción, Carga y Transformación (ELT)."""
    print("\n--- INICIANDO PROCESO BI/ELT PARA HEAVENLY ---")
    
    conn = get_db_connection()
    if conn is None:
        return

    # 1. Ejecutar la lógica de Carga Incremental (ELT)
    # Esto incluye la carga de fact_booking y la población de dim_date.
    if execute_sql_file(conn, POPULATE_SQL):
        
        # 2. Refrescar la Vista Materializada (KPIs)
        # Se ejecuta el REFRESH solo si la carga de datos fue exitosa.
        REFRESH_KPI_SQL = "REFRESH MATERIALIZED VIEW vm_regional_kpis"
        try:
            cursor = conn.cursor()
            print("\n--- REFRESCANDO VISTA MATERIALIZADA (KPIs) ---")
            
            # Usamos CONCURRENTLY para permitir consultas mientras se actualiza la vista,
            # pero requiere un índice único (que ya creamos).
            cursor.execute(REFRESH_KPI_SQL) # + " CONCURRENTLY"
            conn.commit()
            print("SUCCESS: Vistas Materializadas actualizadas (vm_regional_kpis).")
        except psycopg2.Error as e:
            conn.rollback()
            print(f"ERROR al refrescar la vista. Verifique que el índice único exista. Detalle: {e}")
        finally:
            cursor.close()
            
    conn.close()
    print("--- PROCESO BI/ELT FINALIZADO ---")

# Si ejecutas este script directamente:
if __name__ == "__main__":
    # Asegúrate de ejecutar 'poetry install' antes de ejecutar este script
    run_bi_etl()