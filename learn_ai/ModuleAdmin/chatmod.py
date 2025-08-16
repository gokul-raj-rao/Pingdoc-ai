import os
import time
from dotenv import load_dotenv
from groq import Groq
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_docs_from_url(url):
    loader = WebBaseLoader(url)
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    split_docs = text_splitter.split_documents(docs)
    print('Documents Loaded from URL')
    return split_docs


def get_docs(file_path):
    start_time = time.time()
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
    final_documents = text_splitter.split_documents(documents)
    print('Documents Loaded')
    end_time = time.time()
    print(f"Time taken to load documents: {end_time - start_time:.2f} seconds")
    return final_documents


def create_vector_store(docs):
    start_time = time.time()
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"trust_remote_code": True})
    vectorstore = FAISS.from_documents(docs, embeddings)
    print('DB is ready')
    end_time = time.time()
    print(f"Time taken to create DB: {end_time - start_time:.2f} seconds")
    return vectorstore


def chat_groq(messages):
    load_dotenv()
    client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
    response_content = ''
    stream = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages,
        max_tokens=1024,
        temperature=1.3,
        stream=True,
    )

    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content:
            response_content += chunk.choices[0].delta.content
    return response_content


def summarize_chat_history(chat_history):
    chat_history_text = " ".join([f"{chat['role']}: {chat['content']}" for chat in chat_history])
    prompt = f"Summarize the following chat history:\n\n{chat_history_text}"
    messages = [{'role': 'system', 'content': 'You are very good at summarizing the chat between User and Assistant'}]
    messages.append({'role': 'user', 'content': prompt})
    summary = chat_groq(messages)
    return summary


def main():
    print("Welcome to ArvDocuQuery!")
    print("1. Upload PDF")
    print("2. Enter Web URL")
    option = input("Choose an option (1/2): ").strip()

    docs = None
    vectorstore = None
    chat_history = []

    if option == "1":
        file_path = input("Enter the path to the PDF file: ").strip()
        if os.path.exists(file_path):
            print("Loading documents...")
            docs = get_docs(file_path)  #get documents
        else:
            print("File not found. Please try again.")
    elif option == "2":
        url = input("Enter the web URL: ").strip()
        print("Fetching and processing documents from URL...")
        docs = get_docs_from_url(url)

    if docs:
        print("Creating vector store...")
        vectorstore = create_vector_store(docs) #create vector store

    while True:
        user_input = input("Enter your question (or type 'exit' to quit): ").strip()
        if user_input.lower() == 'exit':
            break

        if vectorstore:
            retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})
            context = retriever.invoke(user_input)
            prompt = f'''
            Answer the user's question based on the latest input provided in the chat history. Ignore
            previous inputs unless they are directly related to the latest question. Provide a generic
            answer if the answer to the user's question is not present in the context by mentioning it
            as general information.

            Context: {context}

            Chat History: {chat_history}

            Latest Question: {user_input}
            '''

            messages = [{'role': 'system', 'content': 'You are a very helpful assistant'}]
            messages.append({'role': 'user', 'content': prompt})

            try:
                ai_response = chat_groq(messages) #ai response
            except Exception as e:
                print(f"Error occurred during chat_groq execution: {str(e)}")
                ai_response = "An error occurred while fetching response. Please try again."

        else:
            prompt = f'''
            Answer the user's question based on the latest input provided in the chat history. Ignore
            previous inputs unless they are directly related to the latest
            question.

            Chat History: {chat_history}

            Latest Question: {user_input}
            '''

            messages = [{'role': 'system', 'content': 'You are a very helpful assistant'}]
            messages.append({'role': 'user', 'content': prompt})

            try:
                ai_response = chat_groq(messages)
            except Exception as e:
                print(f"Error occurred during chat_groq execution: {str(e)}")
                ai_response = "An error occurred while fetching response. Please try again."

        chat_history.append({'role': 'user', 'content': user_input})
        chat_history.append({'role': 'assistant', 'content': ai_response})
        print(f"Assistant: {ai_response}")

    print("\nGenerating chat summary...")
    chat_summary = summarize_chat_history(chat_history)
    print("Chat Summary:")
    print(chat_summary)


if __name__ == "__main__":
    main()
