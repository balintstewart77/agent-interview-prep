INTERVIEW_CONCEPTS = {
    "type_i_ii_errors": {
        "definition": "Type I: False positive (rejecting true null hypothesis). Type II: False negative (failing to reject false null hypothesis)",
        "key_points": [
            "Type I (α): Saying there's an effect when there isn't",
            "Type II (β): Missing an effect that exists",
            "Power = 1 - β (ability to detect true effects)",
            "Setting α affects β inversely"
        ],
        "examples": {
            "type_i": "Medical test says you have disease when you don't (false alarm)",
            "type_ii": "Medical test misses disease you actually have",
            "business": "A/B test says feature works when it doesn't vs missing a successful feature"
        },
        "practical_application": "Choose α based on cost of false positives vs false negatives in business context",
        "interview_red_flags": [
            "Confusing which is which",
            "No real-world examples", 
            "Not discussing business trade-offs"
        ]
    },
    
    "p_value": {
        "definition": "Probability of observing test results at least as extreme as observed, assuming null hypothesis is true",
        "key_points": [
            "NOT the probability that null hypothesis is true",
            "Lower p-value = stronger evidence against null hypothesis",
            "Threshold (usually 0.05) is arbitrary",
            "Affected by sample size"
        ],
        "common_misunderstandings": [
            "P(H0|data) - this is backwards",
            "P-hacking and multiple testing issues",
            "Statistical vs practical significance confusion"
        ],
        "practical_application": "Use alongside effect size and confidence intervals for complete picture",
        "interview_red_flags": [
            "Defining as probability null is true",
            "Not mentioning p-hacking risks",
            "Ignoring practical significance"
        ]
    },
    
    "central_limit_theorem": {
        "definition": "Sample means approach normal distribution as sample size increases, regardless of population distribution",
        "key_points": [
            "Works for any population distribution shape",
            "Sample size ~30 often sufficient",
            "Standard error = σ/√n",
            "Foundation for confidence intervals and hypothesis testing"
        ],
        "importance_for_ds": [
            "Enables statistical inference on non-normal data",
            "Justifies normal approximations in modeling",
            "Critical for bootstrap methods and sampling theory"
        ],
        "practical_application": "Allows us to make probabilistic statements about sample statistics",
        "interview_red_flags": [
            "Saying original data becomes normal",
            "Not explaining why it matters for data science",
            "Missing the sampling distribution concept"
        ]
    },
    
    "correlation_vs_causation": {
        "definition": "Correlation measures linear relationship strength; causation implies one variable directly influences another",
        "key_points": [
            "Correlation ≠ causation",
            "Confounding variables can create spurious correlations",
            "Temporal order matters for causation",
            "Randomized experiments can establish causation"
        ],
        "examples": {
            "spurious": "Ice cream sales and drowning deaths (both increase in summer)",
            "confounding": "Coffee and heart disease (lifestyle factors)",
            "reverse_causation": "Does success cause confidence or vice versa?"
        },
        "establishing_causation": [
            "Randomized controlled trials",
            "Natural experiments", 
            "Causal inference methods (IV, regression discontinuity)"
        ],
        "interview_red_flags": [
            "Using correlation to imply causation",
            "No mention of confounding variables",
            "Not discussing experimental design"
        ]
    },
    
    "bias_variance_tradeoff": {
        "definition": "The fundamental tradeoff between a model's bias (underfitting) and variance (overfitting)",
        "key_points": [
            "Bias: error from overly simplistic assumptions",
            "Variance: error from sensitivity to training data changes",
            "Total error = bias² + variance + irreducible error",
            "Cannot minimize both simultaneously"
        ],
        "examples": {
            "high_bias": "Linear regression on non-linear data",
            "high_variance": "Deep neural network on small dataset",
            "balanced": "Random forest with proper hyperparameters"
        },
        "practical_application": [
            "Use learning curves to diagnose",
            "Cross-validation to evaluate",
            "Regularization to reduce variance",
            "Feature engineering to reduce bias"
        ],
        "interview_red_flags": [
            "Confusing with statistical bias",
            "No practical examples or diagnostics",
            "Missing the fundamental tradeoff"
        ]
    },
    
    "class_imbalance": {
        "definition": "When target classes are not represented equally in the dataset",
        "key_points": [
            "Accuracy becomes misleading metric",
            "Model may just predict majority class",
            "Need different evaluation metrics",
            "Multiple handling techniques available"
        ],
        "techniques": {
            "sampling": "SMOTE, oversampling, undersampling",
            "algorithmic": "Class weights, cost-sensitive learning",
            "ensemble": "Balanced bagging, boosting variations"
        },
        "evaluation_metrics": [
            "Precision, recall, F1-score",
            "AUC-ROC, AUC-PR curves", 
            "Balanced accuracy"
        ],
        "practical_application": "Choose technique based on dataset size, domain constraints, and business costs",
        "interview_red_flags": [
            "Only mentioning accuracy",
            "Not discussing business implications",
            "Ignoring evaluation metric changes"
        ]
    },
    
    "bagging_vs_boosting": {
        "definition": "Bagging: parallel weak learners on bootstrap samples. Boosting: sequential weak learners focusing on mistakes",
        "bagging": {
            "how_it_works": "Train multiple models on bootstrap samples, average predictions",
            "examples": "Random Forest, Extra Trees",
            "strengths": "Reduces variance, parallelizable, handles overfitting",
            "weaknesses": "May not improve bias much"
        },
        "boosting": {
            "how_it_works": "Sequential training where each model corrects previous errors",
            "examples": "AdaBoost, Gradient Boosting, XGBoost",
            "strengths": "Reduces bias and variance, often higher accuracy",
            "weaknesses": "Prone to overfitting, sensitive to noise"
        },
        "when_to_use": {
            "bagging": "High variance models, noisy data, parallel processing available",
            "boosting": "High bias models, clean data, need maximum accuracy"
        },
        "interview_red_flags": [
            "Confusing the sequential vs parallel nature",
            "Not mentioning specific algorithms",
            "Missing bias/variance implications"
        ]
    },
    
    "linear_regression_assumptions": {
        "definition": "Key assumptions that must hold for linear regression to provide reliable results",
        "assumptions": {
            "linearity": "Relationship between features and target is linear",
            "independence": "Observations are independent of each other",
            "homoscedasticity": "Constant variance of residuals",
            "normality": "Residuals are normally distributed",
            "no_multicollinearity": "Features are not highly correlated"
        },
        "diagnostics": {
            "linearity": "Residuals vs fitted plots, partial regression plots",
            "independence": "Durbin-Watson test, residual autocorrelation",
            "homoscedasticity": "Scale-location plots, Breusch-Pagan test", 
            "normality": "Q-Q plots, Shapiro-Wilk test",
            "multicollinearity": "VIF (Variance Inflation Factor), correlation matrix"
        },
        "violations_solutions": {
            "non_linearity": "Polynomial features, splines, transformations",
            "heteroscedasticity": "Weighted least squares, robust standard errors",
            "non_normality": "Data transformation, robust regression",
            "multicollinearity": "Ridge regression, feature selection, PCA"
        },
        "interview_red_flags": [
            "Forgetting key assumptions",
            "Not knowing how to test assumptions",
            "No solutions for violations"
        ]
    },
    
    "ab_test_design": {
        "definition": "Controlled experiment to compare two or more variants to determine which performs better",
        "key_components": [
            "Clear hypothesis and success metrics",
            "Random assignment to treatment/control",
            "Sufficient sample size (power analysis)",
            "Statistical significance testing"
        ],
        "design_process": [
            "Define hypothesis and metrics",
            "Calculate required sample size",
            "Randomize user assignment", 
            "Run test for predetermined duration",
            "Analyze results with proper statistics"
        ],
        "common_pitfalls": [
            "Multiple testing without correction",
            "Peeking at results early",
            "Insufficient sample size",
            "Selection bias in randomization"
        ],
        "practical_considerations": [
            "Seasonality effects",
            "Network effects", 
            "Segment-specific impacts",
            "Business metric alignment"
        ],
        "interview_red_flags": [
            "No mention of randomization",
            "Ignoring statistical power",
            "Not discussing potential biases"
        ]
    },
    
    "missing_data_handling": {
        "definition": "Systematic approach to deal with incomplete data in datasets",
        "missing_data_types": {
            "MCAR": "Missing Completely At Random - missing independent of observed/unobserved data",
            "MAR": "Missing At Random - missing depends on observed data only", 
            "MNAR": "Missing Not At Random - missing depends on unobserved data"
        },
        "analysis_steps": [
            "Understand missingness pattern and mechanism",
            "Assess impact on analysis (40% is substantial)", 
            "Choose appropriate handling strategy",
            "Validate approach and document assumptions"
        ],
        "handling_strategies": {
            "deletion": "Listwise/pairwise deletion (if MCAR and <5% missing)",
            "imputation": "Mean/median/mode, KNN, regression imputation",
            "advanced": "Multiple imputation, model-based methods",
            "domain_specific": "Forward fill, interpolation for time series"
        },
        "key_considerations": [
            "Preserve relationships between variables",
            "Don't introduce bias",
            "Consider uncertainty from imputation",
            "Business domain knowledge crucial"
        ],
        "interview_red_flags": [
            "Just deleting rows without analysis",
            "Not understanding missingness types",
            "No justification for chosen method"
        ]
    }
}

def get_concept_for_question(question_text):
    """Match question to relevant concept(s)"""
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
            return INTERVIEW_CONCEPTS.get(concept)
    
    return None

def get_feedback_context(question_text):
    """Get relevant knowledge base context for generating feedback"""
    concept = get_concept_for_question(question_text)
    
    if concept:
        context = f"""
RELEVANT CONCEPT KNOWLEDGE:
Definition: {concept['definition']}

Key Points: {', '.join(concept['key_points'])}

Common Interview Red Flags: {', '.join(concept['interview_red_flags'])}

Practical Application: {concept.get('practical_application', 'N/A')}
"""
        return context
    
    return "No specific concept knowledge found."