from backend.agent_comp.nodes import *
from langgraph.graph import StateGraph, START, END


workflow = StateGraph(State)

workflow.add_node('get_table_info', get_table_info)
workflow.add_node('execute_table_query', execute_table_query)
workflow.add_node('question_const', question_construction)
workflow.add_node('analyse_query', analyse_query)
workflow.add_node('subquestions', subquestions)
workflow.add_node('execution_loop', execution_loop)
workflow.add_node('generate_final_answer', generate_final_answer)


workflow.add_edge(START, 'get_table_info')
workflow.add_edge('get_table_info', 'execute_table_query')
workflow.add_edge('execute_table_query', 'question_const')
workflow.add_edge('question_const', 'analyse_query')
workflow.add_edge('analyse_query', 'subquestions')
workflow.add_edge('subquestions', 'execution_loop')
workflow.add_edge('execution_loop', 'generate_final_answer')
workflow.add_edge('generate_final_answer', END)

