# blip_dab_treinamento

Material de apoio para o treinamento sobre Databricks Asset Bundles (DAB) na Blip. O bundle demonstra como empacotar código Python e notebooks, parametrizar jobs e acionar o deploy automatizado em produção via Azure Pipelines.

## O que está sendo construído
- Job `blip_dab_treinamento_job` que executa o notebook `src/notebooks/demo_notebook.py` com parâmetros dinâmicos (catálogo, usuário e nome).
- Bundle com dois _targets_ (`dev` e `prod`) definidos em `databricks.yml`, incluindo ajustes de catálogo e performance.
- Azure Pipeline (`../azure-pipelines.yml`) que valida o bundle e efetua `bundle deploy`/`bundle run` em produção utilizando um service principal.

## Pré-requisitos
- Python 3.12 e [uv](https://docs.astral.sh/uv/getting-started/installation/) instalados localmente.
- Databricks CLI v0.218.0 ou superior (`curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh`).
- Perfis autenticados via `databricks auth login --profile dev` e `--profile prod`, usando os hosts mascarados (`https://adb-***dev***.azuredatabricks.net`, `https://adb-***prod***.azuredatabricks.net`).
- Service principal com permissões no workspace e variáveis no Azure Pipelines: `DATABRICKS_HOST_PROD`, `DATABRICKS_CLIENT_ID`, `DATABRICKS_CLIENT_SECRET`.

## Como executar localmente
```bash
uv sync --dev              # instala dependências
databricks bundle validate # valida o bundle para o target padrão (dev)
databricks bundle deploy --target dev
```
Para testar o job diretamente:
```bash
databricks bundle run blip_dab_treinamento_job --target dev \
  -- --job-parameters catalog_name=dab_dev user_id=1 user_name=Demo
```

## CI/CD no Azure Pipelines
- `BuildAndTest` foi removido: o pipeline atual executa somente o estágio `DeployProd` para validar, implantar e acionar o job em produção.
- Os passos do decorator corporativo (SonarQube) são ignorados via variáveis `skipDecorator=true` e `skipSonarBranch=true`.
- A autenticação usa os envs exportados pelo pipeline; não é necessário token pessoal.

### Parâmetros sensíveis
Certifique-se de registrar os valores como variáveis secretas e revisar periodicamente a validade do client secret do service principal.

## Estrutura principal
```
blip_dab_treinamento/
├── databricks.yml              # definição do bundle e targets
├── resources/jobs/             # job YAML usado no deploy
├── src/notebooks/demo_notebook.py
├── tests/                      # ponto de partida para testes
└── README.md                   # este arquivo
```

## Próximos passos sugeridos
1. Adaptar o job/notebook para o cenário real do time.
2. Reativar estágios de build/testes quando houver validações automatizadas relevantes.
3. Versionar secrets no Key Vault e vinculá-los ao pipeline para reforçar governança.
4. Apresentação para video
