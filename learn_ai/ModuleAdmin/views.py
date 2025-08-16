from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from authorize.models import User
from django.views.decorators.csrf import csrf_exempt
#Chatbot requirements
import os
import time
from dotenv import load_dotenv
from django.shortcuts import render, redirect
from django.http import JsonResponse
from groq import Groq
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter



import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from learn_ai import settings

from .models import *

load_dotenv()
# Create your views here.
def user_list(request):
    users = User.objects.all()
    return render(request, 'admin/admin_dashboard.html', {'users': users})

def user_add(request):
    users = User.objects.all()

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        if username and email and password and role:
            user = User.objects.create_user(username=username, email=email, password=password, role=role)
            user.save()
            return redirect('users')
    
    return render(request, 'admin/add_user.html',{'users': users})

def register(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')
        if username and password and role:
            user = User.objects.create_user(username=username, password=password, role=role)
            user.save()
            return redirect('login')
    return render(request, 'authority/registration.html')

def course_list(request):
    courses=Course.objects.all()
    context={'courses':courses}
    return render(request, 'courses/list_courses.html',context)

def add_course(request):
    try:
        if request.method=="POST":
            course_name=request.POST.get('course_name')
            description=request.POST.get('description')
            course_image=request.FILES["course_image"]
            youtube_link=request.POST.get('youtube_link')
            pdf_documents=request.FILES["pdf_documents"]
            file_name = pdf_documents.name
            
            course=Course.objects.create(course_name=course_name,
                                        description=description,
                                        course_image=course_image,
                                        youtube_link=youtube_link,
                                        pdf_documents=pdf_documents
                                        )
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            region = settings.AWS_S3_REGION_NAME
            folder_name = course_name
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
            try:
                s3.put_object(Bucket=bucket_name, Key=f'{folder_name}/')
                course.save()
                print(f"Folder '{folder_name}' created successfully in bucket '{bucket_name}'.")
                if pdf_documents:
                    print("------IAM IN---------")
                    print(f"{type(file_name)}",file_name)
                    s3.upload_fileobj(pdf_documents, bucket_name, f'{folder_name}/{file_name}')
                    print(f"File '{pdf_documents}' uploaded successfully.")
                    return redirect('list_course')
                return redirect('list_course')
            
                

            except NoCredentialsError:
                return "AWS credentials not found. Please configure your credentials."
            except ClientError as e:
                return f"An error occurred: {e}"
            
            
            # for pdf_doc in pdf_documents:
            #     course.pdf_documents.add(pdf_doc)
            
    except Exception as e:
        print(str(e))
    return render(request, 'courses/add_course.html')

def get_s3_objects(bucket_name, folder_name):
    s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=f'{folder_name}/')
    if 'Contents' in response:
        file_list = []
        for obj in response['Contents']:
            file_key = obj['Key']
            file_name = file_key.split('/')[-1] #get the filename
            file_list.append(file_name)
        return [obj['Key'] for obj in response['Contents']], file_list
    return []

def view_course(request, course_id):
    course=Course.objects.get(pk=course_id)
    folder_name = course.course_name
    
    object_keys,file_list = get_s3_objects(settings.AWS_STORAGE_BUCKET_NAME, folder_name)
    file_list=file_list[1:]
    print(file_list)
    context={'course':course,'object_keys':object_keys,'file_list':file_list}
    return render(request, 'courses/view_course.html',context)

def delete_course(request, course_id):
    course=Course.objects.get(pk=course_id)
    course.delete()
    return redirect('list_course')


@csrf_exempt
def stream(request):
    return render(request, 'admin/stream.html')
