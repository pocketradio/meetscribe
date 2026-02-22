import streamlit as st
from src.app.graph.graph import app
from loader import load_document, load_pasted_text
import uuid
import tempfile
import os

st.title("Meetscribe")
st.subheader("AI-Powered Meeting Analysis with Human-in-the-Loop")


# session state init 
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4()) # create a new thread ID for langgraph

if 'stage' not in st.session_state: # stage -> UI screen control
    st.session_state.stage = 'input' 

config = {"configurable" : {"thread_id" : st.session_state.thread_id}}
# configurable is a reserved key in LG. thread_id is passed here so that LG can load or save the crct checkpoint
# so that same workflow instance can resume across reruns

# Input stage ; default
if st.session_state.stage == 'input':
    input_method = st.radio("Choose input method:", ["Paste Text", "Upload File"])
    
    transcript = None
    
    if input_method == "Paste Text":
        transcript = st.text_area("Paste your meeting transcript here:", height=300)
    else:
        uploaded_file = st.file_uploader("Upload transcript (PDF or TXT)", type=['pdf', 'txt'])
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp: #tempfile needed since PDF loader needs file path
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name 
                
            #extract raw text from pdf or txt:
            transcript = load_document(tmp_path)
            os.unlink(tmp_path) # deleting temp file
            st.success("File loaded :D")
    
    if st.button("Analyze Meeting", type="primary"):
        if not transcript:
            st.error("Please provide a transcript!")
        else:
            with st.spinner("Processing..."):
                # start graph ; it will pause at review node
                for chunk in app.stream({'transcript': transcript}, config):
                    pass  # let it run until interruption
                # app.invoke wont support interrupts, it'll run fully
                
                
                st.session_state.stage = 'review'# move UI to review screen
            st.rerun()


# Review stage
elif st.session_state.stage == 'review':
    # get current state from checkpointer
    state = app.get_state(config)
    current_values = state.values
    
    # current_values will contain summary, enmail etc
    
    st.success("Analysis complete! Review the results:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📄 Summary")
        st.write(current_values['summary'])
        
        st.markdown("### ✅ Action Items")
        st.write(current_values['action_items'])
    
    with col2:
        st.markdown("### 📧 Follow-up Email Draft")
        email_display = st.empty()
        email_display.code(current_values['email'], language=None)
    
    st.divider()
    st.markdown("### 🤔 What would you like to do?")
    
    
    
    
    col_a, col_b, col_c, col_d = st.columns(4)
    
    with col_a:
        if st.button("✅ Approve & Send", type="primary"):
            # Update state with decision and resume
            app.update_state(config, {"decision": "send"})
            for chunk in app.stream(None, config):
                pass
            st.session_state.stage = 'complete' # move to final screen after below rerun
            st.rerun()
    
    with col_b:
        if st.button("✏️ Edit Draft"):
            st.session_state.stage = 'edit'
            st.rerun()
    
    with col_c:
        if st.button("🔄 Regenerate"):
            # Update state with regenerate decision and resume
            app.update_state(config, {"decision": "regenerate"})
            with st.spinner("Regenerating..."):
                for chunk in app.stream(None, config):
                    pass
            st.rerun()
    
    with col_d:
        if st.button("🛑 Cancel"):
            app.update_state(config, {"decision": "stop"})
            for chunk in app.stream(None, config):
                pass
            
            # reset stage and threadid : 
            
            st.session_state.stage = 'input'
            st.session_state.thread_id = str(uuid.uuid4())  # new thread
            st.rerun()


# Edit stage
elif st.session_state.stage == 'edit':
    state = app.get_state(config)
    current_values = state.values
    
    st.markdown("### ✏️ Edit Email Draft")
    edited_email = st.text_area("Edit the email:", value=current_values['email'], height=300)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save & Continue Review"):
            # Update the email in state
            app.update_state(config, {"email": edited_email, "decision": "edit"})
            st.session_state.stage = 'review' 
            st.rerun()
    with col2:
        if st.button("◀️ Cancel Edit"):
            st.session_state.stage = 'review'
            st.rerun()
            

# Complete stage
elif st.session_state.stage == 'complete':
    state = app.get_state(config)
    current_values = state.values
    
    st.success("✅ Email approved and ready to send!")
    st.markdown("### 📧 Final Email")
    st.code(current_values['email'], language=None)
    
    if st.button("🔄 Start New Analysis"):
        st.session_state.stage = 'input'
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()