from langchain_core.output_parsers import StrOutputParser
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage, HumanMessage
from typing_extensions import TypedDict, Annotated, Dict
import ast
import time

from backend.main import model, db, dialect

from backend.agent_comp.prompts import *

from backend.agent_comp.output_models import *

class State(TypedDict):
    messages: Annotated[list, add_messages]
    question: str
    query: str
    result: str
    answer: str
    code: str
    breakdown: str
    subquestion: list
    context: Dict
    isValid: str
    suggestions: str
    ValidData: str
    table_name: str
    table_info: str
    table_query: str



def get_table_info(state):
    """Get table info from the database."""
    print("--GETTING TABLE INFO--")
    table_name = state["table_name"]

    prompt = table_info_query.invoke({"table_name": table_name})

    structured_llm = model.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt.messages[0].content)

    return {"table_query": result.query, "table_name": table_name}
 
def question_construction(state):
    print("--CONSTRUCTING QUESTION--")

    messages = state['messages']
    print(state['table_info'])
    ques = messages[-1]

    if len(messages) > 10:
        history = messages[-10:-1]
    else:
        history = messages[:-1]
        
    prompt = question_contruction_prompt.invoke({"question": ques, "history": history})

    chain = model | StrOutputParser()
    out = chain.invoke(prompt)
    return {"question": out}

def write_query(state):
    """Generate SQL query to fetch information."""
    print("--GENERATING QUERY--")

    prompt = query_prompt_template.invoke(
        {
            "dialect": dialect,
            "top_k": 100,
            "table_info": state["table_info"],
            "input": state["question"],
            "table_name": state["table_name"],
            "context": state["context"]
        }
    )
    structured_llm = model.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt.messages[0].content)
    return {"query": result.query}

def validate_query(state: State):

    """Validate SQL query."""
    print("--VALIDATING QUERY--")

    prompt = query_validation_prompt.invoke(
        {
            "question": state["question"],
            "query": state["query"],
            "table": state["table_info"],
            "table_name": state["table_name"]
        })

    llm = model.with_structured_output(QueryValidation)
    result = llm.invoke(prompt)
    print(result.suggestions)
    return {"isValid": result.isValid, "suggestions": result.suggestions}

def rewrite_query(state: State):
    """Generate SQL query to fetch information."""
    print("--REWRITING QUERY--")

    prompt = fix_query_prompt_template.invoke(
        {
            "table_info": state["table_info"],
            "input": state["question"],
            "suggestions": state["suggestions"],
            "query": state["query"]
            # "context": state["context"]
        }
    )
    structured_llm = model.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt.messages[0].content)
    return {"query": result.query}

def execute_table_query(state: State):
    """Execute SQL query."""
    print("--EXECUTING TABLE QUERY--")

    execute_query_tool = QuerySQLDatabaseTool(db=db)
    return {"table_info": execute_query_tool.invoke(state["table_query"])}

def execute_general_query(state: State):
    """Execute SQL query."""
    print("--EXECUTING SQL QUERY--")

    execute_query_tool = QuerySQLDatabaseTool(db=db)
    return {"result": execute_query_tool.invoke(state["query"])}

def validate_data(state):
    """Validate data."""
    print("--VALIDATING DATA--")
    data = state['result']

    llm = model.with_structured_output(DataValidation)

    result = llm.invoke(data_val_prompt.invoke({
        'question': state['question'],
        'data': data,
        'query': state['query'],
        'table_info': state["table_info"],
        # 'table_name': state['table_name']
        }))

    return {"ValidData": result.ValidData, "suggestions": result.suggestions}

def analyse_query(state):

    question = state['question']
    table_info = state['table_info']

    prompt = analysis_prompt.invoke({"question": question, "table_info": table_info})
    llm = model.with_structured_output(QueryAnalysis)
    analysis = llm.invoke(prompt)
    return {'breakdown': analysis.breakdown}

def subquestions(state):

    shouldbreak = state['breakdown']

    if shouldbreak == 'yes':
        prompt = breakdown_prompt.invoke({"question": state['question'], "table_info": state['table_info']})
        llm = model.with_structured_output(QueryBreakdown)
        breakdown = llm.invoke(prompt)
        return {'subquestion': breakdown.subq}
    else:
        return {'subquestion': [state['question']]}
    
def make_msg_history(context):
    history = []

    for key, val in context.items():
        history.append(HumanMessage(content=key))
        history.append(AIMessage(content=val['answer']))

    return history

def execution_loop(state):
    context = {}
    subquestions = state['subquestion']

    for subquestion in subquestions:
        history = make_msg_history(context)
        history.append(HumanMessage(content=subquestion))
        if context:
          subquestion = question_construction({'messages': history, 'table_info': state['table_info']})['question']

        data_valid = False
        validation_attempts = 0
        query = None
        
        while not data_valid and validation_attempts < 3:
            if validation_attempts == 0:
                query = write_query({
                    'question': subquestion,
                    'table_info': state['table_info'],
                    'table_name': state['table_name'],
                    'context': context
                })['query']

            time.sleep(1)  # Pause for 1 second to avoid exhausting API resources

            result = execute_general_query({'query': query})['result']

            time.sleep(1)  # Pause for 1 second to avoid exhausting API resources

            data_val = validate_data({
                'question': subquestion,
                'result': result,
                'query': query,
                'table_info': state['table_info'],
                'table_name': state['table_name'],
                'context': context
            })

            time.sleep(1)  # Pause for 1 second to avoid exhausting API resources

            if data_val['ValidData'] == 'no':

                print(data_val['suggestions'])
                query = rewrite_query({
                    'question': subquestion,
                    'suggestions': data_val['suggestions'],
                    'query': query,
                    'table_info': state['table_info'],
                    'context': context
                })['query']
                validation_attempts += 1
                time.sleep(1)  # Pause for 1 second to avoid exhausting API resources
            else:
                data_valid = True

        if data_valid:
            answer = generate_answer({
                'question': subquestion,
                'query': query,
                'result': result,
                'context': context
            })['answer']

            context[subquestion] = {
                'query': query,
                'result': result,
                'answer': answer
            }

    return {'context': context}

def generate_answer(state):

    print("-- GENERATING ANSWER--")

    chain = llm_prompt | model | StrOutputParser()
    ans = chain.invoke({'question': state['question'], 'query': state['query'], 'data': state['result'], 'context': state['context']})
    return {"answer": ans}

def generate_final_answer(state):

    print("-- GENERATING ANSWER--")

    chain = final_llm_prompt | model | StrOutputParser()
    ans = chain.invoke({'question': state['question'],  'context': state['context']})
    return {"answer": ans, "messages": ans}

