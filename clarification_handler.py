from config import client, MODEL_NAME
from knowledge_base import get_feedback_context

def generate_clarification(original_question, student_answer, student_question):
    """
    Generate a clarification response to help students understand concepts.
    
    Args:
        original_question (str): The original interview question
        student_answer (str): The student's most recent answer
        student_question (str): The clarification question asked by student
    
    Returns:
        str: Clarification response
    """
    try:
        # Get relevant knowledge base context
        context = get_feedback_context(original_question)
        
        clarification_prompt = f"""
        You are a patient data science tutor helping a student understand concepts.
        
        ORIGINAL INTERVIEW QUESTION: {original_question}
        THEIR RECENT ANSWER: {student_answer}
        STUDENT'S QUESTION: {student_question}
        
        RELEVANT KNOWLEDGE:
        {context}
        
        Provide a clear, helpful explanation that:
        1. Directly answers their specific question
        2. Uses concrete examples
        3. References their previous answer to build understanding
        4. Keeps it concise and interview-focused
        
        Be conversational and supportive.
        """
        
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a supportive data science tutor who gives clear explanations with examples."},
                {"role": "user", "content": clarification_prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error providing clarification: {str(e)}"

def is_valid_clarification_question(question):
    """
    Basic validation for clarification questions.
    
    Args:
        question (str): The student's question
    
    Returns:
        bool: True if question seems valid
    """
    if not question or len(question.strip()) < 5:
        return False
    
    # Could add more sophisticated validation here
    return True