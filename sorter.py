import streamlit as st
from datetime import datetime
import smtplib

def sortscores(scorelist):
    st.title("Potential Candidates")
    
    # Sort candidates by score in decreasing order
    sorted_data = sorted(scorelist, key=lambda x: x['score'], reverse=True)
    
    # Select/Deselect All buttons
    select_all = st.checkbox("SELECT ALL")
    deselect_all = st.checkbox("DESELECT ALL")
    
    # Display candidates and count selected
    selected_candidates = display_candidates(sorted_data, select_all, deselect_all)
    
    # Show selected count
    selected_count = len(selected_candidates)
    st.write(f"Number of candidates selected: {selected_count}")
    
    # Interview scheduling
    interview_date = st.date_input("Select Interview Date", min_value=datetime.today())
    interview_time = st.time_input("Select Interview Time")
    interview_location = st.text_input("Interview Location")

    # Get Sender Email and App Password
    sender_email = st.text_input("Enter Sender Email")

    link = "[Google Mail Help Center](https://support.google.com/mail/answer/185833?hl=en)"
    st.markdown(f" [Click here to setup your Google app password:](https://support.google.com/mail/answer/185833?hl=en)")
    
    app_password = st.text_input("Enter 16 Digit App Password", type="password")

    st.title("Draft Mail")
    
    draft = st.button("Generate Draft")
    if "draft_state" not in st.session_state:
        st.session_state.draft_state = False

    # Update button color if clicked and show new page
    if draft or st.session_state.draft_state:
        st.session_state.draft_state = True
        for candidate in selected_candidates:
            st.write(f"Candidate: {candidate['email']}")
            st.write(f"Interview Date: {interview_date}")
            st.write(f"Interview Time: {interview_time}")
            st.write(f"Interview Location: {interview_location}")
            st.markdown('--------------------')

        replaced_content = replace_placeholders(interview_date, interview_time, interview_location)
        st.write(replaced_content)

    interview = st.button("NOTIFY INTERVIEW")
    if "interview_state" not in st.session_state:
        st.session_state.interview_state = False

    # Update button color if clicked and show new page
    if interview or st.session_state.interview_state:
        st.session_state.interview_state = True
        notify_interview_print(selected_candidates, interview_date, interview_time, interview_location)
        
        # Check if both email and password are provided
        if sender_email and app_password:
            notify_interview(selected_candidates, interview_date, interview_time, interview_location, sender_email, app_password)
        else:
            st.error("Please provide both Sender Email and App Password before sending emails.")


def notify_interview(selected_candidates, interview_date, interview_time, interview_location, sender_email, app_password):
    # Connect to the SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    try:
        # Login with the provided email and app password
        server.login(sender_email, app_password)

        for candidate in selected_candidates:
            recipient = candidate['email']
            subject = "INTERVIEW CALL"
            content = replace_placeholders(interview_date, interview_time, interview_location)
            message = f"Subject: {subject}\n\n{content}"

            # Send the email
            server.sendmail(sender_email, recipient, message)
        
    except smtplib.SMTPAuthenticationError:
        st.error("Failed to authenticate. Please check your credentials and try again.")
    except smtplib.SMTPException as e:
        st.error(f"An error occurred while sending emails: {str(e)}")

    finally:
        # Close the connection to the SMTP server
        server.quit()


def replace_placeholders(date, time, location):
    with open('notice.txt', 'r') as file:
        notice_content = file.read()
    # Convert date to a formatted string
    formatted_date = date.strftime('%d-%m-%Y')
    # Convert time to a formatted string
    formatted_time = time.strftime('%H:%M')
    # Replace placeholders with the formatted values
    notice_content = notice_content.replace('[Date]', formatted_date)
    notice_content = notice_content.replace('[Time]', formatted_time)
    notice_content = notice_content.replace('[Location]', location)
    return notice_content

def display_candidates(candidates, select_all, deselect_all):
    selected_candidates = []
    for candidate in candidates:
        candidate_selected = st.checkbox(f"{candidate['email']} (Score: {candidate['score']})", value=select_all)
        if candidate_selected:
            selected_candidates.append(candidate)
    if deselect_all:
        selected_candidates = []
    return selected_candidates

def notify_interview_print(selected_candidates, interview_date, interview_time, interview_location):
    for candidate in selected_candidates:
        print(f"Candidate: {candidate['email']}")
        print(f"Interview Date: {interview_date}")
        print(f"Interview Time: {interview_time}")
        print(f"Interview Location: {interview_location}")
        print("=" * 20)
