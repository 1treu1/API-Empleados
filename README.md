# Arquitectura Completa del Proyecto:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/4146a723-2871-4c25-8fcd-106556df7c34)

## Desafio #3 y #4

*#3 Implemente un proceso batch para migrar los datos a una base de datos SQL/NoSQL, o si lo desea, a un Datawarehouse o bucket analítico de un Datalake. No descarte usar la capa gratuita de algún servicio de almacenamiento tipo cloud, será considerado un plus.*

*#4 Dependiendo si escoge una base de datos SQL/NoSQL, un Datawarehouse, o un Datalake, entonces desarrolle una view/query/report a partir del modelo de datos*

Para estos puntos vamos siguiremos la siguiente arquitectura y poco a poco la irémos ampliando en los proximos desafios:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/cb9de9f1-3b3b-44ba-a3a8-c24fe06439ac)

Para implementar la solución descrita, necesitarás seguir los siguientes pasos:

1. Crear una función Lambda para generar los datos que hicimos en el [Desafio #1](https://www.notion.so/PRUEBA-T-CNICA-INGENIERIA-DE-DATOS-ClOUD-LABS-c0c66396f7764631bb307487a12a13d5?pvs=21) y guardarlos en un bucket de S3 en formato Parquet.
2. Configurar un Crawler en AWS Glue para detectar y transformar los datos Parquet en una tabla de Athena.

Entonces, primero vamos a crear una función Lambda para generar los datos y guardarlos en S3. Luego, configuraremos un Crawler en AWS Glue para detectar y transformar los datos Parquet en una tabla de Athena

**Paso 1: Crear la función Lambda para generar y guardar los datos en S3:**

- Creando Rol y añadiendo permisos
![image](https://github.com/1treu1/API-Empleados/assets/71142778/6b2f8a3b-de19-458d-b19e-45e5ea97c914)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/69a751f6-7d87-4e9e-b3b0-cec5120ad357)
- Creando Lambda
![image](https://github.com/1treu1/API-Empleados/assets/71142778/3f106c4f-84ee-4cfb-bcaf-553f96fdbb05)
Creamos un nuevo archivo llamado generar_datos.py y ponemos exactamente el mismo codigo que hicimos en el [Desafio #1](https://www.notion.so/PRUEBA-T-CNICA-INGENIERIA-DE-DATOS-ClOUD-LABS-c0c66396f7764631bb307487a12a13d5?pvs=21)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/b26d6862-d24d-4774-a082-46fe0333181c)


Ahora en lambda_funtion colocamos el codigo que hicimos en el Desafio #2 y lo modificamos un poco:

```python
import boto3
import pandas as pd
import pyarrow.parquet as pq
from io import BytesIO
from generar_datos import generar_empleados

def lambda_handler(event, context):
    # Creando el cliente de S3
    s3 = boto3.client('s3')
    
    # Nombre del archivo y el nombre del bucket de S3
    nombre_archivo = 'empleados.parquet'
    nombre_bucket = 'luis-ds-db'
    
    # Generar 10000 empleados ficticios
    empleados_generados = pd.DataFrame(generar_empleados(10000))
    # Convirtiendo el DataFrame a formato Parquet en memoria
    parquet_buffer = BytesIO()
    empleados_generados.to_parquet(parquet_buffer, index=False)
    
    # Cargando el archivo Parquet en el bucket de S3
    parquet_buffer.seek(0)
    s3.put_object(Bucket=nombre_bucket, Key=nombre_archivo, Body=parquet_buffer)
    
    print("Los datos de empleados han sido guardados exitosamente en el bucket")

    # Devolver la ubicación del archivo guardado
    ubicacion_archivo = f's3://{nombre_bucket}/{nombre_archivo}'
    return {
        'statusCode': 200,
        'body': ubicacion_archivo
    }
```

Al ejecutar la Lambda sale este error:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/bfdc3a60-91cc-44ea-9edc-5287ee8bf162)
Esto significa que no tiene las dependencias necesarias para usar las librerias que estamos llamando en nuestro codigo. Para esto añadimos algo llamado “Capas” que permite añadir las dependencias que necesitamos:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/a136067e-ddda-4a36-b33f-7cf10b371e9b)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/d683559c-04ce-4076-909f-081c99a253a4)

Ahora vamos a crear una capa customizada para Faker:

```bash
mkdir python
pip3 install -t python/ Faker
zip -r libraries.zip python/
```
- Vamos a Lambda/Layers y creamos una capa:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/10739add-01ad-4bea-a855-3e58f3574d73)
- Subimos el archivo libraries.zip donde se encuentra nuestra libreria
![image](https://github.com/1treu1/API-Empleados/assets/71142778/8019f457-1347-4ea5-981e-4c20bf7b2be5)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/44db2e56-e2d4-425d-a647-36983d8ac1d7)
- Volvemos a nuestra funcion Lambda y añadimos la capa usando la opcion Custom layers:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/55493ed1-96ca-4188-a1b6-37be0ef01fa4)
Ejecutamos:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/62e78dde-7ced-4ade-af27-35dcf0b16b68)
- Cargado:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/c692bf7e-2d11-434e-8c4c-2d675b2167f1)
Ahora vamos a crear el Crawler para convertir este archivo en una tabla y psoteriormente pueda ser consultada y visualizada en Athena.

