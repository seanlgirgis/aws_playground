"""
AI Agent (Bedrock + Athena)
This module acts as the "Brain".
1. It reads the database schema from Glue.
2. It sends your question + schema to Amazon Bedrock (Claude).
3. It gets a SQL query back.
4. It executes the SQL on Athena.
"""
import boto3
import time
import json

class DataAgent:
    def __init__(self, session):
        self.session = session
        self.glue = session.client('glue')
        self.athena = session.client('athena')
        # We use the 'bedrock-runtime' client to invoke models
        self.bedrock = session.client('bedrock-runtime', region_name='us-east-1')
        self.region = session.region_name

    def get_table_schema(self, db_name):
        """
        Fetches all tables and their columns to teach the AI what data we have.
        """
        schema_text = ""
        try:
            tables = self.glue.get_tables(DatabaseName=db_name)['TableList']
            for t in tables:
                table_name = t['Name']
                columns = [c['Name'] for c in t['StorageDescriptor']['Columns']]
                schema_text += f"Table: {table_name}\nColumns: {', '.join(columns)}\n\n"
        except Exception as e:
            schema_text = f"Error fetching schema: {e}"
        return schema_text

    def generate_sql(self, question, schema):
        """
        Asks Claude to convert English to Athena SQL.
        """
        print("   🧠 Thinking (Calling Bedrock)...")
        
        prompt = f"""
        You are a Data Analyst Agent. 
        You have access to an AWS Athena database with the following schema:
        
        {schema}
        
        Write a standard SQL query to answer this user question: "{question}"
        
        Rules:
        1. Return ONLY the SQL query. No explanation, no markdown.
        2. Use the database name 'edu_etl_db' if needed, e.g. "FROM edu_etl_db.tablename"
        """

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        })

        try:
            # Invoking Claude 3 Sonnet (or Haiku for speed)
            model_id = "anthropic.claude-3-sonnet-20240229-v1:0" 
            # Note: If Sonnet isn't enabled, we might need Haiku: "anthropic.claude-3-haiku-20240307-v1:0"
            
            response = self.bedrock.invoke_model(
                modelId=model_id,
                body=body
            )
            
            resp_body = json.loads(response['body'].read())
            sql = resp_body['content'][0]['text'].strip()
            
            # Cleanup: sometimes models add ```sql ... ```
            sql = sql.replace("```sql", "").replace("```", "").strip()
            return sql
            
        except Exception as e:
            print(f"❌ Bedrock Error: {e}")
            return None

    def run_query(self, sql, output_location):
        """
        Executes the SQL on Athena.
        """
        print(f"   ⚡ Executing Query: {sql}")
        try:
            # 1. Start execution
            response = self.athena.start_query_execution(
                QueryString=sql,
                ResultConfiguration={'OutputLocation': output_location}
            )
            query_id = response['QueryExecutionId']
            
            # 2. Wait for results
            while True:
                status = self.athena.get_query_execution(QueryExecutionId=query_id)
                state = status['QueryExecution']['Status']['State']
                
                if state in ['SUCCEEDED']:
                    break
                if state in ['FAILED', 'CANCELLED']:
                    print(f"❌ Query Failed: {status['QueryExecution']['Status']['StateChangeReason']}")
                    return None
                time.sleep(1)
            
            # 3. Fetch results
            results = self.athena.get_query_results(QueryExecutionId=query_id)
            return results
            
        except Exception as e:
            print(f"❌ Athena Error: {e}")
            return None

    def print_results(self, results):
        """
        Pretty prints Athena results.
        """
        if not results: return
        
        rows = results['ResultSet']['Rows']
        print("\n--- 📊 Results ---")
        for row in rows:
            data = [d.get('VarCharValue', 'NULL') for d in row['Data']]
            print(" | ".join(data))
        print("------------------\n")
