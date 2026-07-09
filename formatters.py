def format_card_info(card):
    if not card: return "❌ Card information unavailable."

    s = card.get('skills', {})
    res = (
        f"🃏 **Card Name:** {card.get('name', 'Unknown')}\n\n"
        f"📌 **Type:** {card.get('type', 'N/A')}\n"
        f"⭐ **Rarity:** {card.get('rarity', 'N/A')}\n"
        f"📖 **Description:** {card.get('description', 'N/A')}\n\n"
    )

    for i in range(1, 4):
        sk = s.get(f'skill{i}', {})
        if sk:
            res += f"⚔️ **Skill {i} ({sk.get('name', 'N/A')})**\n"
            if i < 3:
                res += f"• Effect: {sk.get('effect', 'N/A')}\n"
                res += f"• Cooldown: {sk.get('cooldown', 'N/A')}\n"
                res += f"• Best Usage: {sk.get('best_usage', 'N/A')}\n\n"
            else:
                res += f"• Explanation: {sk.get('explanation', 'N/A')}\n"
                res += f"• Hidden Interactions: {sk.get('hidden_interactions', 'N/A')}\n"
                res += f"• Priority: {sk.get('priority', 'N/A')}\n"
                res += f"• Combos: {sk.get('combos', 'N/A')}\n\n"

    stats = card.get('stats', {})
    res += (
        f"❤️ HP: {stats.get('hp', 'N/A')} | ⚔️ ATK: {stats.get('attack', 'N/A')} | 🛡️ DEF: {stats.get('defense', 'N/A')}\n"
        f"💥 Pierce: {stats.get('pierce', 'N/A')} | 🎯 Crit: {stats.get('crit', 'N/A')} | 🧱 Block: {stats.get('block', 'N/A')}\n\n"
        f"🎮 **PvP Analysis:** {card.get('analysis', {}).get('pvp', 'N/A')}\n"
        f"👹 **PvE Analysis:** {card.get('analysis', {}).get('pve', 'N/A')}\n"
        f"🏆 **Guild War:** {card.get('analysis', {}).get('guild_war', 'N/A')}\n"
        f"👑 **Arena:** {card.get('analysis', {}).get('arena', 'N/A')}\n\n"
        f"✅ **Strengths:** {card.get('strategy', {}).get('strengths', 'N/A')}\n"
        f"⚠️ **Weaknesses:** {card.get('strategy', {}).get('weaknesses', 'N/A')}\n\n"
        f"🆚 **Strong Against:** {', '.join(card.get('strategy', {}).get('strong_against', [])) if isinstance(card.get('strategy', {}).get('strong_against'), list) else card.get('strategy', {}).get('strong_against', 'N/A')}\n"
        f"❌ **Countered By:** {', '.join(card.get('strategy', {}).get('countered_by', [])) if isinstance(card.get('strategy', {}).get('countered_by'), list) else card.get('strategy', {}).get('countered_by', 'N/A')}\n\n"
        f"📊 **Investment Rating:** {card.get('rating', {}).get('overall', 'N/A')}\n"
        f"💬 **Expert Opinion:** _{card.get('expert_opinion', 'N/A')}_"
    )
    return res

def format_character_info(char):
    if not char: return "❌ Character information unavailable."

    res = (
        f"👤 **Character:** {char.get('name', 'Unknown')}\n"
        f"📌 **Type:** {char.get('type', 'N/A')}\n\n"
        f"📖 **Description:** {char.get('description', 'N/A')}\n\n"
        f"⚔️ **Skills:** {', '.join(char.get('skills', [])) if isinstance(char.get('skills'), list) else 'Parsed Skills'}\n"
        f"🔗 **Bonds:**\n"
        f"⚔️ ATK: {', '.join(char.get('bonds', {}).get('attack', []))}\n"
        f"❤️ HP: {', '.join(char.get('bonds', {}).get('hp', []))}\n"
        f"🛡️ DEF: {', '.join(char.get('bonds', {}).get('defense', []))}\n\n"
        f"📜 **History:** {char.get('history', 'N/A')}"
    )
    return res

def format_meta(meta):
    if not meta: return "❌ Meta information unavailable."
    cm = meta.get('current_meta', {})
    res = "🔥 **CURRENT BLEACH MOBILE 3D META** 🔥\n\n"
    res += f"⚔️ **PvP Meta:**\n{cm.get('pvp', 'N/A')}\n\n"
    res += f"👹 **PvE Meta:**\n{cm.get('pve', 'N/A')}\n\n"
    res += "🏆 **Character Tier List:**\n"
    tiers = cm.get('tierlist', {})
    for tier, chars in tiers.items():
        res += f"• **{tier}:** {', '.join(chars)}\n"
    return res
