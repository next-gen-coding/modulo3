# Pausa del flujo · thread_id=HU-10-solicitar-vacaciones

## diagnostico
5 failed, 18 passed, 1 warning in 38.03s
- tests.api.test_hu_10::test_cp_hu10_02
  assert 1 == 0
- tests.api.test_hu_10::test_cp_hu10_14
  assert 201 == 422
 +  where 201 = <Response [201 Created]>.status_code
- tests.api.test_hu_10::test_cp_hu10_15
  AssertionError: assert 'La solicitud...: te quedan 9' == 'La solicitud...: te quedan 8'
  
  Skipping 42 identical leading characters in diff, use -v to show
  - te quedan 8
  ?           ^
  + te quedan 9
  ?           ^
- tests.e2e.test_hu_10_e2e::test_cp_hu10_21[chromium]
  AssertionError: assert '7' in '8'
- tests.e2e.test_hu_10_e2e::test_cp_hu10_22[chromium]
  playwright._impl._errors.TimeoutError: Locator.text_content: Timeout 30000ms exceeded.
Call log:
  - waiting for get_by_test_id("mensaje-error")

## pregunta
El triage no resolvió los fallos en 1 ciclos. Anota tu decisión
