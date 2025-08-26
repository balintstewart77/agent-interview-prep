import streamlit as st
import json
import random
from config import *
from feedback_generator import generate_feedback, evaluate_answer_quality
from followup_generator import generate_followup_question

st.title("🎯 Data Science Interview Prep Agent")
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
if "revision_mode" not in st.session_state:
    st.session_state.revision_mode = False
if "original_answer" not in st.session_state:
    st.session_state.original_answer = ""
if "current_followup" not in st.session_state:
    st.session_state.current_followup = None

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
    st.session_state.revision_mode = False
    st.session_state.original_answer = ""
    st.session_state.current_followup = None
    st.rerun()

# Display selected question
if st.session_state.selected_question:
    st.subheader("Your Interview Question:")
    st.write(f"**Category:** {st.session_state.selected_question['category'].replace('_', ' ').title()}")
    st.write(f"**Question:** {st.session_state.selected_question['question']}")
    
    # Answer input - different key for revision vs initial
    answer_key = "revised_answer" if st.session_state.revision_mode else "answer_input"
    answer_label = "Your revised answer:" if st.session_state.revision_mode else "Your answer:"
    
    user_answer = st.text_area(answer_label, height=200, key=answer_key)
    
    # Different button text based on mode
    button_text = "Get Feedback on Revision" if st.session_state.revision_mode else "Get Feedback"
    
    if st.button(button_text) and user_answer.strip():
        with st.spinner("Generating feedback..."):
            # Generate feedback
            feedback = generate_feedback(
                st.session_state.selected_question['question'], 
                user_answer,
                iteration=2 if st.session_state.revision_mode else 1
            )
            
            # Evaluate quality
            quality_score = evaluate_answer_quality(
                st.session_state.selected_question['question'],
                user_answer
            )
            
            # Display feedback
            st.subheader("📋 Feedback")
            st.write(feedback)
            
            # Quality indicator
            quality_labels = {
                1: "Needs Work 📚", 
                2: "Getting There 📈", 
                3: "Good Start 👍", 
                4: "Strong Answer 💪", 
                5: "Excellent! 🌟"
            }
            st.info(f"**Answer Quality:** {quality_score}/5 - {quality_labels.get(quality_score, 'Unknown')}")
            
            # DECISION POINT: What happens next based on quality and revision status
            
            if quality_score <= 2 and not st.session_state.revision_mode:
                # Poor initial answer - encourage revision
                st.warning("💡 **Suggestion:** Your answer could be stronger. Try revising it based on the feedback above before we move to follow-up questions.")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Revise My Answer", type="primary"):
                        st.session_state.revision_mode = True
                        st.session_state.original_answer = user_answer
                        st.rerun()
                        
                with col2:
                    if st.button("➡️ Move to Follow-up Anyway"):
                        # Generate follow-up even for poor answer if they insist
                        followup_question = generate_followup_question(
                            st.session_state.selected_question['question'],
                            user_answer,
                            feedback,
                            quality_score,
                            is_revision=False
                        )
                        
                        if followup_question:
                            st.session_state.current_followup = followup_question
                            st.rerun()
            
            else:
                # Good answer (3+) or revised answer - proceed to follow-up
                is_revision = st.session_state.revision_mode
                
                followup_question = generate_followup_question(
                    st.session_state.selected_question['question'],
                    user_answer,
                    feedback,
                    quality_score,
                    is_revision=is_revision
                )
                
                if followup_question:
                    st.subheader("🤔 Follow-up Question")
                    st.success("Great! Your answer is solid enough for a follow-up question:")
                    st.info(followup_question)
                    st.session_state.current_followup = followup_question
                elif quality_score >= 5:
                    st.success("🌟 Excellent answer! No follow-up needed.")
                
                # Show improvement if this was a revision
                if is_revision and st.session_state.original_answer:
                    with st.expander("📈 See Your Improvement"):
                        st.write("**Original Answer:**")
                        st.write(st.session_state.original_answer[:200] + "..." if len(st.session_state.original_answer) > 200 else st.session_state.original_answer)
                        st.write("**Revised Answer:**")
                        st.write(user_answer[:200] + "..." if len(user_answer) > 200 else user_answer)
            
            # Store in conversation history
            st.session_state.conversation_history.append({
                "question": st.session_state.selected_question,
                "answer": user_answer,
                "feedback": feedback,
                "quality_score": quality_score,
                "followup": followup_question if 'followup_question' in locals() else None,
                "is_revision": st.session_state.revision_mode
            })
            
            # Reset revision mode after processing
            if st.session_state.revision_mode:
                st.session_state.revision_mode = False
                st.session_state.original_answer = ""

# Follow-up answer section
if st.session_state.current_followup:
    st.markdown("---")
    st.subheader("🎯 Answer the Follow-up")
    st.write(f"**Follow-up Question:** {st.session_state.current_followup}")
    
    followup_answer = st.text_area("Your follow-up answer:", height=150, key="followup_answer")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit Follow-up Answer"):
            if followup_answer.strip():
                with st.spinner("Analyzing your follow-up..."):
                    # Generate feedback on follow-up
                    followup_feedback = generate_feedback(st.session_state.current_followup, followup_answer)
                    followup_quality = evaluate_answer_quality(st.session_state.current_followup, followup_answer)
                    
                    st.subheader("📋 Follow-up Feedback")
                    st.write(followup_feedback)
                    st.info(f"**Follow-up Quality:** {followup_quality}/5")
                    
                    # Update conversation history with follow-up
                    if st.session_state.conversation_history:
                        st.session_state.conversation_history[-1]["followup_answer"] = followup_answer
                        st.session_state.conversation_history[-1]["followup_feedback"] = followup_feedback
                        st.session_state.conversation_history[-1]["followup_quality"] = followup_quality
                    
                    # Clear the follow-up
                    st.session_state.current_followup = None
                    
                    st.success("🎉 Great job completing the full interview sequence!")
                    
    with col2:
        if st.button("Skip Follow-up"):
            st.session_state.current_followup = None
            st.rerun()

# Enhanced conversation history display
if st.session_state.conversation_history:
    with st.expander("📚 Interview History", expanded=False):
        for i, item in enumerate(st.session_state.conversation_history):
            st.write(f"**Q{i+1}:** {item['question']['question']}")
            st.write(f"**Quality:** {item['quality_score']}/5 {'(Revised)' if item.get('is_revision') else ''}")
            
            if item.get('followup'):
                st.write(f"**Follow-up:** {item['followup']}")
                if item.get('followup_answer'):
                    st.write(f"**Follow-up Quality:** {item.get('followup_quality', 'N/A')}/5")
            
            st.markdown("---")

# Reset button for new interview session
if st.session_state.conversation_history:
    if st.button("🔄 Start New Interview Session"):
        st.session_state.conversation_history = []
        st.session_state.selected_question = None
        st.session_state.current_followup = None
        st.session_state.revision_mode = False
        st.session_state.original_answer = ""
        st.rerun()