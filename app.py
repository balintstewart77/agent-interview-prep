import streamlit as st
import json
import random
from config import *
from feedback_generator import generate_feedback, evaluate_answer_quality
from followup_generator import generate_followup_question
from clarification_handler import generate_clarification, is_valid_clarification_question

st.title("Data Science Interview Prep Agent")
st.write("Practice technical questions with AI feedback")

# Load questions
@st.cache_data
def load_questions():
    with open('data/questions.json', 'r') as f:
        return json.load(f)

questions = load_questions()

# Get unique categories
categories = list(set(q["category"] for q in questions))

# Initialize session state
if "selected_question" not in st.session_state:
    st.session_state.selected_question = None
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "current_followup" not in st.session_state:
    st.session_state.current_followup = None
if "current_thread" not in st.session_state:
    st.session_state.current_thread = []

# Category selection
selected_category = st.selectbox(
    "Choose a category:",
    ["Select a category..."] + categories
)

# Generate question button
if st.button("Generate Question") and selected_category != "Select a category...":
    # Filter questions by category
    category_questions = [q for q in questions if q["category"] == selected_category]
    
    # Randomly select one
    st.session_state.selected_question = random.choice(category_questions)
    
    # Reset states when new question is generated
    st.session_state.current_followup = None
    st.session_state.current_thread = []
    st.rerun()

# Display selected question with persistent thread
if st.session_state.selected_question:
    st.subheader("Your Interview Question:")
    st.write(f"**Category:** {st.session_state.selected_question['category'].replace('_', ' ').title()}")
    st.write(f"**Question:** {st.session_state.selected_question['question']}")
    
    # Display conversation thread
    if st.session_state.current_thread:
        st.markdown("---")
        st.subheader("Conversation Thread")
        
        for i, entry in enumerate(st.session_state.current_thread):
            # User's answer
            with st.chat_message("user"):
                attempt_label = f" (Attempt {i+1})" if i > 0 else ""
                st.write(f"**Your Answer{attempt_label}:**")
                st.write(entry['answer'])
            
            # AI feedback
            with st.chat_message("assistant"):
                st.write(f"**Feedback** (Quality: {entry['quality_score']}/5)")
                st.write(entry['feedback'])
                
                # Show follow-up if exists
                if entry.get('followup'):
                    st.write(f"**Follow-up:** {entry['followup']}")
                    
                    if entry.get('followup_answer'):
                        st.write(f"**Your Follow-up:** {entry['followup_answer']}")
                        if entry.get('followup_feedback'):
                            st.write(f"**Follow-up Feedback:** {entry['followup_feedback']}")
        
        st.markdown("---")
    
    # Answer input section - always visible
    answer_label = "Your answer:" if not st.session_state.current_thread else "Try another answer:"
    user_answer = st.text_area(answer_label, height=200, key=f"answer_input_{len(st.session_state.current_thread)}")
    
    if st.button("Submit Answer") and user_answer.strip():
        with st.spinner("Generating feedback..."):
            # Generate feedback
            feedback = generate_feedback(
                st.session_state.selected_question['question'], 
                user_answer,
                iteration=len(st.session_state.current_thread) + 1
            )
            
            # Evaluate quality
            quality_score = evaluate_answer_quality(
                st.session_state.selected_question['question'],
                user_answer
            )
            
            # Generate follow-up if appropriate
            is_revision = len(st.session_state.current_thread) > 0
            followup_question = None
            if quality_score >= 3 or is_revision:
                followup_question = generate_followup_question(
                    st.session_state.selected_question['question'],
                    user_answer,
                    feedback,
                    quality_score,
                    is_revision=is_revision
                )
            
            # Add to current thread
            thread_entry = {
                "answer": user_answer,
                "feedback": feedback,
                "quality_score": quality_score,
                "followup": followup_question,
                "attempt_number": len(st.session_state.current_thread) + 1
            }
            
            st.session_state.current_thread.append(thread_entry)
            
            # Also add to main conversation history
            st.session_state.conversation_history.append({
                "question": st.session_state.selected_question,
                **thread_entry
            })
            
            st.rerun()

