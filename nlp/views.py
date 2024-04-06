from django.shortcuts import render, redirect, HttpResponse
from django.http import HttpResponseRedirect
from openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PDFMinerLoader
import re
from typing import Optional
from django.conf import settings
import os
from dotenv import load_dotenv
from google.api_core.client_options import ClientOptions
from google.cloud import documentai 
from langchain_openai import ChatOpenAI

#Load the Api keys as environment variables
load_dotenv()

#Obtain the output
temp_template="So you are a teacher evaluating students answers and giving it a score. The question carries 10 marks. You are having a syllabus sheet which you refer for assigning marks. So here is the syllabus sheet-{docs}. So here is the question-{question} and here is the corresponding students answer-{student_answer}. Evaluate considering a bunch of points typically looked by human teachers such as the depth of the answer. Just return score and nothing else. Make sure your response format is \"x/10\" is x is the assigned score"
def get_conversational_chain(iv,template):
    llm=ChatOpenAI()
    prompt_template=PromptTemplate(
        input_variables=iv,
        template=template
    )
    name_chain=LLMChain(llm=llm, prompt=prompt_template)
    return name_chain

#Google Document AI stuff
credential_path = r"C:\Users\DELL\Subjective_answer_evaluation\fluted-nation-419211-afb27e726842.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

project_id = "fluted-nation-419211"
location = "us" # Format is "us" or "eu"
processor_id = "90755a4f5919851b" # Create processor before running sample
mime_type = "application/pdf" # Refer to https://cloud.google.com/document-ai/docs/file-types for supported file types
field_mask = "text"  # Optional. The fields to return in the Document object.
processor_version_id = "pretrained-ocr-v2.0-2023-06-02" # Optional. Processor version to use

#Google DocumentAI API call code
def process_document_sample(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    mime_type: str,
    field_mask: Optional[str] = None,
    processor_version_id: Optional[str] = None,
) -> str:
    # You must set the api_endpoint if you use a location other than "us".
    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")

    client = documentai.DocumentProcessorServiceClient(client_options=opts)

    if processor_version_id:
        # The full resource name of the processor version, e.g.:
        # projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}
        name = client.processor_version_path(
            project_id, location, processor_id, processor_version_id
        )
    else:
        # The full resource name of the processor, e.g.:
        # projects/{project_id}/locations/{location}/processors/{processor_id}
        name = client.processor_path(project_id, location, processor_id)

    # Read the file into memory
    with open(file_path, "rb") as image:
        image_content = image.read()

    # Load binary data
    raw_document = documentai.RawDocument(content=image_content, mime_type=mime_type)

    # For more information: https://cloud.google.com/document-ai/docs/reference/rest/v1/ProcessOptions
    # Optional: Additional configurations for processing.
    process_options = documentai.ProcessOptions(
        # Process only specific pages
        individual_page_selector=documentai.ProcessOptions.IndividualPageSelector(
            pages=[1]
        )
    )

    # Configure the process request
    request = documentai.ProcessRequest(
        name=name,
        raw_document=raw_document,
        field_mask=field_mask,
        process_options=process_options,
    )

    result = client.process_document(request=request)

    # For a full list of Document object attributes, reference this page:
    # https://cloud.google.com/document-ai/docs/reference/rest/v1/Document
    document = result.document
    return document.text

def home(request):
    return render(request, 'ut.html')

def create_vector_db(request):
    if request.method == 'POST':
        embeddings=OpenAIEmbeddings(model="text-embedding-3-small")
        textbook=request.FILES.get('pdfFile')
        save_dir = os.path.join(settings.BASE_DIR, 'nlp//static//')
        file_path = save_dir + textbook.name
        
        # Write the file to the specified location
        with open(file_path, 'wb+') as destination:
            for chunk in textbook.chunks():
                destination.write(chunk)
        #Take the input document and then return a segmented dataset
        loader = PDFMinerLoader(file_path)
        data = loader.load_and_split()
        #New way to create vector stores and use faiss similarity search
        faiss_index = FAISS.from_documents(data, embeddings)
        faiss_index.save_local("New_Vector_Database1")
    return render(request, 'upload_documents.html')

def process(request):
    if request.method == 'POST':
        # Handle submission of other documents
        question_file = request.FILES['question_paper']
        answer_file = request.FILES['student_answer']

        save_dir = os.path.join(settings.BASE_DIR, 'nlp//static')
        
        # Create the directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Save the question paper file
        question_filepath = os.path.join(save_dir, question_file.name)
        with open(question_filepath, 'wb') as f:
            for chunk in question_file.chunks():
                f.write(chunk)
        
        # Save the student answer file
        answer_filepath = os.path.join(save_dir, answer_file.name)
        with open(answer_filepath, 'wb') as f:
            for chunk in answer_file.chunks():
                f.write(chunk)

        #Gotta have to write the OCR code here
        #Process question pdf
        questions=process_document_sample(
            project_id=project_id,
            location=location, 
            processor_id=processor_id, 
            file_path=question_filepath, 
            mime_type=mime_type, 
            field_mask=field_mask, 
            processor_version_id=processor_version_id
            )
        
        #Process student answer pdf
        answers=process_document_sample(
            project_id=project_id,
            location=location, 
            processor_id=processor_id, 
            file_path=answer_filepath, 
            mime_type=mime_type, 
            field_mask=field_mask, 
            processor_version_id=processor_version_id
            )
        
        #Preprocess questions
        questions_temp="Here is some text fetched with OCR-\"{questions}\". The OCR gets things wrong, your job is to correct and realign them. After doing that, return those questions. Make sure individual questions are separated by \"Q-\" so that further the split function run on that properly segments them. Make sure you dont add any other text in your response as that would be used for further downstream tasks"
        q_chain=get_conversational_chain(['questions'], questions_temp)
        questions=q_chain(questions, return_only_outputs=True)
        questions=questions['text']

        #Segmenting those questions and answers
        questions=questions.split("Q-")
        questions.pop(0)
        answers=answers.split("Ans")
        answers.pop(0)

        #Preprocess answers to bring them in order.
        correction_template="Here is some text-{answer}. We have got it from OCR. It is out of order. So bring that in order, respond with just the corrected text. Make sure you dont add any other text in your response as that would be used for further downstream tasks "
        correction_chain=get_conversational_chain(['answer'],correction_template)
        for idx in range(len(answers)):
            answers[idx]=correction_chain(answers[idx], return_only_outputs=True)
            answers[idx]=answers[idx]['text']
        
        # #For the sake of debugging
        # print(f"Here are the questions-{questions}")
        # print(f"Here are the answers-{answers}")

        #Load the vector DB
        embeddings=OpenAIEmbeddings(model="text-embedding-3-small")
        faiss_index=FAISS.load_local("New_Vector_Database1",embeddings,allow_dangerous_deserialization=True)

        reo=re.compile("(\\d+)/10")
        marks=[]
        context={}
        evaluation_chain=get_conversational_chain(['question','docs','student_answer'],temp_template)
        for question,student_answer in zip(questions,answers):
            docs = faiss_index.similarity_search(question,k=2)
            generated_answer=evaluation_chain.run(question=question, student_answer=student_answer, docs=docs, return_only_outputs=True)
            mo=reo.search(generated_answer)
            marks.append(mo[0])
            context[question]=mo[0]

    return render(request, 'result.html',  {'context': context})



