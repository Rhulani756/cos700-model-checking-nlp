# NLP module test suite

Copy the `tests` directory and `pytest.ini` into the repository root:

```text
cos700-model-checking-nlp/
├── pipeline/
├── tests/
│   ├── conftest.py
│   ├── test_configuration.py
│   ├── test_live_smoke.py
│   ├── test_llm_client.py
│   ├── test_parser_nlp_contract.py
│   ├── test_prompt_builder.py
│   ├── test_providers.py
│   └── test_schemas.py
└── pytest.ini
```

Run all offline tests:

```bash
python -m pytest -q
```

The live API test is skipped by default. Run it manually only when you intend to use API quota:

```bash
RUN_LIVE_NLP_TEST=1 python -m pytest pipeline/tests/test_live_smoke.py -q -s
```

PowerShell equivalent:

```powershell
$env:RUN_LIVE_NLP_TEST="1"
python -m pytest tests/test_live_smoke.py -q -s
```
