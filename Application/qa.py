import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import random

# Dummy data
questions = [
    "What is the capital of France?",
    "Who wrote \"Romeo and Juliet\"?",
    "What is the largest planet in our solar system?",
    "What is the chemical symbol for gold?",
    "In which year did World War II end?"
]

answers = [
    "Paris",
    "Shakespeare",
    "Jupiter",
    "Au",
    "1945"
]


def create_questionnaire_pdf(questions_dict):
    c = canvas.Canvas("Questionnaire.pdf", pagesize=letter)
    c.setFont("Helvetica", 12)
    
    for qn, data in questions_dict.items():
        question = data['question']
        option1 = data['option1']
        option2 = data['option2']
        option3 = data['option3']
        option4 = data['option4']
        
        text = f"{qn}: {question}\nA: {option1}\nB: {option2}\nC: {option3}\nD: {option4}\n\n"
        c.drawString(100, 700 - int(qn[1:]) * 100, text)
    
    c.save()

def create_answer_pdf(all_questions):
    c = canvas.Canvas("Answer.pdf", pagesize=letter)
    c.setFont("Helvetica", 12)
    
    for i, answer in enumerate(all_questions, start=1):
        text = f"Q{i}: {answer}\n"
        c.drawString(100, 700 - i * 20, text)
    
    c.save()
    
def generate_questions(verb, quant):
    verbal_df = pd.read_csv('Verbal.csv')
    quant_df = pd.read_csv('Quant.csv')
    
    verbal_questions = verbal_df.sample(n=verb)
    quant_questions = quant_df.sample(n=quant)
    
    selected_questions = pd.concat([verbal_questions, quant_questions], ignore_index=True)
    selected_questions = selected_questions.sample(frac=1)  # Shuffle the selected questions
    
    questions_dict = {}
    answers = []
    
    for index, row in selected_questions.iterrows():
        question = row['question']
        option1 = row['option1']
        option2 = row['option2']
        option3 = row['option3']
        option4 = row['option4']
        answer = row['answer']
        
        question_data = {
            'question': question,
            'option1': option1,
            'option2': option2,
            'option3': option3,
            'option4': option4
        }
        
        questions_dict[f'Q{index + 1}'] = question_data
        answers.append(answer)
    
    return questions_dict, answers



def first_round():
    assessment_type = st.radio("Select an option:", ["Quantitative Aptitude", "Verbal Reasoning", "Both"])

    if assessment_type == "Quantitative Aptitude":
        num_quant_questions = st.number_input("Choose the number of Quantitative Aptitude questions (1-25):", min_value=1, max_value=25)
        num_verbal_questions=0
        st.write(f"You chose Quantitative Aptitude with {num_quant_questions} questions. Start your assessment!")

    elif assessment_type == "Verbal Reasoning":
        num_quant_questions=0
        num_verbal_questions = st.number_input("Choose the number of Verbal Reasoning questions (1-25):", min_value=1, max_value=25)
        st.write(f"You chose Verbal Reasoning with {num_verbal_questions} questions. Start your assessment!")

    elif assessment_type == "Both":
        num_quant_questions = st.number_input("Choose the number of Quantitative Aptitude questions (1-15):", min_value=1, max_value=15)
        num_verbal_questions = st.number_input("Choose the number of Verbal Reasoning questions (1-25):", min_value=1, max_value=25)
        st.write(f"You chose Both with {num_quant_questions} Quantitative Aptitude questions and {num_verbal_questions} Verbal Reasoning questions. Start your assessment!")
        
        if st.button("Generate First Round Questions"):
            st.write(num_quant_questions + num_verbal_questions, " questions will be generated")
            
            # Generate questions and answers
    questions_dict, answers_new = generate_questions(num_verbal_questions, num_quant_questions)
            
            # Generate Questionnaire and Answer PDFs
    create_questionnaire_pdf(questions_dict)
    create_answer_pdf(answers_new)
            
    st.success("PDFs generated successfully!")
    with open("Questionnaire.pdf", "rb") as pdf_file:
        st.download_button("Download Questionnaire PDF", pdf_file, "Questionnaire.pdf")

    with open("Answer.pdf", "rb") as pdf_file:
        st.download_button("Download Answer PDF", pdf_file, "Answer.pdf")
                    

# Create PDF function
def create_pdf(questions, answers):
    st.write("Skill Based Screening Questions PDF Generator")
    c = canvas.Canvas("InterviewQuestions.pdf", pagesize=letter)
    c.setFont("Helvetica", 12)
    
    for i, (question, answer) in enumerate(zip(questions, answers), start=1):
        question_text = f"Q{i}: {question}"
        answer_text = f"A: {answer}"
        
        c.drawString(100, 700 - i * 60, question_text)
        c.drawString(100, 700 - i * 60 - 15, answer_text)
    
    c.save()

# Streamlit app
def main():
    st.title("CANDIDATE EVALUATION") 
    st.title("SKILL BASED TECHNICAL SCREENING ROUND") 
    st.write("DOWNLOAD QA PDF FOR TECHNICAL ROUND")   
    if st.button("Generate PDF"):
        create_pdf(questions, answers)
        st.success("PDF generated successfully!")
        
        with open("InterviewQuestions.pdf", "rb") as pdf_file:
            st.download_button("Download PDF", pdf_file, "InterviewQuestions.pdf")
    st.title("First Round Interview") 
    st.write("Generating Question Paper and Answer key")
    first_round()       

if __name__ == "__main__":
    main()
