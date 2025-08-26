from config import client, MODEL_NAME, MAX_TOKENS, TEMPERATURE
from knowledge_base import get_feedback_context

from config import client, MODEL_NAME, MAX_TOKENS, TEMPERATURE

def generate_feedback(question, user_answer, iteration=1):
    """Generate structured feedback for a user's answer"""
    
    feedback_prompt = f"""
    You are a friendly data science interview coach giving conversational feedback.
    
    QUESTION: {question}
    STUDENT ANSWER: {user_answer}
    ATTEMPT: {iteration}
    
    Provide brief, encouraging feedback directly to the student (use "you", not "the candidate"):
    
    1. POSITIVE: Start with something they got right or showed understanding of
    2. KEY GAP: Identify the most important thing they missed (don't explain it fully)
    3. NEXT STEP: Give ONE specific suggestion to improve their answer
    
    Keep it conversational, supportive, and concise (max 4-5 sentences). Don't give away the full answer - guide them to discover it.
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a supportive interview coach. Be conversational, brief, and encouraging."},
                {"role": "user", "content": feedback_prompt}
            ],
            max_tokens=200,  # Reduced from 500
            temperature=TEMPERATURE
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating feedback: {str(e)}"

def evaluate_answer_quality(question, user_answer):
    """Quick evaluation to determine if answer needs improvement"""
    
    eval_prompt = f"""
    Rate this data science interview answer strictly on a 1-5 scale:
    
    1 = Very poor (major gaps, oversimplified, or wrong)
    2 = Poor (shows some awareness but significant issues)
    3 = Average (covers basics but lacks depth/examples)
    4 = Good (solid understanding with minor gaps)
    5 = Excellent (comprehensive, accurate, well-explained)
    
    Be harsh but fair - most real interview answers are 2-3/5.
    
    QUESTION: {question}
    ANSWER: {user_answer}
    
    Consider: Does this answer demonstrate job-ready knowledge? Would you hire based on this response?
    
    Respond with just the number (1-5).
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": eval_prompt}],
            max_tokens=10,
            temperature=0.1  # Lower temperature for more consistent scoring
        )
        
        return int(response.choices[0].message.content.strip())
    
    except:
        return 2  # Default to below average if error