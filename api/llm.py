import os
from typing import Dict, List
import google.generativeai as genai


USE_REAL_GEMINI = True if os.getenv("GEMINI_API_KEY") else False


class SubAgentResult:
    def __init__(self, name: str, output: str):
        self.name = name
        self.output = output


class GeminiClient:
    """
    Thin wrapper around Gemini API.
    """

    def __init__(self):
        if USE_REAL_GEMINI:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel("gemini-1.5-flash")

    def generate(self, prompt: str) -> str:
        if not USE_REAL_GEMINI:
            return "[SIMULATED OUTPUT]\n" + prompt[:300]

        response = self.model.generate_content(prompt)
        return response.text


class StrategicBuyerEngine:
    """
    Multi-agent orchestration layer.
    """

    def __init__(self):
        self.llm = GeminiClient()

    def run_full_analysis(self, vyzva_text: str, nabidky_text: str) -> Dict:
        agent_outputs = []

        agent_outputs.append(
            self._run_agent(
                "Agent analýzy výzvy",
                self._prompt_analyza_vyzvy(vyzva_text),
            )
        )

        agent_outputs.append(
            self._run_agent(
                "Agent technického souladu",
                self._prompt_technicky_soulad(nabidky_text),
            )
        )

        agent_outputs.append(
            self._run_agent(
                "Agent cenového hodnocení",
                self._prompt_cenove_hodnoceni(nabidky_text),
            )
        )

        agent_outputs.append(
            self._run_agent(
                "Agent rizik",
                self._prompt_rizika(nabidky_text),
            )
        )

        executive = self._run_agent(
            "Agent manažerského shrnutí",
            self._prompt_manazerske_shrnuti(agent_outputs),
        )

        doporuceni = self._run_agent(
            "Hlavní agent – finální doporučení",
            self._prompt_finalni_doporuceni(agent_outputs),
        )

        skolitel = self._run_agent(
            "Školitel",
            self._prompt_skolitel(doporuceni.output),
        )

        return {
            "executive_summary": executive.output,
            "agent_outputs": {
                a.name: a.output for a in agent_outputs
            },
            "final_recommendation": doporuceni.output,
            "vysvetleni_pro_novacka": skolitel.output,
            "gemini_mode": "REAL" if USE_REAL_GEMINI else "SIMULATED",
        }

    # =========================
    # AGENT EXECUTION
    # =========================

    def _run_agent(self, name: str, prompt: str) -> SubAgentResult:
        output = self.llm.generate(prompt)
        return SubAgentResult(name, output)

    # =========================
    # PROMPTS (aligned with document)
    # =========================

    def _prompt_analyza_vyzvy(self, vyzva: str) -> str:
        return f"""
Jsi Agent analýzy výzvy v systému Strategický nákupčí.

Úkol:
- Identifikuj kvalitativní a kvantitativní požadavky
- Vytvoř hodnoticí kritéria

Vstupní výzva:
{vyzva}

Strukturovaný výstup:
"""

    def _prompt_technicky_soulad(self, nabidky: str) -> str:
        return f"""
Jsi Agent technického souladu.

Úkol:
- Vyhodnoť soulad nabídek s technickými požadavky
- Uveď procentuální vyjádření

Nabídky:
{nabidky}

Výstup (tabulka nebo seznam):
"""

    def _prompt_cenove_hodnoceni(self, nabidky: str) -> str:
        return f"""
Jsi Agent cenového hodnocení.

Úkol:
- Porovnej cenové modely
- Uveď číselné srovnání (TCO)

Nabídky:
{nabidky}

Výstup:
"""

    def _prompt_rizika(self, nabidky: str) -> str:
        return f"""
Jsi Agent rizik.

Úkol:
- Identifikuj 3–5 klíčových rizik
- Popiš jejich dopad

Nabídky:
{nabidky}

Výstup:
"""

    def _prompt_manazerske_shrnuti(self, agent_outputs: List[SubAgentResult]) -> str:
        joined = "\n\n".join(
            f"{a.name}:\n{a.output}" for a in agent_outputs
        )

        return f"""
Jsi Agent manažerského shrnutí.

Na základě následujících výstupů připrav EXECUTIVE SUMMARY
(max 3 krátké odstavce):

{joined}
"""

    def _prompt_finalni_doporuceni(self, agent_outputs: List[SubAgentResult]) -> str:
        joined = "\n\n".join(
            f"{a.name}:\n{a.output}" for a in agent_outputs
        )

        return f"""
Jsi HLAVNÍ AGENT systému Strategický nákupčí.

Na základě podkladů vydej finální doporučení:
- max. 5 bodů
- objektivní
- profesionální tón

Podklady:
{joined}
"""

    def _prompt_skolitel(self, doporuceni: str) -> str:
        return f"""
Jsi AI Agent Školitel.

Vysvětli následující doporučení úplnému začátečníkovi:
- jednoduchý jazyk
- praktické dopady
- žádný odborný žargon

Doporučení:
{doporuceni}
"""