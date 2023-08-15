import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import ReSAn2

# Dummy data
# questions = [
#     "What is the capital of France?",
#     "Who wrote \"Romeo and Juliet\"?",
#     "What is the largest planet in our solar system?",
#     "What is the chemical symbol for gold?",
#     "In which year did World War II end?"
# ]

# answers = [
#     "Paris",
#     "Shakespeare",
#     "Jupiter",
#     "Au",
#     "1945"
# ]


qstn_generator = ReSAn2.Interview_Chat()


def create_questionnaire_pdf(questions_dict):
    doc = SimpleDocTemplate("Questionnaire.pdf", pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    for qn, data in questions_dict.items():  
        wrapped_question = textwrap.fill(data['question'], width=40)
        wrapped_option1 = textwrap.fill(data['option1'], width=40)
        wrapped_option2 = textwrap.fill(data['option2'], width=40)
        wrapped_option3 = textwrap.fill(data['option3'], width=40)
        wrapped_option4 = textwrap.fill(data['option4'], width=40)
        
        question_paragraph = Paragraph(f"<b>Q:</b> {wrapped_question}", styles['Normal'])
        option1_paragraph = Paragraph(f"<b>A:</b> {wrapped_option1}", styles['Normal'])
        option2_paragraph = Paragraph(f"<b>B:</b> {wrapped_option2}", styles['Normal'])
        option3_paragraph = Paragraph(f"<b>C:</b> {wrapped_option3}", styles['Normal'])
        option4_paragraph = Paragraph(f"<b>D:</b> {wrapped_option4}", styles['Normal'])
        
        story.append(question_paragraph)
        story.append(Spacer(1, 0.3 * inch))
        story.append(option1_paragraph)
        story.append(Spacer(1, 0.15 * inch))
        story.append(option2_paragraph)
        story.append(Spacer(1, 0.15 * inch))
        story.append(option3_paragraph)
        story.append(Spacer(1, 0.15 * inch))
        story.append(option4_paragraph)
        story.append(Spacer(1, 0.3 * inch))
    
    doc.build(story)

def create_answer_pdf(all_questions):
    doc = SimpleDocTemplate("Answer.pdf", pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    for i, answer in enumerate(all_questions, start=1):
        text = str(i) + ":" + answer
        wrapped_answer = textwrap.fill(text, width=40)
        answer_paragraph = Paragraph(f"<b>Q</b>{wrapped_answer}", styles['Normal'])
        story.append(answer_paragraph)
        story.append(Spacer(1, 0.3 * inch))
    
    doc.build(story)
    
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
        
        genfirst = st.button("Generate First Round Questions")
        if "genfirst_state" not in st.session_state:
            st.session_state.genfirst_state = False

    # Update button color if clicked and show new page
        if genfirst or st.session_state.genfirst_state:
            st.session_state.genfirst_state = True
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
    doc = SimpleDocTemplate("InterviewQuestions.pdf", pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    for question, answer in zip(questions, answers):
        wrapped_question = textwrap.fill(question, width=40)
        wrapped_answer = textwrap.fill(answer, width=40)
        
        question_paragraph = Paragraph(f"<b>Q:</b> {wrapped_question}", styles['Normal'])
        answer_paragraph = Paragraph(f"<b>A:</b> {wrapped_answer}", styles['Normal'])
        
        story.append(question_paragraph)
        story.append(Spacer(1, 0.2 * inch))
        story.append(answer_paragraph)
        story.append(Spacer(1, 0.4 * inch))
    
    doc.build(story)

# Streamlit app
def runqa(skills : list):
    st.title("CANDIDATE EVALUATION") 
    st.title("SKILL BASED TECHNICAL SCREENING ROUND") 
    st.write("DOWNLOAD QA PDF FOR TECHNICAL ROUND")   

    genpdf = st.button("Generate PDF")
    if "genpdf_state" not in st.session_state:
        st.session_state.genpdf_state = False

    # Update button color if clicked and show new page
    if genpdf or st.session_state.genpdf_state:
        st.session_state.genpdf_state = True
        questions = []
        answers = []
        
        outputs = qstn_generator(skills=["".join(skills)]) 
        for q_a in outputs:
            questions.append(q_a[0])
            answers.append(q_a[1])

        print(f"question:{questions}")
        print(f"answers:{answers}")
        create_pdf(questions[0], answers[0])
        st.success("PDF generated successfully!")
        
        with open("InterviewQuestions.pdf", "rb") as pdf_file:
            st.download_button("Download PDF", pdf_file, "InterviewQuestions.pdf")
    st.title("First Round Interview") 
    st.write("Generating Question Paper and Answer key")
    first_round()       
