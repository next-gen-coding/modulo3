"""Patrón Reflexión: generar → revisar contra criterios → corregir, con un límite de intentos.

Lo que distingue al patrón en el código: un `for intento` donde la crítica del revisor se AGREGA
al siguiente prompt. Aquí el revisor es código (reglas verificables), igual que en la fábrica.

Uso:  python -m ejemplos.s1_razonamiento.reflexion
En tu fábrica:  agentes/analista.py → validar_gherkin() y generar_criterios()
"""
import os
import re

from anthropic import Anthropic

from ejemplos.comun import historia, paso, titulo

MAX_INTENTOS = 3


def revisar(gherkin: str) -> list[str]:
    """El revisor: reglas que se comprueban sin modelo. Devuelve la lista de problemas."""
    problemas = []
    escenarios = re.split(r"\n\s*Escenario:", gherkin)[1:]
    if len(escenarios) < 3:
        problemas.append(f"Hay {len(escenarios)} escenarios; se necesitan al menos 3 (éxito y dos errores).")
    for i, esc in enumerate(escenarios, 1):
        for palabra in ("Dado", "Cuando", "Entonces"):
            if not re.search(rf"^\s*{palabra}\b", esc, re.M):
                problemas.append(f"El escenario {i} no tiene '{palabra}'.")
    if "Usa el correo corporativo @empresa.com" not in gherkin:
        problemas.append("Falta el escenario del correo no corporativo con el mensaje exacto "
                         "«Usa el correo corporativo @empresa.com».")
    return problemas


def generar_con_reflexion(hu: str) -> str:
    cliente = Anthropic()
    tarea = f"Escribe criterios de aceptación en Gherkin (# language: es) para esta historia:\n{hu}"
    for intento in range(1, MAX_INTENTOS + 1):
        resp = cliente.messages.create(model=os.environ["MODEL"], max_tokens=3000,
                                       messages=[{"role": "user", "content": tarea}])
        gherkin = "".join(b.text for b in resp.content if b.type == "text")   # solo bloques de texto
        #print("GHERKIN: " + gherkin)   # ← temporal
        problemas = revisar(gherkin)                              # REVISAR
        paso(f"intento {intento}", f"{len(problemas)} problema(s): {problemas}" if problemas else "sin problemas")
        #Si no tiene problemas en la validación, revuelve el gherkin generado.
        if not problemas:
            return gherkin
        #De lo contrario, retroalimenta al modelo con los problemas detectados para corregirlos en el siguiente intento.
        tarea += ("\n\nTu versión anterior tiene estos problemas; corrígelos y devuelve el Gherkin completo:\n- "
                  + "\n- ".join(problemas))                       # CORREGIR: la crítica vuelve como contexto
    raise RuntimeError(f"Tras {MAX_INTENTOS} intentos sigue habiendo problemas: {problemas}")


if __name__ == "__main__":
    titulo("Reflexión")
    print(generar_con_reflexion(historia("HU-01")))
