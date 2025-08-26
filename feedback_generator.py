from knowledge_base import get_feedback_context

def generate_feedback(question, user_answer, iteration=1):
    """Generate structured feedback using knowledge base context"""
    
    # Get relevant concept knowledge
    context = get_feedback_context(question)
    
    feedback_prompt = f"""
    {context}
    
    You are an expert data science interviewer. A candidate just answered this question:
    
    QUESTION: {question}
    CANDIDATE ANSWER: {user_answer}
    ATTEMPT: {iteration}
    
    Based on the concept knowledge above, provide structured feedback:
    
    1. STRENGTHS: What did they demonstrate well?
    2. GAPS: What key points from the concept knowledge are missing?
    3. IMPROVEMENTS: Specific suggestions using the knowledge base
    4. RED FLAGS: Did they hit any of the common interview mistakes?
    5. NEXT STEPS: What should they focus on in their revision?

    Be encouraging but honest. Focus on helping them improve without giving away the complete answer.
    """
    
    try:
        response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful data science interview coach."},
                {"role": "user", "content": feedback_prompt}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating feedback: {str(e)}"

def evaluate_answer_quality(question, user_answer):
    """Quick evaluation to determine if answer needs improvement"""
    
    eval_prompt = f"""
    Rate this interview answer on a scale of 1-5:
    1 = Poor (major gaps, incorrect)
    2 = Below average (some understanding, needs work)
    3 = Average (decent but could be stronger)
    4 = Good (solid answer, minor improvements)
    5 = Excellent (comprehensive, clear, accurate)
    
    QUESTION: {question}
    ANSWER: {user_answer}
    
    Respond with just the number (1-5).
    """
    
    try:
        response = openai.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": eval_prompt}],
            max_tokens=10,
            temperature=0
        )
        
        return int(response.choices[0].message.content.strip())
    
    except:
        return 3  # Default to average if error