- Creando DataBase: Ingresamos a AWS Glue/Databases:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/59478fb5-6ab5-48bf-909a-ddb9a561d50a)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/88117da1-0681-4109-9576-9af87e505838)
- **Creando Rol:** Vamos a IAM/Roles para nuestro Crawler:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/accd5d80-1868-4149-b0b9-ab7d29a58a19)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/2da7c71b-6370-45aa-8ff0-ff3416400d34)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/17de2b2f-fd2c-427c-898c-aeb2facb821a)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/cfbad945-1436-45bc-b2c7-d8665ad607ae)
- Nombrando el rol:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/09292f04-98f0-4322-92dd-a5eb2d85c8d2)
- Crear:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/dd4e5189-2df4-49d2-adfb-e67df2616531)
- Creando Crawler: Nos vamos a Glue/Crawlers, opcion crear crawler:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/a007c9db-3cc1-4913-a4de-f1eaf04f74a2)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/8589da16-29d3-45b4-8dda-28c4f7c4ca33)
- Seleccionamos el bucket donde esta nuestro archivo y añadimos la fuente:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/ce38d967-2297-4fc1-b44a-a31552014ddc)
- Y damos click en next:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/5a9fe7e2-af8d-4af6-bcd4-75c17895bd7c)
- Seleccionamos el rol que creamos anteriormente:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/07d9ac61-184c-459a-9c75-765548d35e50)
- Seleccionamos la base de datos que creamos anterirormente:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/8edef6f6-cd42-41af-a162-5c5cf5c94e12)
- Creando Crawler:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/d9b0a300-f7fd-43ad-b1e5-d6c505fb0b4e)
- Corriendo Crawler:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/a32bbb2f-3136-4643-80a6-190946169ded)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/afb8cb1e-9c40-4465-8836-eee79bc6d539)
- Ahora, para visualizar la informacion en AWS Athena debemos darle permisos a Athena para que pueda visualizar la información. Debemos darle dos tipos de permisos. Uno a nuestro Rol `rol_dev_glue` y otro a nuestro usuario IAM
- Vamos a AWS Lake Formation/Data Lake Permissions y damos click en Grant
- Añadiendo permisos de Lake Formation a `rol_dev_glue`
![image](https://github.com/1treu1/API-Empleados/assets/71142778/4783b2ee-4952-4a72-9849-d778c3147d4f)
- Seleccionamos lo siguiente:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/b7e150ca-ef11-4d2c-b21e-678dc7959b85)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/1f041d94-002b-4dda-acd6-b201eeaa7b51)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/188beaae-4ba9-4bab-85a2-829cceb46aba)
- Repetimos los mismos pasos pero esta vez agregamos las tablas:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/97500d51-d207-4edf-867b-c5eb5d542ac8)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/8e749c86-c313-4155-a98b-f0b1523b6ae6)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/bb99fbbe-35f9-476e-95ab-c1520f76d2fd)
- Repetimos los mismos pasos, pero esta vez escogemos el usuario de la cuenta:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/7c509c21-9f08-471c-a3d7-bae0d1a12add)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/17bac52b-c236-4bc0-abba-ead54d3dc6f2)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/7a0094da-c253-4d34-bc49-49110b1f94dd)
- Repetimos lo mismo pero agregando las tablas:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/8e36e731-92ef-40b1-87c0-a44dbfb8188a)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/97714aaf-e297-48bd-a5d9-5ea457ad4883)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/d669637f-3197-4ac5-9294-daf742651255)
- Ahora vamos a visualizar la información en AWS Athena:

