# Bleach Mobile 3D Expert Knowledge Base

CHARACTERS = {
    "sp aizen": {
        "name": "SP Aizen (Final Fusion)",
        "build": {
            "main": "SP Aizen (Final Fusion)",
            "assists": ["Bankai Shinji", "Halloween Nelliel"],
            "guards": ["Genryusai Yamamoto", "Sosuke Aizen (Throne)"],
            "cards": ["Final Fusion", "God of Destruction", "Hogyoku's Will"],
            "bonds": {
                "attack": ["Ichigo Kurosaki (Mugetsu)", "Gin Ichimaru"],
                "hp": ["Momo Hinamori", "Kaname Tosen"],
                "defense": ["Barragan Louisenbairn", "Tier Halibel"]
            }
        }
    },
    "tensa": {
        "name": "Tensa Zangetsu",
        "build": {
            "main": "Tensa Zangetsu",
            "assists": ["White Ichigo", "Yoruichi (Armor)"],
            "guards": ["Kisuke Urahara", "Isshin Kurosaki"],
            "cards": ["Zangetsu's Power", "Inner Hollow", "Bankai Training"],
            "bonds": {
                "attack": ["Ichigo Kurosaki", "Old Man Zangetsu"],
                "hp": ["Orihime Inoue", "Yasutora Sado"],
                "defense": ["Uryu Ishida", "Shunsui Kyoraku"]
            }
        }
    }
}

CARDS = {
    "final fusion": {
        "name": "Final Fusion",
        "type": "Attack / Special",
        "skills": {
            "skill1": {
                "effect": "Increases ATK by 15% for 10 seconds.",
                "usage": "Use at the start of the combo to maximize burst.",
                "situation": "Perfect for PvP opening and Boss rushes."
            },
            "skill2": {
                "effect": "Reduces enemy Defense by 20%.",
                "usage": "Follow up after Skill 1 for maximum damage impact.",
                "situation": "Effective against tanky builds and high-armor guards."
            },
            "skill3": {
                "effect": "Ignores 30% of target's block and adds 5% life steal.",
                "usage": "The ultimate sustain skill. Keeps you alive while finishing targets.",
                "advantages": "Makes SP Aizen almost immortal in 1v1 scenarios."
            }
        },
        "advantages": "Extreme damage multiplier, defense shred, and high sustain via life steal.",
        "disadvantages": "High cooldown if interrupted. Weak against silence effects.",
        "meta_usage": "Core card for SP Aizen and top-tier ATK builds in current PvP meta.",
        "counters": {
            "strong_against": ["Tanky Guards", "Low-mobility Characters"],
            "countered_by": ["Silence Cards", "Stun-locking Combos"]
        },
        "bonds": {
            "attack": ["Hogyoku", "Butterfly Aizen"],
            "hp": ["Gin Ichimaru"],
            "defense": ["Tosen"]
        },
        "best_builds": {
            "main": ["SP Aizen", "Mugetsu"],
            "assists": ["Nelliel"],
            "guards": ["Yamamoto"]
        },
        "rating": {
            "overall": "9.5/10",
            "pvp": "10/10",
            "pve": "9/10",
            "priority": "Highest"
        },
        "availability": {
            "status": "Available now",
            "cycle_days": 30 # Example: cycles every 30 days
        }
    }
}

# General knowledge base for the "AI" to answer common questions
GENERAL_KNOWLEDGE = {
    "how to get sp characters": "SP characters can be obtained through Special Gacha events, typically rotating every 2 weeks. Save your crystals!",
    "best build for beginners": "Focus on Ichigo (Vasto Lorde) or Ulquiorra (Resurrección). They are easier to build and very effective in early-mid game.",
    "what are guards": "Guards provide defensive stats and special protective skills when your health drops below a certain threshold."
}
