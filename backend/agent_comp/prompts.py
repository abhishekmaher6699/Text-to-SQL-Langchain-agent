from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser



table_info_query = ChatPromptTemplate.from_template(
    """
    You are an SQL expert at getting table info from a database. You are given a table name. Write a SQL query to get the table info and schema of the given table name. 
    Table Name: {table_name} 
"""
)

question_contruction_prompt = ChatPromptTemplate.from_messages(
    [
        ('system', """Refine the query using the provided question and message history to ensure it is context-aware and clear for text-to-SQL translation. 
        Incorporate relevant context only if it enhances understanding or accuracy; otherwise, keep the query independent and concise. Return only the refined query in a clear and effective format. 
        The new question should be info from history if possible to get the best results during data extraction."""),
        ('human', "Current Question: {question}, Message History: {history}"),
    ]
)

query_prompt_template = ChatPromptTemplate.from_template(
    """
    Given an input question, create a syntactically correct {dialect} query to run to help find the answer. Unless the user specifies in his question a specific number of examples they wish to obtain, always limit your query to at most {top_k} results. You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.
    Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.
    Remember that this query will be used for fetching data that will be USED FOR DATA VISUALIZATION. So give appropriate query.
    Use `` for column names if there is a space in it. Make a working relevant query.
    The queries should always return as concise and accurate results as possible. Make sure the query is syntactically correct and logically sound. Dont return unnecessary clutter.
    Only use the following tables for checking the column names and schema:
    TABLE NAME: {table_name}
    TABLE_INFO: {table_info}. USE THIS

    Question: {input}

    You can use the additional context if available. This context can give you some important regarding query construction. make sure to use it if it aligns with your use case
    Additional Context: {context}

    """
)

breakdown_prompt = ChatPromptTemplate.from_messages([
    ('system', """
        You are an expert Text-to-SQL assistant. Your task is to analyze a user's query in the context of a provided table schema and determine the best approach to retrieve accurate and relevant results.
        Follow these steps:
        1. Understand the user's query and its intent.
        2. Evaluate the provided table
        3. Breakdown the user query into subqueries in such a way that answering one will provide input to the next suquestion and we reach a final subquestion which is the main question of the user. The user will then answer this question suquencially and pass the answer of each question to the next as context so we a get a proper answer at last.
        Ensure your analysis is logical and helps optimize the data retrieval process. There should be at maximum 5 subquestions.
        Keep in minf that these questions will be used to to generate sql queries. So give proper questions that can be transformed into queries
    """),
    ('user', "User Query: {question}\nTable Schema: {table_info}")
])

analysis_prompt = ChatPromptTemplate.from_messages([
    ('system', """
        You are an expert Text-to-SQL assistant. Your task is to analyze a user's query in the context of a provided table schema and determine the best approach to retrieve accurate and relevant results.
        Follow these steps:
        1. Understand the user's query and its intent.
        2. Evaluate the provided table schema to confirm whether the query can be answered with a single SQL query or if it needs to be broken down into multiple subqueries which can provide overall better results if the question requires complex queries.
        Ensure your analysis is logical and helps optimize the data retrieval process.
    """),
    ('user', "User Query: {question}\nTable Schema: {table_info}")
])

query_validation_prompt = ChatPromptTemplate.from_messages([
    ('system', """You are a SQL expert and validator. Your task is to evaluate the provided SQL query for syntactic correctness, logical accuracy, and alignment with the user's question.
                  Based on the given table schema, ensure that the query adheres to SQL syntax rules and retrieves data accurately to answer the question.
                  If the query is invalid or inappropriate, provide corrections or suggestions for improvement."""),
    ('user', "Question: {question}, Query: {query}, Table info: {table}")
])

fix_query_prompt_template = ChatPromptTemplate.from_template(
    """
    The given sql query was generated by an AI for answering user question. However, it has some issues. Figure out the issues and fix them. Here are some suggestions on how to fix it:
    {suggestions}
    The queries should always return as concise and accurate results as possible. Make sure the query is syntactically correct and logically sound. Dont return unnecessary clutter.

    Query: {query}

    Additional info:
    table_info: {table_info}
    User question: {input}
    """
)

data_val_prompt = ChatPromptTemplate.from_template(
    """
        You are given some data fetched from a database using a query. Check the data if it exists. If there is some error or some important valuesare null, suggest ways to fix it.
        Data: {data}, Query: {query}, table info: {table_info}, User question: {question}
    """
)

llm_prompt = ChatPromptTemplate.from_messages([
    ('system', """
        You are an expert assistant for answering user questions with data retrieved from a database. 
        The user provides a question, a SQL query, the data fetched using the query, and additional context if applicable.
        
        Your responsibilities:
        1. Use the provided data and context to answer the question accurately and concisely.
        2. Avoid including large lists of values in your response. If the data contains more than 10-15 items, summarize it instead (e.g., "The values are in the provided data").
        3. If the data does not fully answer the question, indicate that and encourage checking the data or query for completeness.
        
        Your focus is on clarity and precision without overloading the response with unnecessary details.
    """),
    ('user', "Question: {question}, SQL Query: {query}, Data: {data}, Additional Context: {context}")
])

final_llm_prompt = ChatPromptTemplate.from_messages([
    ('system', """ You are an expert at answering users question. User has given a question and some context. Use the context to answer the question. The context includes subquestions generated from the users questiona nd answers to them and the data used to answer those question.
    Now you have all those, use it to produce a relevant answer."""),
    ('user', "question: {question}, context: {context}")
])