```sql
-- Esta es nuestra consulta:
select * from empleados_db
```
![image](https://github.com/1treu1/API-Empleados/assets/71142778/b8e59fa2-7a29-424c-9447-dad6f2fae2a4)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/a19ef320-4a26-4fab-a08a-c513ef444fa7)
- Por ultimo, vamos a crear un Step Funtion para automatizar todo el proceso:
- Vamos a Step Funtion/State Machine:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/08ce56d6-53ba-4b23-8ee2-a1a42782ece8)
- **Paso 1 Configurando Lambda:**
![image](https://github.com/1treu1/API-Empleados/assets/71142778/e7f38b90-d1da-4f1a-9968-f6316562f1c9)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/2621af3a-e300-4e54-a6d8-ce1d354c124e)
- **Paso 2 Configurando Crawler:**
![image](https://github.com/1treu1/API-Empleados/assets/71142778/a07099d9-5ed5-4cce-ba62-c11c53fa5950)


- **Paso 3 Ejecutar:**
![image](https://github.com/1treu1/API-Empleados/assets/71142778/0e2e1152-029c-4e23-bdd3-983114efd8a7)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/e9f09de5-757c-4b8b-9d7d-571111f59f1f)

## Desafio #5 y #6

Para estos dos puntos vamos a crear una API con **GCP Cloud Run**, que se conecte a **AWS Athena** y haga las consultas a `empleados_db` . Pero primero vamos a crear las credenciales en **AWS Athena** para poder acceder externamente:

- Buscar en la consola de AWS IAM/Usuarios y seguir los pasos:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/34e7cc75-083a-49c4-9650-79e8776eb370)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/7e528a97-b17c-4414-91b0-e3593870513f)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/69ea3254-e7a6-4fe8-941a-3f622d47f558)
- Seleccionamos las siguientes politicas:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/e78e745e-3150-412d-9099-c8476fd3f098)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/45136f6b-97bc-4861-833a-3fde4830a70b)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/3e29d193-bfbc-4bb3-b8e0-c4bccad9986b)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/cee128b6-c193-48f4-ac95-f87dc90a6a4b)
- Creando clave de acceso:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/b1ee78ce-5fe3-408d-ac4f-1dc5f1414fe6)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/608ac144-02ac-4722-b8af-3b81b57ec1b1)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/c614ded7-b1a0-4985-bc84-f54fb139f01f)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/7a37b1ec-62d9-4b84-a22f-423b16d1672e)
- Ahora tenemos que darle permisos de Lake Formation al nuevo usuario `Luis-DS-API-User` para que pueda hacer consultas en Athena.
    
    Vamos a [AWS Lake Formation](https://us-east-1.console.aws.amazon.com/lakeformation/home?region=us-east-1#firstRun)/Data lake permissions, y seguimos los pasos:
    ![image](https://github.com/1treu1/API-Empleados/assets/71142778/efadf64a-215a-4228-966b-839425db87c7)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/95e477a8-e084-4159-8ee5-e44aab7078fa)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/9639e4ed-30ac-4bcc-bde2-f01882773182)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/79f2b0b1-3c2f-4bfd-be33-37c01c8d80e4)
- Haremos nuevamente los mismos pero incluyendo las tablas:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/abc8a41c-5c79-4edb-8b38-0b15423752c2)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/8636678b-5ce7-470d-b8a0-9dc4a64c2351)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/474afba4-4c86-40f2-b33c-ed25b8775499)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/a9286e8a-2695-436e-b3b4-52e4096fe976)

