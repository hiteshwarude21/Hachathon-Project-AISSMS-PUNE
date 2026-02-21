#!/usr/bin/env python3
"""
Advanced Agriculture Schemes Database
Structured JSON format for intelligent scheme recommendations
"""

schemes_database = {
    "insurance": [
        {
            "name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
            "category": "insurance",
            "benefits": "Crop insurance premium subsidy, claims for crop loss due to natural calamities, pests, diseases",
            "eligibility": "All farmers growing notified crops, sharecroppers, tenant farmers",
            "apply_process": "Contact nearest bank/insurance company, submit land records, crop details",
            "state_filter": "All India",
            "keywords": ["crop loss", "insurance", "damage", "flood", "drought", "pest", "disease"]
        },
        {
            "name": "Weather Based Crop Insurance Scheme (WBCIS)",
            "category": "insurance", 
            "benefits": "Automatic payout based on weather parameters, no claim assessment required",
            "eligibility": "Farmers with Kisan Credit Card, growing notified crops",
            "apply_process": "Enroll through bank, link with KCC, automatic weather monitoring",
            "state_filter": "All India",
            "keywords": ["weather", "rain", "temperature", "automatic", "no claim"]
        }
    ],
    
    "financial_support": [
        {
            "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
            "category": "financial_support",
            "benefits": "Direct income support of ₹6,000 per year in 3 installments",
            "eligibility": "Small and marginal farmers with landholding up to 2 hectares",
            "apply_process": "Register with local revenue officer, submit land documents, bank account",
            "state_filter": "All India",
            "keywords": ["income", "money", "support", "direct benefit", "6000"]
        },
        {
            "name": "Kisan Credit Card (KCC)",
            "category": "financial_support",
            "benefits": "Crop loan up to ₹3 lakh, interest subvention 2% per annum, flexible repayment",
            "eligibility": "All farmers including sharecroppers, tenant farmers",
            "apply_process": "Apply to nearest bank, submit land records, identity proof",
            "state_filter": "All India",
            "keywords": ["loan", "credit", "kcc", "interest", "bank", "money"]
        },
        {
            "name": "Agriculture Infrastructure Fund",
            "category": "financial_support",
            "benefits": "Financing for farm infrastructure, warehouses, cold storage, processing units",
            "eligibility": "Farmer groups, cooperatives, agri-entrepreneurs",
            "apply_process": "Submit project proposal to NABARD, get bank financing",
            "state_filter": "All India",
            "keywords": ["infrastructure", "warehouse", "storage", "processing", "investment"]
        }
    ],
    
    "irrigation": [
        {
            "name": "Pradhan Mantri Krishi Sinchai Yojana (PMKSY)",
            "category": "irrigation",
            "benefits": "Financial assistance for irrigation equipment, drip/sprinkler systems, wells",
            "eligibility": "All farmers, priority to small and marginal farmers",
            "apply_process": "Apply through agriculture department, submit land records, irrigation plan",
            "state_filter": "All India",
            "keywords": ["water", "irrigation", "pump", "drip", "sprinkler", "well"]
        },
        {
            "name": "Per Drop More Crop (PDMC)",
            "category": "irrigation",
            "benefits": "Micro-irrigation subsidy up to 55% for small farmers, 45% for others",
            "eligibility": "All farmers with access to water source",
            "apply_process": "Apply through state horticulture department, install micro-irrigation",
            "state_filter": "All India",
            "keywords": ["micro irrigation", "drip", "sprinkler", "water saving", "efficiency"]
        },
        {
            "name": "Atal Bhujal Yojana (ABY)",
            "category": "irrigation",
            "benefits": "Ground water management, water conservation, recharge structures",
            "eligibility": "Village communities, farmer groups, water user associations",
            "apply_process": "Community-based application through district administration",
            "state_filter": "Selected states",
            "keywords": ["ground water", "recharge", "conservation", "community", "village"]
        }
    ],
    
    "subsidy_development": [
        {
            "name": "Rashtriya Krishi Vikas Yojana (RKVY)",
            "category": "subsidy_development",
            "benefits": "Subsidy for farm mechanization, infrastructure development, training",
            "eligibility": "All farmers, farmer groups, state governments",
            "apply_process": "Apply through state agriculture department, project-based funding",
            "state_filter": "All India",
            "keywords": ["development", "mechanization", "training", "infrastructure", "subsidy"]
        },
        {
            "name": "Sub-Mission on Agricultural Mechanization (SMAM)",
            "category": "subsidy_development",
            "benefits": "Subsidy up to 50% for farm machinery, custom hiring centers",
            "eligibility": "Individual farmers, farmer groups, entrepreneurs",
            "apply_process": "Apply through state agriculture department, purchase approved machinery",
            "state_filter": "All India",
            "keywords": ["machinery", "equipment", "tractor", "hiring center", "mechanization"]
        }
    ],
    
    "livestock_allied": [
        {
            "name": "National Livestock Mission",
            "category": "livestock_allied",
            "benefits": "Subsidy for livestock breeding, health, fodder development, insurance",
            "eligibility": "Livestock farmers, dairy farmers, poultry farmers",
            "apply_process": "Apply through animal husbandry department, submit livestock details",
            "state_filter": "All India",
            "keywords": ["animal", "livestock", "dairy", "poultry", "breeding", "fodder"]
        },
        {
            "name": "Pradhan Mantri Matsya Sampada Yojana (PMMSY)",
            "category": "livestock_allied",
            "benefits": "Financial assistance for fish farming, aquaculture, infrastructure",
            "eligibility": "Fish farmers, aquaculture entrepreneurs, fisher communities",
            "apply_process": "Apply through fisheries department, submit project proposal",
            "state_filter": "All India",
            "keywords": ["fish", "aquaculture", "fisheries", "pond", "aquatic"]
        }
    ]
}

# Intent detection mapping
intent_keywords = {
    "insurance": ["insurance", "crop loss", "damage", "flood", "drought", "pest", "disease", "weather", "rain", "crop damaged", "crop failure", "natural calamity"],
    "financial_support": ["loan", "money", "credit", "kcc", "income", "support", "financial", "bank", "cash", "fund", "investment", "capital"],
    "irrigation": ["water", "irrigation", "pump", "drip", "sprinkler", "well", "conservation", "water shortage", "water problem", "drought", "rainfall"],
    "subsidy_development": ["subsidy", "machinery", "equipment", "tractor", "mechanization", "development", "modern farming", "technology", "tools"],
    "livestock_allied": ["animal", "livestock", "dairy", "poultry", "fish", "aquaculture", "cattle", "goat", "chicken", "pond"]
}

def get_schemes_by_intent(intent):
    """Get schemes matching detected intent"""
    if intent in schemes_database:
        return schemes_database[intent]
    return []

def get_all_schemes():
    """Get all schemes for comprehensive search"""
    all_schemes = []
    for category in schemes_database.values():
        all_schemes.extend(category)
    return all_schemes

def detect_intent(message):
    """Detect user intent from message"""
    message_lower = message.lower()
    
    for intent, keywords in intent_keywords.items():
        for keyword in keywords:
            if keyword in message_lower:
                return intent
    
    return "general"
