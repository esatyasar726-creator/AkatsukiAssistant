def format_card_info(card):
    if not card: return "❌ Card information unavailable."
    s = card.get('skills', {})
    stats = card.get('stats', {})
    rec = card.get('recommendations', {})
    strat = card.get('strategy', {})

    res = (
        f"🃏 **{card.get('name', 'N/A').upper()}**\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
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
                res += (f"• Explanation: {sk.get('explanation', 'N/A')}\n"
                        f"• Interactions: {sk.get('hidden_interactions', 'N/A')}\n"
                        f"• Priority: {sk.get('priority', 'N/A')}\n"
                        f"• Combos: {sk.get('combos', 'N/A')}\n\n")

    res += (
        f"🔥 **Passive Effects:** {card.get('passive_effects', 'N/A')}\n"
        f"📈 **Scaling:** {card.get('scaling', 'N/A')}\n\n"
        f"❤️ HP: {stats.get('hp', 'N/A')} | ⚔️ ATK: {stats.get('attack', 'N/A')} | 🛡️ DEF: {stats.get('defense', 'N/A')}\n"
        f"🎯 Crit: {stats.get('crit', 'N/A')} | 🧱 Block: {stats.get('block', 'N/A')} | 💥 Pierce: {stats.get('pierce', 'N/A')}\n\n"
        f"🔋 **Rage Recovery:** {card.get('rage', {}).get('recovery', 'N/A')}\n\n"
        f"🎮 **PvP Analysis:** {card.get('analysis', {}).get('pvp', 'N/A')}\n"
        f"👹 **PvE Analysis:** {card.get('analysis', {}).get('pve', 'N/A')}\n\n"
        f"✅ **Strengths:** {strat.get('strengths', 'N/A')}\n"
        f"⚠️ **Weaknesses:** {strat.get('weaknesses', 'N/A')}\n\n"
        f"🆚 **Counter Information:**\n"
        f"• Strong Against: {', '.join(strat.get('strong_against', []))}\n"
        f"• Countered By: {', '.join(strat.get('countered_by', []))}\n\n"
        f"🔗 **Recommended Bonds:** {', '.join(rec.get('bonds', []))}\n"
        f"👥 **Recommended Team:** {', '.join(rec.get('team', []))}\n\n"
        f"📊 **Final Rating:** {card.get('rating', {}).get('overall', 'N/A')}\n"
        f"💬 **Expert Opinion:** _{card.get('expert_opinion', 'N/A')}_"
    )
    return res

def format_character_info(char):
    if not char: return "❌ Character unavailable."
    b = char.get('bonds', {})
    res = (
        f"👤 **{char.get('name', 'N/A').upper()}**\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 **Type:** {char.get('type', 'N/A')}\n"
        f"📖 **Bio:** {char.get('description', 'N/A')}\n\n"
        f"⚔️ **Skills:** {', '.join(char.get('skills', []))}\n"
        f"🌟 **Talents:** {', '.join(char.get('talents', []))}\n\n"
        f"⚙️ **Gear:** {', '.join(char.get('gear', []))}\n"
        f"🏛️ **Soul Hall:** {char.get('soul_hall', 'N/A')}\n\n"
        f"🔗 **ALL RECOMMENDED BONDS**\n\n"
        f"⚔️ **Attack Bonds:**\n- " + "\n- ".join(b.get('attack', [])) + "\n\n"
        f"❤️ **HP Bonds:**\n- " + "\n- ".join(b.get('hp', [])) + "\n\n"
        f"🛡️ **Defense Bonds:**\n- " + "\n- ".join(b.get('defense', [])) + "\n\n"
        f"📊 **Expert PvP:** {char.get('pvp_rating', 'S')} | **PvE:** {char.get('pve_rating', 'A')}\n"
        f"💡 **Gameplay Tip:** {char.get('gameplay_tip', 'Focus on maximizing rage generation.')}"
    )
    return res

def format_profile(data):
    username, coins, xp, level, streak = data
    return (
        f"👤 **PLAYER PROFILE: {username}**\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎖 **Level:** {level}\n"
        f"✨ **XP:** {xp}\n"
        f"💰 **Coins:** {coins}\n"
        f"🔥 **Win Streak:** {streak}\n"
    )

def format_meta(meta):
    if not meta: return "❌ Meta info unavailable."
    tl = meta.get('current_meta', {}).get('tierlist', {})
    res = "🏆 **AKATSUKI EXPERT TIER LIST** 🏆\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    for tier, chars in tl.items():
        res += f"⭐ **{tier}**: {', '.join(chars)}\n"
    res += f"\n🎮 **PvP Meta:** {meta['current_meta'].get('pvp', 'N/A')}\n"
    res += f"👹 **PvE Meta:** {meta['current_meta'].get('pve', 'N/A')}"
    return res