**Ejecutando Localmente la API:**

```bash
git clone https://github.com/1treu1/API-Empleados.git
cd API-Empleados
python3 -m venv API
source API/bin/activate
pip install -r requirement.txt
```

- Agregar credenciales en main.py en las lineas 7 y 8
![image](https://github.com/1treu1/API-Empleados/assets/71142778/f33b22bd-486f-4fec-8a79-5f1a702ead98)

```json
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

- Ingresamos a esta URL:

http://127.0.0.1:8000/docs#/default/ejecutar_consulta_consulta__post

- Seguimos los siguientes pasos:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/8c074260-1e23-4f89-9600-724c33abb725)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/bee6b3bf-fecc-4be4-9955-602a9062d546)
- Respuesta de la API:

```json
[
  {
    "nombre": "Juanita Escalona Parejo",
    "departamento": "Caquetá",
    "puesto_de_trabajo": "Gerente",
    "salario": "8220576",
    "email": "chaparroamaro@example.com",
    "teléfono": "+34 886 42 96 81",
    "dirección": "Urbanización Macario Álvarez 88 Puerta 6 \nSanta Cruz de Tenerife, 13159",
    "__index_level_0__": "0"
  }
]
```

**Ejecutando contenedor en GCP Cloud Run:**

Ingresamos a la consola de GCP y buscamos Cloud Run. Y seguimos los siguiente pasos:
![image](https://github.com/1treu1/API-Empleados/assets/71142778/1417a43c-800a-41ba-8614-6b4c0fa6ba3a)
```bash
# URL del Contenedor
11treu11/api-empleados:v1
```
![image](https://github.com/1treu1/API-Empleados/assets/71142778/d2b20c30-7252-472b-a3d0-2a8b1cae19ca)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/f00ed91d-e30a-4a94-a27a-8c2c46f8a4fb)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/1b3374e9-8a8b-49a5-a9dd-ebac4c52c61d)


- API desplegada (Si quieres probar la API ingresa al siguiente link y sigue los pasos):

[Reporte Empleados API - Swagger UI](https://api-empleados-a7ngfzyxxq-uc.a.run.app/docs#/default/ejecutar_consulta_consulta__post)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/bc2414fc-19a2-45ad-8cdb-891ef6937062)
![image](https://github.com/1treu1/API-Empleados/assets/71142778/28b0397d-efe2-4734-8227-56601c2641e6)

**Respuesta de la API:**

```json
[
  {
    "nombre": "Juanita Escalona Parejo",
    "departamento": "Caquetá",
    "puesto_de_trabajo": "Gerente",
    "salario": "8220576",
    "email": "chaparroamaro@example.com",
    "teléfono": "+34 886 42 96 81",
    "dirección": "Urbanización Macario Álvarez 88 Puerta 6 \nSanta Cruz de Tenerife, 13159",
    "__index_level_0__": "0"
  }
]
```
Documentacion mas detallada: https://axiomatic-ticket-4ff.notion.site/PRUEBA-T-CNICA-INGENIERIA-DE-DATOS-ClOUD-LABS-c0c66396f7764631bb307487a12a13d5?pvs=4
Muchas gracias por la oportunidad, un abrazo.
