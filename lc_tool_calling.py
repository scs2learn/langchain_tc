# tool_calling_gemini.py
import getpass
import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain import hub

# --- Import all your tools from the new file ---
from my_tools import (
    add,
    multiply,
    subtract, # New import
    divide,   # New import
    get_all_users,
    get_user_by_id,
    add_new_user,
    delete_existing_user,
    update_existing_user,
    get_current_weather
)

load_dotenv()

# --- Combine all imported tools ---
tools = [
    add,
    multiply,
    subtract, # Add to the list
    divide,   # Add to the list
    get_all_users,
    get_user_by_id,
    add_new_user,
    delete_existing_user,
    update_existing_user,
    get_current_weather
]

llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai", temperature=0)

# --- ENHANCED PROMPT (keep as is) ---
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", (
            "You are a helpful and proactive AI assistant. "
            "You have access to tools to perform various tasks, including arithmetic, "
            "fetching user information, and retrieving current weather. "
            "When a user asks a question that requires information from a tool, "
            "you MUST use the appropriate tool(s) to get the necessary information "
            "before responding. "
            "If a query requires multiple steps (e.g., getting user info then weather), "
            "you should chain the tool calls automatically. "
            "Always provide a direct and concise answer to the user's original question after using tools."
        )),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True) # Keep verbose=True for debugging

# --- Example Queries ---
print("\n--- Testing Arithmetic ---")
query_arithmetic_add = "What is 4 + 3 * 12?"
response_arithmetic_add = agent_executor.invoke({"input": query_arithmetic_add})
print(f"Arithmetic Add/Multiply Answer: {response_arithmetic_add['output']}")

print("\n--- Testing Subtract ---")
query_subtract = "What is 100 minus 45?"
response_subtract = agent_executor.invoke({"input": query_subtract})
print(f"Subtract Answer: {response_subtract['output']}")

print("\n--- Testing Divide ---")
query_divide = "What is 75 divided by 5?"
response_divide = agent_executor.invoke({"input": query_divide})
print(f"Divide Answer: {response_divide['output']}")

print("\n--- Testing Divide by Zero ---")
query_divide_by_zero = "What is 100 divided by zero?"
response_divide_by_zero = agent_executor.invoke({"input": query_divide_by_zero})
print(f"Divide by Zero Answer: {response_divide_by_zero['output']}")

# ... (rest of your example queries for weather and user management) ...

print("\n--- Testing Weather API ---")
query_weather = "What's the weather like in New York City in Fahrenheit?"
response_weather = agent_executor.invoke({"input": query_weather})
print(f"Weather Answer: {response_weather['output']}")

print("\n--- Testing REST API: Get all users ---")
query_get_all_users = "List all users."
response_get_all_users = agent_executor.invoke({"input": query_get_all_users})
print(f"Get All Users Answer: {response_get_all_users['output']}")

print("\n--- Testing REST API: Add a new user ---")
query_add_user = "Add a new user named Alice Smith with ID 201, born 2000-05-15, living at 789 Pine St, Anytown, CA 90210, phone 111-222-3333, email alice.smith@example.com."
response_add_user = agent_executor.invoke({"input": query_add_user})
print(f"Add User Answer: {response_add_user['output']}")

print("\n--- Testing REST API: Get user by ID ---")
query_get_user = "Can you get details for user 201?"
response_get_user = agent_executor.invoke({"input": query_get_user})
print(f"Get User 201 Answer: {response_get_user['output']}")

print("\n--- Testing REST API: Update an existing user ---")
query_update_user = "Update user 201's last name to Jones and email to alice.jones@example.com."
response_update_user = agent_executor.invoke({"input": query_update_user})
print(f"Update User 201 Answer: {response_update_user['output']}")

print("\n--- Testing REST API: Delete a user ---")
query_delete_user = "Delete user 201."
response_delete_user = agent_executor.invoke({"input": query_delete_user})
print(f"Delete User 201 Answer: {response_delete_user['output']}")

print("\n--- Testing combination tool calling REST API: Get user by ID and Weather API ---")
query_chained_weather = "What is the weather of the city associated with the user with user_id 101?"
response_chained_weather = agent_executor.invoke({"input": query_chained_weather})
print(f"Chained Weather Answer: {response_chained_weather['output']}")