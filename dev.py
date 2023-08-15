import streamlit as st
import base64
import csv
import qa
import ReSAn2
import sorter
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import os
import fitz

path=os.path.dirname(os.path.abspath(__file__))
analyser = ReSAn2.ResumeAnalyser()

essential_skills = ["Python", "JavaScript", "HTML", "CSS"]

# Download NLTK resources
#nltk.download('punkt')
#nltk.download('stopwords')

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()
 
def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file) 
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: scroll; # doesn't work
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return

def convert_image_to_base64(image_path):
    with open(image_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
    return encoded_string

def set_streamlit_background(image_path):
    st.markdown(
        f"""
        <style>
        .reportview-container {{
            background: url(data:image/jpg;base64,{convert_image_to_base64(image_path)});
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Preprocess the text
def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text.lower())
    words = [word for word in words if word.isalpha() and word not in stop_words]
    return " ".join(words)

def read_skills_from_csv():
    skills_list = []
    with open("skills.csv", mode="r") as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            skills_list.append(row[0].strip().lower())
    return skills_list

def trigger_skills(description):
    skills_list = read_skills_from_csv()

    description = preprocess_text(description)
    skills_list = [preprocess_text(skill) for skill in skills_list]

    # Create a tfidfVectorizer instance
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform([description] + skills_list)
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()

    target_skills = []
    for i, similarity in enumerate(cosine_similarities):
        if similarity >= 0.2:        #Threshold taken as 50%
            target_skills.append(skills_list[i])

    print("The target skills are: ",target_skills)
    return target_skills

def extract_email_from_txt(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return emails

def read_pdf(pdffile):
    pdf_data = pdffile.read()
    pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
    pdf_text = ""

    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        pdf_text += page.get_text()

    pdf_document.close()
    return pdf_text

def is_document_file(filename):
    allowed_extensions = [".pdf", ".doc", ".docx"]
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)

def document_input():
    # Document Uploader
    st.header("Resume/CV Uploader")

    uploaded_file = st.file_uploader("Choose a document", type=["pdf", "doc", "docx"], accept_multiple_files=True)
    extracted_text={}

    if uploaded_file:
        for resume in uploaded_file:
            if is_document_file(resume.name):
                text = read_pdf(resume)
                if text:
                    email = extract_email_from_txt(text)[0]
                    if email:
                        extracted_text[email]=text
                        st.success(f"Email IDs found in {resume.name}")
                    else:
                        st.warning(f"No email IDs found in {resume.name}.")
            else:
                st.error("Please upload a PDF, Word, or other document format.") 
        if extracted_text:
            for email in extracted_text:
                st.write(email) 
    return extracted_text

def show_target_details_page():
    text = document_input()
    selected_skills=[]
    st.markdown("<h1 style='color: white;'>Enter Target Details</h1>", unsafe_allow_html=True)
    # Create a placeholder to store the job description
    description = st.text_area("Give a brief Description on Job")

    trigger = st.button("Trigger Skills")
    if "trigger_state" not in st.session_state:
        st.session_state.trigger_state = False

    # Check if the "Trigger Skills" button is clicked
    if trigger or st.session_state.trigger_state:
        st.session_state.trigger_state = True
        # Clear previously triggered skills
        st.session_state.triggered_skills = []
        # Perform task here when the button is clicked
        skills = list(set(trigger_skills(description)))
        if len(skills) > 0:
            st.success(skills)
            print("Skills", skills)
            skill_states = {skill: st.checkbox(skill) for skill in skills}
            select_all = st.button("Select All")
            deselect_all = st.button("Deselect All")
            if select_all:
                for skill in skill_states:
                    skill_states[skill] = True
            
            if deselect_all:
                for skill in skill_states:
                    skill_states[skill] = False

            selected_skills = [skill for skill, state in skill_states.items() if state]
            select_essential_skills = st.button("Select Essential Skills")
            if select_essential_skills:
                for skill in skills:
                    skill_states[skill] = skill in essential_skills
            
            # Display selected skills
            if selected_skills:
                st.success(f"Selected Skills: {', '.join(selected_skills)}")
            else:
                st.warning("Please select at least one skill.")
        else:
            st.info("No skills triggered.")

    return text, selected_skills, description

def main():
    # Set Streamlit page configuration
    st.set_page_config(
        page_title="ALIEN HR",
        page_icon="👽",
    )
    
    # set_streamlit_background('bgimg.jpg')
    set_png_as_page_bg(os.path.join(path, 'bgimg.jpg'))
    
    st.markdown("<h1 style='color: white;'>Welcome to ALIEN HR</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: white;'>We Search for the Most Talented</h2>", unsafe_allow_html=True)
    
    # Apply CSS styling for button color
    st.markdown(
        """
        <style>
        /* Button styling */
        .button {
            background-color: green;
            color: white !important;
            font-size: 16px;
            font-weight: bold;
            padding: 8px 12px;
            border-radius: 4px;
            animation: glowing 2s infinite;
        }
        .button:hover {
            background-color: #008040;
            cursor: pointer;
        }
        @keyframes glowing {
            0% {
                background-color: #002bff;
                box-shadow: 0 0 15px #002bff;
            }
            50% {
                background-color: #007bff;
                box-shadow: 0 0 20px #007bff, 0 0 30px #007bff;
            }
            100% {
                background-color: #002bff;
                box-shadow: 0 0 15px #002bff;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Reactive variable to track button click
    hunt = st.button("Let's Start Hunting", key="start_button")
    if "hunt_state" not in st.session_state:
        st.session_state.hunt_state = False

    # Update button color if clicked and show new page
    if hunt or st.session_state.hunt_state:
        st.session_state.hunt_state = True
        st.success("Talent hunting has started! Let's find the best of the best.")
        resume_text, skill_array, description = show_target_details_page()
        data=[]
        print(f"Skills:{skill_array}")

        getscores = st.button("Calculate Scores")
        if "getscores_state" not in st.session_state:
            st.session_state.getscores_state = False

        if getscores or st.session_state.getscores_state:
            st.session_state.getscores_state = True
            score, resume=0, ""

            if "generated_skills" not in st.session_state:
                st.session_state.generated_skills = []

            if not st.session_state.generated_skills:

                for resume in resume_text:
                    score = analyser(resume_text[resume], description)
                    data.append({'score':score, 'email':resume})
                st.session_state.generated_skills=data

            data=st.session_state.generated_skills
            sorter.sortscores(data)
            qa.runqa(skills=skill_array)

if __name__ == "__main__":
    main()
