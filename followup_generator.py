import json
import random
import openai
from sentence_transformers import SentenceTransformer
import numpy as np
from config import OPENAI_API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE
from knowledge_base import get_concept_for_question

openai.api_key = OPENAI_API_KEY

class FollowupGenerator:
    def __init__(self, patterns_file='data/followup_patterns.json'):
        self.patterns = self.load_patterns(patterns_file)
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.setup_embeddings()
    
    def load_patterns(self, filepath):
        """Load followup patterns from JSON file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: {filepath} not found. Using empty patterns.")
            return {}
    
    def setup_embeddings(self):
        """Create embeddings for all followup patterns for RAG retrieval"""
        all_patterns = []
        self.pattern_metadata = []
        
        for concept, categories in self.patterns.items():
            for category, questions in categories.items():
                for question in questions:
                    all_patterns.append(question)
                    self.pattern_metadata.append({
                        'concept': concept,
                        'category': category,
                        'question': question
                    })
        
        if all_patterns:
            self.pattern_embeddings = self.embedder.encode(all_patterns, normalize_embeddings= True) # normalise for cosine sim instead of plain dot product
        else:
            self.pattern_embeddings = np.array([])
    
    def determine_followup_type(self, quality_score, feedback):
        """Determine what type of follow-up question to ask"""
        if quality_score >= 4:
            return "advanced_application"
        elif quality_score <= 2:
            return "clarification" 
        else:
            # Look for gaps in feedback to determine type
            feedback_lower = feedback.lower()
            if "missing" in feedback_lower or "add" in feedback_lower:
                return "gap_filling"
            elif "unclear" in feedback_lower or "confusing" in feedback_lower:
                return "clarification"
            else:
                return "gap_filling"
    
    def retrieve_relevant_patterns(self, original_question, user_answer, followup_type, top_k=3):
        """Use RAG to retrieve most relevant follow-up patterns (cosine + small boosts)."""
        if len(self.pattern_embeddings) == 0:
            return []

        # 1) Query embedding (unit-normalised) → cosine similarity in [-1, 1]
        query_text = f"{original_question} {user_answer}"
        query_embedding = self.embedder.encode([query_text], normalize_embeddings=True)  # shape (1, d)
        sim = (query_embedding @ self.pattern_embeddings.T).ravel()  # cosine in [-1, 1]

        # 2) Concept/type features (vectorised)
        concept = self.get_concept_from_question(original_question)
        concept_match = np.array([m['concept'] == concept for m in self.pattern_metadata], dtype=np.float32)
        type_match    = np.array([m['category'] == followup_type for m in self.pattern_metadata], dtype=np.float32)

        # 3) Prefer same concept: if any exist (and concept not "general"), restrict ranking to them
        if concept != "general" and concept_match.any():
            mask = concept_match.astype(bool)
        else:
            mask = np.ones_like(sim, dtype=bool)

        # 4) Blend similarity (mapped to [0,1]) with small boosts so sim stays dominant
        sim01 = (sim + 1.0) / 2.0  # [-1,1] → [0,1]
        w_sim, w_concept, w_type = 0.85, 0.10, 0.05
        final = w_sim * sim01 + w_concept * concept_match + w_type * type_match

        # 5) Rank within mask and return top_k
        idx = np.where(mask)[0]
        if idx.size == 0:
            return []
        top = idx[np.argsort(final[idx])[-min(top_k, idx.size):][::-1]]
        return [self.pattern_metadata[i] for i in top]

    
    def get_concept_from_question(self, question_text):
        """Extract concept key from question text"""
        question_lower = question_text.lower()
        
        concept_mapping = {
            "type i and type ii errors": "type_i_ii_errors",
            "p-value": "p_value", 
            "central limit theorem": "central_limit_theorem",
            "correlation and causation": "correlation_vs_causation",
            "bias-variance tradeoff": "bias_variance_tradeoff",
            "class imbalance": "class_imbalance",
            "bagging and boosting": "bagging_vs_boosting",
            "linear regression": "linear_regression_assumptions",
            "a/b test": "ab_test_design",
            "missing": "missing_data_handling"
        }
        
        for keyword, concept in concept_mapping.items():
            if keyword in question_lower:
                return concept
        
        return "general"
    
    def generate_followup_question(self, original_question, user_answer, feedback, quality_score):
        """Generate contextual follow-up question using RAG and LLM"""
        
        # Determine type of follow-up needed
        followup_type = self.determine_followup_type(quality_score, feedback)
        
        # Retrieve relevant patterns using RAG
        relevant_patterns = self.retrieve_relevant_patterns(
            original_question, user_answer, followup_type, top_k=3
        )
        
        # Create context from retrieved patterns
        if relevant_patterns:
            pattern_context = "Similar follow-up questions from interview database:\n"
            for pattern in relevant_patterns:
                pattern_context += f"- {pattern['question']} (Category: {pattern['category']})\n"
        else:
            pattern_context = "No specific patterns found."
        
        # Get concept knowledge for additional context
        concept_knowledge = get_concept_for_question(original_question)
        concept_context = ""
        if concept_knowledge:
            concept_context = f"Key concept areas: {', '.join(concept_knowledge.get('key_points', []))}"
        
        # Generate follow-up using LLM
        followup_prompt = f"""
        You are conducting a technical interview. Based on the candidate's answer, generate ONE natural follow-up question.
        
        ORIGINAL QUESTION: {original_question}
        CANDIDATE'S ANSWER: {user_answer}
        ANSWER QUALITY: {quality_score}/5
        FEEDBACK GIVEN: {feedback}
        FOLLOWUP TYPE NEEDED: {followup_type}
        
        {pattern_context}
        
        {concept_context}
        
        Generate a single, specific follow-up question that:
        1. Builds naturally on their answer
        2. Tests deeper understanding ({followup_type})
        3. Feels like a real interview conversation
        4. Is different from the original question
        
        Return only the question, no extra text.
        """
        
        try:
            response = openai.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer. Generate natural, probing follow-up questions."},
                    {"role": "user", "content": followup_prompt}
                ],
                max_tokens=150,
                temperature=TEMPERATURE
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback to pattern-based selection
            concept = self.get_concept_from_question(original_question)
            if concept in self.patterns and followup_type in self.patterns[concept]:
                return random.choice(self.patterns[concept][followup_type])
            else:
                return "Can you elaborate more on that concept?"
    
    def should_ask_followup(self, quality_score, feedback, is_revision=False):
        """Determine if a follow-up question is warranted"""
        # For initial poor answers, encourage revision first (no follow-up yet)
        if quality_score <= 2 and not is_revision:
            return False  # Let them improve their answer first
        
        # Don't ask follow-up if answer is already excellent
        if quality_score >= 5:
            return False
        
        # For revised answers (even if still not perfect) or decent initial answers, ask follow-up
        if quality_score >= 3 or is_revision:
            return True
            
        return False

# Convenience function for easy import
def generate_followup_question(original_question, user_answer, feedback, quality_score, is_revision=False):
    """Convenience function to generate follow-up question"""
    generator = FollowupGenerator()
    
    if not generator.should_ask_followup(quality_score, feedback, is_revision):
        return None
        
    return generator.generate_followup_question(original_question, user_answer, feedback, quality_score)