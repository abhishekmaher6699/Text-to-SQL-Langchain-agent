
# 💬 Text-to-SQL Chatbot with LangChain and LangGraph

A Text-to-SQL chatbot designed to allow users to interact with their uploaded CSV files using natural language. The system efficiently processes user queries by converting them into SQL, fetching the required data from csv file(now saved in a SQLite database), and presenting the results back to the user. It is equipped with context memory, enabling smooth and dynamic conversations.

![image](https://github.com/user-attachments/assets/a93452ab-375d-4e88-8adb-ba097cf431d0)


## Key Features
- **📂File Upload**: Users can upload CSV files via a user-friendly Streamlit interface. The uploaded files are automatically saved as tables in a SQLite database. 

- **💬Natural Language Interaction**: Users can chat with the system to query their data, using natural language.
- **🔍SQL Query Generation**: The LangChain and LangGraph agent powers the conversion of natural language into SQL queries.
- **🧠Context Memory**: The chatbot remembers previous interactions to provide coherent and context-aware responses using a PostgresSQL database.

- **🖥️Frontend and Backend Separation**:
  - **Frontend**: Built with Streamlit for an interactive user experience.
  - **Backend**: FastAPI handles CSV uploads, database interactions, and communication with the LangChain agent.

## 🚀Technologies Used
- **LangChain & LangGraph**: For text-to-SQL translation and conversational AI Agent capabilities.
- **FastAPI**: To create a robust backend API for handling file uploads, database operations, and agent interaction.
- **Streamlit**: For a clean and intuitive user interface.
- **SQLite**: As the database for storing the uploaded CSV files as tables.
- 
## 🛠️Agentic Workflow
This agent, built using LangChain and LangGraph, processes user queries step-by-step to ensure accurate and context-aware answers. Here's how it works:
- **Retrieve Table Information**: The agent begins by fetching metadata or schema   information about the relevant table. This information provides context that will be used to construct better queries and answers.

- **Construct Context-Aware Question**: The agent refines the user's original question to make it context-aware. If there is any previous chat history, it is incorporated to improve the understanding of the question.

- **Analyze the Question**: The agent analyzes the refined question to determine if it can be answered with a single SQL query or if it needs to be broken down further.

- **Break Down Complex Questions**: For complex questions, the agent breaks them into smaller subquestions. Each subquestion is processed individually to fetch relevant data and generate partial answers.

- **Save Intermediate Answers in Memory**: As the agent processes subquestions, it validated the fetched data, saves it if it passes and generated answers in memory. If not validated, it query is rewritten and the process repeats for n number of times. This memory is used to ensure continuity and coherence when synthesizing the final response.

- **Synthesize Final Answer**: All subquestions, their fetched data, and intermediate answers are sent to a final LLM. The LLM synthesizes a cohesive and comprehensive answer to the original user question.

- **Handle Simple Questions in a Single Step**: If the analysis shows that the question can be answered with a single SQL query, the agent directly fetches the answer and provides it without further steps.

##  How to Use  

Follow these steps to set up and use the application:  

### 1. Install Dependencies  
Install the required Python dependencies for both the backend and frontend.  

```bash  
pip install -r requirements.txt  
```  

### 2. Create a `.env` File  
Create a `.env` file in the root directory and add the following environment variables:  

```env  
UPLOAD_API_URL = "http://127.0.0.1:8000/upload_csv/"  
CHAT_API_URL = "http://127.0.0.1:8000/chat/"  
GET_TABLES_API_URL = "http://127.0.0.1:8000/get_all_tables/"  

DB_HOST = "your_database_host"  
DB_PORT = "your_database_port"  
DB_NAME = "your_database_name"  
DB_USER = "your_database_user"  
DB_PASSWORD = "your_database_password"  

GOOGLE_API_KEY = "your_google_api_key"  (or openai key depending on the model you are using)
```  

Replace `your_database_host`, `your_database_port`, `your_database_name`, `your_database_user`, `your_database_password`, and `your_google_api_key` with the appropriate values for your setup.  

### 3. Run the Backend FastAPI App  
Start the backend server by running the following command:  

```bash  
uvicorn backend.main:app --reload
```  

Ensure that the backend dependencies have been installed before running the app.  

### 4. Run the Frontend Streamlit App  
 

```bash  
streamlit run frontend/app.py  
```

This will launch the Streamlit application, where you can interact with the agent through the user interface.  

---


## 🤝Contributions

Your ideas and feedback are welcome! 🌸
