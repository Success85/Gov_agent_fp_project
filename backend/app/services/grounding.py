"""
grounding.py
------------
This file builds the "grounded prompt". Grounding means: we give the AI the
verified service information and tell it to answer ONLY from that information,
so it cannot invent requirements. This is what makes our answers trustworthy.
"""

# For Sprint 1 we hard-code ONE service's verified info so we are not blocked
# waiting on the Service Data lane. Later this will come from the database.
SAMPLE_SERVICE_INFO = """
Service: Gusaba indangamuntu (National ID application)
Ibisabwa (Requirements):
- Icyemezo cy'amavuko (Birth certificate)
- Ifoto ya pasiporo (Passport photo)
Intambwe (Steps):
1. Injira kuri Irembo ukoresheje konti yawe.
2. Hitamo serivisi y'indangamuntu.
3. Ohereza inyandiko zisabwa.
4. Ishyura ukoresheje MoMo.
Amafaranga (Fee): 500 RWF
"""


def build_prompt(question: str, service_info: str = SAMPLE_SERVICE_INFO) -> str:
    """
    Combine the citizen's question with the verified service information into a
    single prompt that instructs the model to answer in Kinyarwanda, using only
    the given information.
    """
    prompt = f"""You are a helpful assistant for Rwandan government (Irembo) services.
Answer in Kinyarwanda, in a clear and simple way.
Use ONLY the information provided below. If the answer is not in the information,
say politely in Kinyarwanda that you do not have that information.

--- VERIFIED SERVICE INFORMATION ---
{service_info}
--- END OF INFORMATION ---

Citizen's question: {question}

Your answer (in Kinyarwanda):"""
    return prompt