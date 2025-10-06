## Como validar a configuração do job (testes)

Antes de realizar o deploy ou rodar jobs, recomenda-se validar a configuração do job YAML via testes automatizados:


1. Exporte o profile Databricks correto (case sensitive, conforme listado em `databricks auth profiles`):
  ```bash
  export DATABRICKS_CONFIG_PROFILE=DEV
  ```
2. Execute os testes com o gerenciador de ambiente `uv`:
  ```bash
  uv run pytest
  ```
  Para visualizar as mensagens informativas dos testes (prints), utilize a flag `-s`:
  ```bash
  uv run pytest -s
  ```
  Assim, você verá no terminal o que cada teste está validando e confirmando.
3. Verifique se todos os testes passaram. Eles garantem que o job está corretamente configurado (tags, schedule, parâmetros, performance_target).

Após a validação dos testes, siga para o deploy e execução dos jobs conforme instruções abaixo.

# blip_dab_treinamento


Material de apoio para o treinamento e implantação de Databricks Asset Bundles (DAB) em ambientes corporativos Azure DEV e PRD. Este bundle serve como exemplo adaptado para uso real, demonstrando empacotamento de código Python, notebooks, parametrização de jobs e deploy automatizado via Azure Pipelines.

## Contexto Corporativo
Este bundle foi adaptado para rodar nos ambientes provisionados conforme arquitetura do projeto:
- Catálogos: `rescue_dev` (DEV) e `rescue_prd` (PRD)
- Workspaces: `https://adb-1293581597272291.11.azuredatabricks.net` (DEV) e `https://adb-2533506717590470.10.azuredatabricks.net` (PRD)
- Governança via Unity Catalog, automação CLI e integração com Azure Pipelines

## O que está sendo construído
- Job `blip_dab_treinamento_job` que executa o notebook `src/notebooks/demo_notebook.py` com parâmetros dinâmicos (catálogo, usuário e nome).
- Bundle com dois _targets_ (`dev` e `prd`) definidos em `databricks.yml`, já configurados para os ambientes reais.
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
Para testar o job diretamente (DEV):
```bash
databricks bundle run blip_dab_treinamento_job --target dev \
  -- --job-parameters catalog_name=rescue_dev user_id=1 user_name=Demo
```
Para rodar em produção (PRD):
```bash
databricks bundle deploy --target prd
databricks bundle run blip_dab_treinamento_job --target prd \
  -- --job-parameters catalog_name=rescue_prd user_id=2 user_name=ProdUser
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
├── databricks.yml              # definição do bundle e targets DEV/PRD
├── resources/jobs/             # job YAML usado no deploy
├── src/notebooks/demo_notebook.py
├── tests/                      # ponto de partida para testes
└── README.md                   # este arquivo
```

## Próximos passos sugeridos
1. Adaptar o job/notebook para o cenário real do time (schemas, tabelas, lógica de negócio).
2. Reativar estágios de build/testes quando houver validações automatizadas relevantes.
3. Versionar secrets no Key Vault e vinculá-los ao pipeline para reforçar governança.
4. Apresentação para vídeo e documentação corporativa.
