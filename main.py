from fastapi import FastAPI, HTTPException
import boto3
import time
import pandas as pd



# Crea una instancia de FastAPI
app = FastAPI(title="Reporte Empleados API", description="Esta API proporciona un servicio para ejecutar consultas en AWS Athena sobre una base de datos de empleados. A continuación se muestran algunos ejemplos de consultas posibles:",
               version="1.0")

# Crea un cliente de Athena
athena_client = boto3.client('athena', 
                             aws_access_key_id=aws_access_key_id, 
                             aws_secret_access_key=aws_secret_access_key, 
                             region_name=region_name)

@app.post("/consulta/")
async def ejecutar_consulta(query: str = "SELECT * FROM empleados_db LIMIT 10"):
    
    """
    Ejecuta una consulta en AWS Athena sobre una base de datos de empleados.
    
    Ejemplos de consultas posibles:
    
    1. SELECT * FROM empleados_db LIMIT 10
    2. SELECT nombre, puesto_de_trabajo, salario FROM empleados_db WHERE departamento = 'Cundinamarca'
    3. SELECT nombre, puesto_de_trabajo, salario FROM empleados_db WHERE salario > 5000000
    4. SELECT COUNT(*) AS total_empleados FROM empleados_db
    5. SELECT departamento, AVG(salario) AS salario_promedio FROM empleados_db GROUP BY departamento
    """
    
    # Ejecuta una consulta en Athena
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': 'luis-ds-database-db'
        },
        ResultConfiguration={
            'OutputLocation': 's3://devfanorg-datalake-dev-us-east-1-776444291528-athena/'
        }
    )

    # Obtiene el ID de ejecución de la consulta
    query_execution_id = response['QueryExecutionId']

    # Espera hasta que la consulta se complete
    while True:
        query_status = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        state = query_status['QueryExecution']['Status']['State']
        if state == 'SUCCEEDED':
            break
        elif state in ['FAILED', 'CANCELLED']:
            raise HTTPException(status_code=500, detail=f"La consulta ha fallado o ha sido cancelada: {state}")
        time.sleep(2)  # Espera 5 segundos antes de volver a verificar el estado

    # Obtiene los resultados de la consulta
    query_results = athena_client.get_query_results(QueryExecutionId=query_execution_id)

    results = query_results['ResultSet']['Rows']
    df = pd.DataFrame([row['VarCharValue'] for row in data['Data']] for data in results)

    # Establecer la primera fila como nombres de columna
    df.columns = df.iloc[0]
    df = df[1:]
    dict_data = df.to_dict(orient='records')
    
    return dict_data