# Follow-up answer section - only show if there's a pending follow-up
if (st.session_state.current_thread and 
    st.session_state.current_thread[-1].get('followup') and 
    not st.session_state.current_thread[-1].get('followup_answer')):
    
    current_followup = st.session_state.current_thread[-1]['followup']
    
    st.markdown("---")
    st.subheader("Answer the Follow-up")
    st.write(f"**Follow-up:** {current_followup}")
    
    followup_answer = st.text_area("Your follow-up answer:", height=150, key="followup_answer_input")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit Follow-up"):
            if followup_answer.strip():
                with st.spinner("Analyzing follow-up..."):
                    followup_feedback = generate_feedback(current_followup, followup_answer)
                    followup_quality = evaluate_answer_quality(current_followup, followup_answer)
                    
                    # Update the last thread entry with follow-up info
                    st.session_state.current_thread[-1]['followup_answer'] = followup_answer
                    st.session_state.current_thread[-1]['followup_feedback'] = followup_feedback
                    st.session_state.current_thread[-1]['followup_quality'] = followup_quality
                    
                    # Update main history too
                    if st.session_state.conversation_history:
                        st.session_state.conversation_history[-1]['followup_answer'] = followup_answer
                        st.session_state.conversation_history[-1]['followup_feedback'] = followup_feedback
                        st.session_state.conversation_history[-1]['followup_quality'] = followup_quality
                    
                    st.rerun()
                    
    with col2:
        if st.button("Skip Follow-up"):
            st.session_state.current_thread[-1]['followup_skipped'] = True
            st.rerun()

# Student can ask clarifying questions - only after submitting at least one answer
if st.session_state.current_thread:
    st.markdown("---")
    st.subheader("Need Help Understanding?")
    st.write("Ask for clarification on any concept you're struggling with:")
    
    student_question = st.text_area(
        "Your question:", 
        height=100, 
        placeholder="e.g., 'Can you provide some examples of methods to reduce model overfitting?'",
        key=f"student_question_{len(st.session_state.current_thread)}"
    )
    
    if st.button("Ask Question") and student_question.strip():
        with st.spinner("Providing clarification..."):
            # Get relevant knowledge base context
            from knowledge_base import get_feedback_context
            context = get_feedback_context(st.session_state.selected_question['question'])
            
            # Reference their most recent answer for context
            recent_answer = st.session_state.current_thread[-1]['answer']
            
            # Generate clarification
            clarification = generate_clarification(
                st.session_state.selected_question['question'],
                recent_answer,
                student_question
            )
            
            # Display in chat format
            with st.chat_message("user"):
                st.write(f"**Your Question:** {student_question}")
            
            with st.chat_message("assistant"):
                st.write(f"**Clarification:** {clarification}")
            
            # Optional: Add to thread for persistence
            clarification_entry = {
                "type": "clarification",
                "student_question": student_question,
                "clarification": clarification,
                "timestamp": len(st.session_state.current_thread)
            }
            
            # Store clarifications separately for better organization
            if "clarifications" not in st.session_state:
                st.session_state.clarifications = []
            st.session_state.clarifications.append(clarification_entry)
            

# New question button - clears current thread
if st.session_state.current_thread:
    st.markdown("---")
    if st.button("New Question"):
        st.session_state.selected_question = None
        st.session_state.current_thread = []  # Clear thread for new question
        st.rerun()

# Enhanced conversation history display
if st.session_state.conversation_history:
    with st.expander("Interview History", expanded=False):
        for i, item in enumerate(st.session_state.conversation_history):
            attempt_type = ""
            if item.get('is_revision'):
                attempt_type = " (Revised)"
            elif item.get('is_different_attempt'):
                attempt_type = " (Alternative Answer)"
                
            st.write(f"**Q{i+1}:** {item['question']['question']}")
            st.write(f"**Quality:** {item['quality_score']}/5{attempt_type}")
            st.write(f"**Answer:** {item['answer'][:100]}...")
            
            if item.get('followup'):
                st.write(f"**Follow-up:** {item['followup']}")
                if item.get('followup_answer'):
                    st.write(f"**Follow-up Quality:** {item.get('followup_quality', 'N/A')}/5")
            
            st.markdown("---")

# Reset button for new interview session
if st.session_state.conversation_history:
    if st.button("Clear All History"):
        st.session_state.conversation_history = []
        st.session_state.selected_question = None
        st.session_state.current_thread = []
        st.session_state.current_followup = None
        st.rerun()