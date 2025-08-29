from config import client, MODEL_NAME, MAX_TOKENS, TEMPERATURE
from knowledge_base import get_feedback_context, get_concept_for_question

def generate_feedback(question, user_answer, iteration=1):
    """Generate structured feedback for a user's answer"""

    # Get concept knowledge 
    concept = get_concept_for_question(question)
    context_parts = []
    if concept:
        if 'key_points' in concept and concept['key_points']:
            # Take top 3 key points
            points = concept['key_points'][:3]
            context_parts.append(f"Key points that should be covered: {', '.join(points)}")
        
        if 'interview_red_flags' in concept and concept['interview_red_flags']:
            context_parts.append(f"Common mistakes to watch for: {', '.join(concept['interview_red_flags'])}")
    
    # Only add context if we have it
    kb_context = '\n'.join(context_parts) if context_parts else ""
    
    feedback_prompt = f"""
    You are a friendly data science interview coach giving conversational feedback.
    
    QUESTION: {question}
    STUDENT ANSWER: {user_answer}
    ATTEMPT: {iteration}

    {kb_context} 
    
    Provide brief, encouraging feedback directly to the student (use "you", not "the candidate"):
    
    1. POSITIVE: Start with something they got right or showed understanding of
    2. KEY GAP: Identify the most important thing they missed (don't explain it fully)
    3. NEXT STEP: Give ONE specific suggestion to improve their answer (avoid the red_flags listed)
    
    Keep it conversational, supportive, and concise (max 4-5 sentences). Don't give away the full answer - guide them to discover it.
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a supportive interview coach. Be conversational, brief, and encouraging."},
                {"role": "user", "content": feedback_prompt}
            ],
            max_tokens=250,  
            temperature=TEMPERATURE
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating feedback: {str(e)}"

def evaluate_answer_quality(question, user_answer):
    """Quick evaluation to determine if answer needs improvement"""
    concept = get_concept_for_question(question)

    key_points_text = "General data science knowledge expected"
    red_flags_text = "Standard interview evaluation criteria"

    if concept:
        if 'key_points' in concept:
            key_points_text = ', '.join(concept['key_points'])
        if 'interview_red_flags' in concept:
            red_flags_text = ', '.join(concept['interview_red_flags'])

    
    eval_prompt = f"""
    Rate this data science interview answer strictly on a 1-5 scale:

    QUESTION: {question}
    ANSWER: {user_answer}

    EXPECTED KEY POINTS:
    {key_points_text}

    RED FLAGS TO PENALIZE:
    {red_flags_text}
    
    1 = Very poor (major gaps, oversimplified, or major red flags present)
    2 = Poor (shows some awareness but significant issues)
    3 = Average (covers basics but lacks depth/examples)
    4 = Good (solid understanding with minor gaps)
    5 = Excellent (comprehensive, accurate, well-explained)
    
    Be harsh but fair - most real interview answers are 2-3/5.
    
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