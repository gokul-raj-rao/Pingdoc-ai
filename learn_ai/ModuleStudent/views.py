from django.shortcuts import render, redirect
from ModuleAdmin.models import Course, ChatMessage, PDFFile
from django.contrib import messages
from django.conf import settings
import boto3
# NEEDED FOR CHATBOT
import os
import time
from dotenv import load_dotenv
from groq import Groq
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from django.conf import settings
load_dotenv()



# Create your views here.



def dashboard(request):
    courses=Course.objects.all()
    context={'courses':courses}
    return render(request, 'student/student_dashboard.html',context)

def view_course(request, course_id):
    course=Course.objects.get(pk=course_id)
    context={'course':course}
    return render(request, 'student/view_course.html',context)


def course_list(request):
    courses=Course.objects.all()
    context={'courses':courses}
    return render(request, 'student/list_courses.html',context)


# -----------AWS FILE STORAGE ---------------------------

def CVS(pdf_path, vectorstore_path):
    """Creates and saves a FAISS vector store from a PDF document."""
    start_time = time.time()

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)
    

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"trust_remote_code": True})
    vectorstore = FAISS.from_documents(docs, embeddings)

    vectorstore.save_local(vectorstore_path)

    print(f"Vector store saved to: {vectorstore_path}")
    end_time = time.time()
    print(f"Time taken to create and save DB: {end_time - start_time:.2f} seconds")
    return vectorstore

def LVS(vectorstore_path):
    """Loads a FAISS vector store from local storage."""
    start_time = time.time()
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", model_kwargs={"trust_remote_code": True})
    vectorstore = FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
    end_time = time.time()
    print(f"Time taken to load DB: {end_time - start_time:.2f} seconds")
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

def process_pdf_and_chat(pdf_path, query):
    """Processes the PDF and chats with the bot."""
    vectorstore_path = os.path.join(settings.BASE_DIR, "faiss_index") #save faiss index in base directory of project

    # 1. Create and save the vector store (run only once or when the PDF changes)
    if not os.path.exists(vectorstore_path):
        CVS(pdf_path, vectorstore_path)

    # 2. Load the saved vector store
    vectorstore = LVS(vectorstore_path)

    # 3. Chat with the bot using the loaded vector store
    
    chat_history=[]
    if vectorstore:
        user_input=query.strip()
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

    
    print("\nGenerating chat summary...")
    print("===>",chat_history)
    return ai_response


# ---------------------------END INBUILD FUNCTIONS---------------------------------


bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
region = os.environ.get('AWS_S3_REGION_NAME')
s3 = boto3.client(
        's3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    )
def upload_to_s3(file, bucket_name):
    s3.upload_fileobj(file, bucket_name, file.name,ExtraArgs={
            'ContentType': file.content_type
        })
    bucket_location = s3.get_bucket_location(Bucket=bucket_name)
    region = bucket_location['LocationConstraint']
    file_url = f"https://s3.{region}.amazonaws.com/{bucket_name}/{file.name.replace(' ', '+')}"
    PDFFile.objects.create(file_name=" ", file_id=str(file_url)) 
    return file_url

def get_s3_objects(bucket_name):

    response = s3.list_objects_v2(Bucket=bucket_name)
    if 'Contents' in response:
        return [obj['Key'] for obj in response['Contents']]
    return []


def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = upload_to_s3(request.FILES['file'], os.environ.get('AWS_STORAGE_BUCKET_NAME'))
        file_name = request.FILES['file'].name
        messages.success(request, "File uploaded successfully.")
        object_keys = get_s3_objects(os.environ.get('AWS_STORAGE_BUCKET_NAME'))
        s3_url =f"https://s3.{os.environ.get('AWS_S3_REGION_NAME')}.amazonaws.com/{os.environ.get('AWS_STORAGE_BUCKET_NAME')}/"
        images = [{'url': s3_url + key} for key in object_keys]
        print(file_name)
        
        return render(request, 'chat/home.html', {'images': images}) 
       

    object_keys = get_s3_objects(os.environ.get('AWS_STORAGE_BUCKET_NAME'))
    s3_url = f"https://s3.{os.environ.get('AWS_S3_REGION_NAME')}.amazonaws.com/{os.environ.get('AWS_STORAGE_BUCKET_NAME')}/"
    images = [{'url': s3_url + key} for key in object_keys]
    filename = os.path.basename(s3_url)
    
    
    return render(request, 'chat/home.html', {'images': images})




def delete_image(request):
    if request.method == 'POST':
        image_key = request.POST.get('image_key')
        print(image_key)
        object_key = image_key.split(f"{bucket_name}/")[1]
        
        try:
            s3.delete_object(Bucket=bucket_name, Key=object_key)
            messages.success(request, "File deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting image: {str(e)}")
        
        return redirect('upload')
    

   

def chat_view(request):
    chat_messages = ChatMessage.objects.all().order_by('timestamp')
    image_key = request.POST.get('image_key')
    print(image_key)
    local_pdf_path = os.path.join(settings.BASE_DIR, "temp_pdf.pdf") #save temp pdf in base dir.
    if not os.path.exists("temp_pdf.pdf"):
        pdf_key=image_key.split(f"{bucket_name}/")[-1]
        print(pdf_key)
        print(type(pdf_key))
        s3 = boto3.client('s3',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')) 
        bucket = os.environ.get('AWS_STORAGE_BUCKET_NAME') 
            
            
        s3.download_file(bucket, pdf_key, local_pdf_path)
    
    
    
    print(local_pdf_path)
    

    
    # pdf_path = os.path.join(settings.BASE_DIR, "Langchain.pdf") #save pdf in base directory of project
    if request.method == "POST":
        user_input = request.POST.get("user_input")
        if user_input:
            print(image_key)
            print(local_pdf_path)
            response = process_pdf_and_chat(local_pdf_path, user_input)
            ChatMessage.objects.create(role='user', content=user_input)
            ChatMessage.objects.create(role='assistant', content=response)
            if user_input.lower() == 'cls':
            
                ChatMessage.objects.all().delete() 
                
            if user_input=="exit":
                os.remove(local_pdf_path)
                os.remove(r"D:\Gokul\4_FinalYearProject\MAIN\learn_ai\faiss_index\index.faiss")
                os.remove(r"D:\Gokul\4_FinalYearProject\MAIN\learn_ai\faiss_index\index.pkl")
                os.rmdir(r"D:\Gokul\4_FinalYearProject\MAIN\learn_ai\faiss_index")
                return redirect('upload')
            return render(request, "chat/chat.html", {"response": response, "user_input": user_input, 'chat_messages': chat_messages})
    return render(request, "chat/chat.html")