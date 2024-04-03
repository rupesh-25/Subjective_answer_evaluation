from django.shortcuts import render, redirect, HttpResponse
from django.http import HttpResponseRedirect
from openai import OpenAI
from langchain_community.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PDFMinerLoader
import re

def home(request):
    return render(request, 'ut.html')

def create_vector_db(request):
    if request.method == 'POST':
        embeddings=OpenAIEmbeddings(model="text-embedding-3-small",openai_api_key='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')
        textbook=request.FILES.get('pdfFile')
        file_path = "C:\\Users\\DELL\\Subjective_answer_evaluation\\nlp\\static\\" + textbook.name
        
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
        # # Read the content of the question paper file
        # question = question_file.read().decode('utf-8')
        # # Read the content of the student answer file
        # student_answer = answer_file.read().decode('utf-8')

        #Gotta have to write the OCR code here

        #Fetch the content from the textbook
        embeddings=OpenAIEmbeddings(model="text-embedding-3-small",openai_api_key='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')
        faiss_index=FAISS.load_local("New_Vector_Database1",embeddings,allow_dangerous_deserialization=True)
        docs = faiss_index.similarity_search(question,k=2)

        #Obtain the output
        temp_template="So you are a teacher evaluating students answers and giving it a score. The question carries 10 marks. You are having a syllabus sheet which you refer for assigning marks. So here is the syllabus sheet-{docs}. So here is the question-{question} and here is the corresponding students answer-{student_answer}. Just return score and nothing else."
        def get_conversational_chain(template):
            llm=OpenAI(temperature=0.5,openai_api_key='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')
            prompt_template=PromptTemplate(
                input_variables=['question','docs','student_answer'],
                template=template
            )
            name_chain=LLMChain(llm=llm, prompt=prompt_template)
            return name_chain

        def user_input(question,template,student_answer):
            chain=get_conversational_chain(template)
            response=chain.run(question=question, student_answer=student_answer, docs=docs, return_only_outputs=True)
            return response
        
        generated_answer=user_input(question, temp_template, student_answer)
        reo=re.compile(f"(\d+)/10")
        mo=reo.search(generated_answer)

    return render(request, 'result.html', {"output": mo[0]})