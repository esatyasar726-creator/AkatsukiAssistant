import json
import os
import logging
from fuzzywuzzy import process

class DataManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.data = {}
        self.load_all()

    def load_all(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            return

        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                key = filename.replace(".json", "")
                filepath = os.path.join(self.data_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        self.data[key] = json.load(f)
                    logging.info(f"Loaded {filename} successfully.")
                except Exception as e:
                    logging.error(f"Error loading {filename}: {e}")

    def get_collection(self, collection_name):
        return self.data.get(collection_name, {})

    def find_item(self, collection_name, query):
        collection = self.get_collection(collection_name)
        if not collection:
            return None

        choices = list(collection.keys())
        if not choices: return None

        # 1. Clean query exact match
        query_clean = query.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_")
        best_match = None
        if query_clean in choices:
            best_match = query_clean
        else:
            # 2. Word-subset matching (very precise for multi-word queries like "sp aizen")
            query_words = [w for w in query.lower().replace("_", " ").replace("-", " ").replace("(", " ").replace(")", " ").split() if w]
            for choice in choices:
                choice_words = choice.lower().replace("_", " ").split()
                if all(qw in choice_words or any(qw in cw for cw in choice_words) for qw in query_words):
                    best_match = choice
                    break

            # 3. Fuzzy matching fallback
            if not best_match:
                bm, score = process.extractOne(query.lower(), choices)
                if score >= 70:  # Threshold for fuzzy match
                    best_match = bm

        if best_match:
            item = collection[best_match]
            if collection_name == "characters":
                return self.enrich_character(item)
            elif collection_name == "cards":
                return self.enrich_card(item)
            return item
        return None

    def enrich_character(self, char):
        # Create a deep-ish copy/enriched version to prevent modifying base loaded data
        enriched = dict(char)

        name = enriched.get("name", "Unknown Character")
        name_lower = name.lower()

        # Determine Bleach Group/Lore based on name
        lore = "shinigami"
        if any(x in name_lower for x in ["aizen", "ichigo", "byakuya", "gin", "yamamoto", "shunsui", "hitsugaya", "toshiro", "yoruichi", "kisuke", "shinji", "rukia", "tensa", "mugetsu", "kenpachi"]):
            lore = "shinigami"
        elif any(x in name_lower for x in ["barragan", "halibel", "starrk", "ulquiorra", "grimmjow", "nelliel", "nel", "szayelaporro", "nnoitra", "yammy"]):
            lore = "espada"
        elif any(x in name_lower for x in ["uryu", "yhwach", "jugram", "bazz", "bambietta"]):
            lore = "quincy"

        # Base templates
        templates = {
            "shinigami": {
                "assists": ["Mugetsu (Ichigo Kurosaki)", "SP Shinji Hirako", "Yoruichi Shihoin (Armor)"],
                "guards": ["Kisuke Urahara (Shopkeeper)", "Genryusai Yamamoto", "Shunsui Kyoraku (Captain)"],
                "cards": ["Final Fusion", "God of Destruction", "Hogyoku's Will", "Zangetsu's Power"],
                "attack_bonds": ["Ichigo Kurosaki (Mugetsu)", "Byakuya Kuchiki", "Sosuke Aizen", "Kenpachi Zaraki", "Toshiro Hitsugaya", "Renji Abarai"],
                "hp_bonds": ["Rukia Kuchiki", "Orihime Inoue", "Momo Hinamori", "Yasutora Sado", "Rangiku Matsumoto", "Yoruichi Shihoin"],
                "defense_bonds": ["Kisuke Urahara", "Shunsui Kyoraku", "Jushiro Ukitake", "Sajin Komamura", "Kaname Tosen", "Mayuri Kurotsuchi"],
                "gear": ["Gotei Captain Haori", "Zanpakuto Spirit Essence", "Soul Cutter Blade"],
                "accessories": ["Kuchiki Heirloom Scarf", "Gotei 13 Badge", "Reishi Condenser Ring"],
                "tips": "Initiate with Skill 1 for the attack buff, then follow up with Skill 2 to shred defense. Use Skill 3 (Weapon) for invincibility frames during high-damage enemy phases.",
                "strengths": "Exceptional AOE clears, high burst potential, strong utility buffs and crowd control (Freeze/Silence).",
                "weaknesses": "Vulnerable to hard crowd control during skill startup animations, cooldown dependent.",
                "counters": "High evasion characters and silence-locking setups.",
                "synergies": "SP Shinji for defense reduction, SP Yamamoto for continuous burn damage.",
                "investment": "Highest Priority (SSS Class)",
                "pvp_rating": "9.8 / 10 (Meta)",
                "pve_rating": "9.6 / 10 (S-Class)"
            },
            "espada": {
                "assists": ["Tier Halibel (Resurrección)", "Coyote Starrk", "Ulquiorra Cifer (R2)"],
                "guards": ["Sosuke Aizen (Throne)", "Kaname Tosen", "Gin Ichimaru"],
                "cards": ["Final Fusion", "Arrogante's Curse", "Gran Rey Cero", "Hogyoku's Will"],
                "attack_bonds": ["Coyote Starrk", "Tier Halibel", "Ulquiorra Cifer", "Grimmjow Jaegerjaquez", "Yammy Llargo", "Sosuke Aizen"],
                "hp_bonds": ["Nel Tu", "Charlotte Chuhlhourne", "Findorr Calius", "Ggio Vega", "Nirgge Parduoc", "Abirama Redder"],
                "defense_bonds": ["Kaname Tosen", "Zommari Rureaux", "Aaroniero Arruruerie", "Nnoitra Gilga", "Szayelaporro Granz", "Baraggan Louisenbairn"],
                "gear": ["Espada Hollow Armor", "Resurrección Release Catalyst", "Caja Negativa Key"],
                "accessories": ["Crown of Las Noches", "Hollow Mask Fragment", "Arrogante Ring"],
                "tips": "Utilize Hollow release forms to gain passive lifesteal and crowd control immunity. Combine skills to corner enemies before unleashing your ultimate.",
                "strengths": "Exceptional passive sustainability (lifesteal), high armor breaking, and immune to silence during release.",
                "weaknesses": "Slow starter before liberation/transformation, vulnerable to fast rush builds.",
                "counters": "Aggressive speed rush builds and freeze-focused characters.",
                "synergies": "Sosuke Aizen for stat boosts, Kaname Tosen for crowd control support.",
                "investment": "S-Tier Priority (High Investment Required)",
                "pvp_rating": "9.6 / 10",
                "pve_rating": "9.4 / 10"
            },
            "quincy": {
                "assists": ["Jugram Haschwalth", "Bazz-B", "As Nodt"],
                "guards": ["Yhwach (Almighty)", "Uryu Ishida", "Gerard Valkyrie"],
                "cards": ["Heilig Pfeil Blessing", "Vandenreich Cloak", "Letzt Stil Power"],
                "attack_bonds": ["Yhwach", "Jugram Haschwalth", "Bazz-B", "Lille Barro", "Gerard Valkyrie", "Askin Nakk Le Vaar"],
                "hp_bonds": ["Uryu Ishida", "Ryuken Ishida", "Bambietta Basterbine", "Candice Catnipp", "Giselle Gewelle", "Liltotto Lamperd"],
                "defense_bonds": ["Quincy King Guard", "Mask De Masculine", "Robert Accutrone", "Cang Du", "BG9", "Driscoll Berci"],
                "gear": ["Vandenreich Officer Coat", "Sanrei Glove", "Seele Schneider"],
                "accessories": ["Quincy Cross Pendant", "Heilig Bogen Badge", "Reishi Collector ring"],
                "tips": "Utilize long range bow attacks to stack pierce buffs. Maintain maximum distance and use defensive guards when pressured.",
                "strengths": "Extreme single-target pierce damage, long attack range, and self-dispel abilities.",
                "weaknesses": "Low base physical defense, highly vulnerable when cornered in close quarters.",
                "counters": "High speed melee gap-closers (like Yoruichi).",
                "synergies": "Yhwach for massive stat amplification, Jugram Haschwalth for damage deflection.",
                "investment": "Top-Tier High Priority",
                "pvp_rating": "9.7 / 10",
                "pve_rating": "9.3 / 10"
            }
        }

        # Select corresponding template
        tmpl = templates[lore]

        # Populate/Enrich missing keys while preserving any spreadsheet parsed values
        # Setup bonds
        bonds = enriched.get("bonds", {})
        if not isinstance(bonds, dict):
            bonds = {}

        # Ensure all list bonds are fully recommended and not shortened
        b_atk = bonds.get("attack", [])
        if not b_atk:
            b_atk = tmpl["attack_bonds"]
        b_hp = bonds.get("hp", [])
        if not b_hp:
            b_hp = tmpl["hp_bonds"]
        b_def = bonds.get("defense", [])
        if not b_def:
            b_def = tmpl["defense_bonds"]

        enriched["bonds"] = {
            "attack": b_atk,
            "hp": b_hp,
            "defense": b_def
        }

        # Setup build details
        build = enriched.get("build", {})
        if not isinstance(build, dict):
            build = {}

        enriched["build"] = {
            "main": build.get("main", name),
            "assists": build.get("assists", tmpl["assists"]),
            "guards": build.get("guards", tmpl["guards"]),
            "cards": build.get("cards", tmpl["cards"]),
            "bonds": enriched["bonds"],
            "talents": enriched.get("talents", tmpl["tips"]),  # default/fallback
            "gear": enriched.get("gear", tmpl["gear"]),
            "accessories": tmpl["accessories"],
            "tips": tmpl["tips"],
            "strengths": tmpl["strengths"],
            "weaknesses": tmpl["weaknesses"],
            "counters": enriched.get("counters", [tmpl["counters"]]),
            "synergies": enriched.get("synergies", [tmpl["synergies"]]),
            "investment": tmpl["investment"],
            "pvp_rating": tmpl["pvp_rating"],
            "pve_rating": tmpl["pve_rating"]
        }

        # Handle top level keys that might be referenced
        if "history" not in enriched:
            enriched["history"] = f"Released as a powerful {enriched['type']} character with excellent attributes."
        if "gear" not in enriched:
            enriched["gear"] = tmpl["gear"]
        if "talents" not in enriched:
            enriched["talents"] = enriched["talents"]  # mapped above
        if "skills" not in enriched or not enriched["skills"]:
            # Fallback mock skills if none parsed
            enriched["skills"] = {
                "Before Liberation": {
                    "s1": "350% Damage, grants Speed increase",
                    "s2": "380% Damage, chance to stun",
                    "s3_weapon": "420% Damage, grants invulnerability frames"
                },
                "Assist": "350% Damage assist call with high shield",
                "Guard": "Gains 15% armor shield and dispels control effects"
            }

        return enriched

    def enrich_card(self, card):
        enriched = dict(card)

        # Ensure all standard fields exist to satisfy formatting
        defaults = {
            "rarity": "SP / SSR",
            "description": "An elite card that drastically improves your battle performance.",
            "skills": {
                "skill1": {"name": "Offensive Surge", "effect": "ATK +15%", "cooldown": "15s", "best_usage": "Opener"},
                "skill2": {"name": "Guard Breaker", "effect": "Enemy DEF -20%", "cooldown": "20s", "best_usage": "Mid-combo"},
                "skill3": {"name": "Absolute Finish", "explanation": "Ignores block, adds life steal", "hidden_interactions": "None", "priority": "High", "combos": "1-2-3"}
            },
            "stats": {"hp": "12000", "attack": "3000", "defense": "1000", "pierce": "600", "crit": "500", "block": "400"},
            "analysis": {"pvp": "Dominates high rank matches.", "pve": "Speeds up boss runs.", "guild_war": "High AOE clearance.", "arena": "Extremely useful in 1v1."},
            "strategy": {"weaknesses": "None", "strengths": "Great stat spikes", "strong_against": ["Low armor characters"], "countered_by": ["Silence"], "best_synergies": ["Any high-tier DPS"]},
            "recommendations": {"bonds": ["Shinji", "Aizen"], "team": ["SP Power"], "assist": "Nelliel", "guard": "Yamamoto"},
            "rating": {"overall": "9.5/10", "investment": "High Priority"},
            "expert_opinion": "An absolute masterpiece of a card. High priority to invest."
        }

        for k, v in defaults.items():
            if k not in enriched:
                enriched[k] = v
            elif isinstance(v, dict):
                # Deeper check for nested dicts
                for sub_k, sub_v in v.items():
                    if sub_k not in enriched[k]:
                        enriched[k][sub_k] = sub_v
                    elif isinstance(sub_v, dict):
                        for sub_sub_k, sub_sub_v in sub_v.items():
                            if sub_sub_k not in enriched[k][sub_k]:
                                enriched[k][sub_k][sub_sub_k] = sub_sub_v

        return enriched

    def get_meta(self):
        return self.data.get("meta", {})

    def get_events(self):
        return self.data.get("events", {})

    def reload(self):
        self.data = {}
        self.load_all()

# Singleton instance
data_manager = DataManager()
