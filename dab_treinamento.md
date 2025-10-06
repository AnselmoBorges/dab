# Guia de Treinamento: Databricks Asset Bundles na Blip

Este repositório reúne o material de apoio para o treinamento interno sobre **Databricks Asset Bundles (DABs)** na Blip. O objetivo é demonstrar, de ponta a ponta, como adotar bundles para padronizar projetos Databricks, desde o preparo do ambiente local até a integração com Azure DevOps e a implantação em ambientes **DEV** e **PRD**.

---

## 1. Visão Geral Visual

**Fluxo resumido**

1. Desenvolvimento local com VS Code usando o bundle (`databricks bundle init`, edição, testes locais).
2. Versionamento do código e das definições YAML no Azure Repos (Git).
3. Pipeline de CI/CD valida o bundle e realiza o deploy no workspace **DEV** (`databricks bundle deploy -t dev`).
4. Após os testes, uma aprovação libera o deploy para **PRD** (`databricks bundle deploy -t prod`).

```
VS Code → Azure Repos → Pipeline CI/CD → Workspace DEV → (Aprovação) → Workspace PRD
```

> Representação textual do fluxo padrão: desenvolvimento local versionado no Git, pipeline executando validação em DEV e, mediante aprovação, deploy em PRD.

![Exemplo de job configurado na UI](docs/images/job-ui-example.png)

> Substitua `docs/images/job-ui-example.png` por um print real da UI do Databricks destacando o job gerado pelo bundle. Veja instruções na seção **Guia para Capturas de Tela** abaixo.

---

## 2. Entendendo Databricks Asset Bundles

- Os DABs combinam código-fonte e metadados em uma estrutura única, permitindo descrever jobs, pipelines, recursos do Unity Catalog e dependências como **Infrastructure-as-Code**.
- A CLI do Databricks usa o bundle para validar configurações, versionar artefatos (pasta `.databricks`) e executar deploys consistentes entre ambientes.
- Benefícios principais: controle de versão centralizado, revisão de código facilitada, testes automatizados e preparação para **CI/CD**.

> Os bundles tornaram-se GA (General Availability) em abril/2024 e são a recomendação oficial da Databricks para governança de artefatos de dados e IA.

---

## 3. Pré-requisitos e Configuração Inicial

1. **VS Code e Python** instalados na máquina local.
2. **Databricks CLI v0.218.0+**: instale e confirme com `databricks --version`.
   - Antes de atualizar, garanta que o `pip` esteja na versão mais recente: `python -m pip install --upgrade pip`.
   - Se você possuir a versão antiga instalada via `pip` (ex.: `Version 0.18.0`), remova-a com `pip uninstall databricks-cli`.
   - macOS/Linux com Homebrew: `brew update && brew install databricks/tap/databricks` (ou `brew upgrade databricks/tap/databricks` para atualizar).
   - macOS/Linux sem Homebrew: `curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh` (instalador oficial). Se o diretório `/usr/local/bin` não for gravável:
     - Execute com privilégio elevado: `curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sudo sh`.
     - Ou baixe o script e instale em um diretório onde tenha permissão:
       ```bash
       curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh -o /tmp/databricks-install.sh
       chmod +x /tmp/databricks-install.sh
       INSTALL_DIR=$HOME/.local/bin /tmp/databricks-install.sh
       ```
       > Garanta que `~/\.local/bin` esteja no `PATH` (adicione `export PATH="$HOME/.local/bin:$PATH"` ao `~/.zshrc`).
     - Para reutilizar o diretório onde a CLI antiga via `pip` era instalada (por exemplo, `~/.pyenv/versions/3.12.0/bin`), informe esse caminho diretamente:
       ```bash
       INSTALL_DIR=$HOME/.pyenv/versions/3.12.0/bin /tmp/databricks-install.sh
       ```
       > Ajuste o caminho conforme sua instalação (use `which databricks` para conferir) e repita `databricks --version` para confirmar a atualização.
   - Windows: `winget install Databricks.DatabricksCLI` (ou `winget upgrade Databricks.DatabricksCLI`).
   - Após instalar ou atualizar, abra um novo terminal e valide com `databricks --version` (necessário **≥ 0.218.0**). Use `which databricks` (ou `where databricks` no Windows) para checar o binário em uso.
3. **Ambiente virtual opcional (`pocdab_env`)**:
   - Crie fora do repositório, na pasta do usuário, para evitar que binários sejam versionados.
   - macOS/Linux: `python -m venv ~/pocdab_env` e ative com `source ~/pocdab_env/bin/activate`.
   - Windows (PowerShell): `python -m venv $env:USERPROFILE\pocdab_env` e ative com `$env:USERPROFILE\pocdab_env\Scripts\Activate.ps1`.
   - Depois de ativar o ambiente, instale as dependências com `pip install -r requirements.txt`.
4. **Autenticação U2M OAuth**: execute `databricks auth login --host https://adb-***dev***.azuredatabricks.net --profile dev` (substitua pelo host do seu workspace). O processo gera/atualiza o arquivo `~/.databrickscfg` com o perfil `dev`.
5. **Gerenciador de pacotes `uv`**: `pip install uv`. O template `default-python` usa o `uv` para resolver dependências.

O arquivo `requirements.txt` define as dependências mínimas para o laboratório:

- `databricks-cli>=0.218.0`
- `uv>=0.2.0`

Com esses itens prontos, abra o terminal integrado do VS Code na pasta do projeto que receberá o bundle.

---

## 4. Estrutura de um Projeto Asset Bundle

1. Inicialize o bundle:
   ```bash
   databricks bundle init
   ```
   - Escolha o template `default python` e responda às perguntas (nome, notebooks de exemplo, pipeline DLT, pacote Python, uso de serverless etc.).
   - Para o treinamento, responda da seguinte forma:
     - Nome do projeto: `blip_dab_treinamento`.
     - Incluir notebook, Lakeflow pipeline e pacote Python de exemplo: **não** (utilize os arquivos fornecidos neste repositório como base).
     - Habilitar serverless compute: `yes`.
    - Workspace: confirme `https://adb-***dev***.azuredatabricks.net` (ajuste se estiver em outro workspace).
2. Após a inicialização, a estrutura típica conterá:
   - `src/`: notebooks e scripts Python do projeto.
   - `resources/`: descrições YAML de jobs, pipelines e outros recursos.
   - `tests/`: scripts de teste.
   - `.databricks/`: snapshots dos deploys para auditoria.
   - `databricks.yml`: arquivo principal de orquestração do bundle.

   Caso algum arquivo de exemplo seja criado automaticamente (ex.: `resources/<nome>.job.yml` ou `resources/<nome>.pipeline.yml`), remova-o. O repositório já contém `resources/jobs/blip_dab_treinamento.job.yml` e `src/notebooks/demo_notebook.py`, que serão usados nas etapas seguintes.

> Mantenha os artefatos versionados no Git para garantir rastreabilidade entre código, configuração e implantações.

---

## 5. Configurando `databricks.yml` para DEV e PRD

O `databricks.yml` define variáveis, inclui recursos e descreve os **targets** (ambientes) usados nos deploys.

```yaml
bundle:
  name: blip_dab_treinamento
  include:
    - resources/jobs/*.yml
    - resources/pipelines/*.yml
    - resources/schemas/*.yml

variables:
  catalog_name:
    description: Nome do catálogo Unity Catalog (treinamento DAB)
    default: dab_dev
  performance_target:
    description: Define o perfil de performance/custo (STANDARD ou PERFORMANCE_OPTIMIZED)
    default: STANDARD

targets:
  dev:
    workspace:
      host: https://adb-***dev***.azuredatabricks.net
    mode: development

  prod:
    workspace:
      host: https://adb-***prod***.azuredatabricks.net
    variables:
      catalog_name: dab_prd
      performance_target: PERFORMANCE_OPTIMIZED
```

> Neste treinamento, o catálogo padrão `dab_dev` atende o workspace de desenvolvimento (`https://adb-***dev***.azuredatabricks.net`) e o catálogo `dab_prd` mapeia o workspace de produção (`https://adb-***prod***.azuredatabricks.net`). O job foi configurado para usar Jobs Compute serverless com fila habilitada (`queue.enabled`) e alvo de performance otimizada.

Recomendações:

- Use variáveis (`${var.catalog_name}`) para evitar repetição e habilitar overrides por target ou linha de comando (`--where catalog_name=valor`).
- Utilize a diretiva `include` para modularizar recursos YAML por pasta.
- Em DEV, `mode: development` pausa a execução automática de jobs agendados e adiciona prefixos de usuário; em PRD mantenha execuções agendadas e configure permissões via `permissions`.

---

## 6. Criando Schemas de Exemplo no Unity Catalog

Durante o treinamento, utilize schemas simples para demonstrar operações:

1. Garanta que os catálogos `dab_dev` e `dab_prd` existam nos respectivos workspaces.
2. Os schemas de treinamento já estão pré-criados em ambos os ambientes:
   - `dab_b` → camada **bronze**
   - `dab_s` → camada **silver**
   - `dab_g` → camada **gold**
3. Durante os notebooks, consuma a variável `catalog_name` para trabalhar com os schemas existentes, por exemplo:
   ```python
   catalog = dbutils.widgets.get("catalog_name")
   spark.sql(f"CREATE TABLE IF NOT EXISTS {catalog}.dab_b.users (id INT, name STRING)")
   ```

Sobrescreva o `catalog_name` ao fazer deploy em PRD: `databricks bundle deploy -t prod --where catalog_name=dab_prd`.

---

## 7. Exemplo Prático: Notebook + Job Orquestrado

1. **Notebook** (`src/notebooks/demo_notebook.py`):
   ```python
   # Databricks notebook source
   dbutils.widgets.text("catalog_name", "dab_dev", "Catalog Name")
   catalog_name = dbutils.widgets.get("catalog_name")
   print(f"Using Catalog: {catalog_name}")

   spark.sql(
       f"CREATE TABLE IF NOT EXISTS {catalog_name}.dab_b.users (id INT, name STRING)"
   )
   spark.sql(
       f"INSERT OVERWRITE {catalog_name}.dab_b.users VALUES (1, 'Alice'), (2, 'Bob')"
   )

   df = spark.sql(f"SELECT * FROM {catalog_name}.dab_b.users")
   display(df)
   ```

2. **Job** (`resources/jobs/blip_dab_treinamento.job.yml`):
   - O bundle já inclui uma definição de job pronta para uso com Jobs Compute serverless (fila habilitada e alvo de performance otimizada).
   - Estrutura principal do job:
     ```yaml
     resources:
       jobs:
         blip_dab_treinamento_job:
           name: blip_dab_treinamento_job
           tags:
             treinamento: dab
             ambiente: dev
             area: D4B
           description: Job de treinamento que ingere usuários de exemplo com parâmetros dinâmicos.
           parameters:
             - name: catalog_name
               default: ${var.catalog_name}
             - name: user_id
               default: "3"
             - name: user_name
               default: "Anselmo"
           email_notifications:
             on_failure:
               - anselmo.junior@blip.ai
           timeout_seconds: 900
           schedule:
             quartz_cron_expression: "0 0 8 ? * TUE *"
             timezone_id: America/Sao_Paulo
           tasks:
             - task_key: ingest_demo
               notebook_task:
                 notebook_path: ../../src/notebooks/demo_notebook.py
                 base_parameters:
                   catalog_name: {{job.parameters.catalog_name}}
                   user_id: {{job.parameters.user_id}}
                   user_name: {{job.parameters.user_name}}
          queue:
            enabled: true
          performance_target: ${var.performance_target}
    ```
   - As tags (`treinamento`, `ambiente`, `area`) aparecem no Job Run e nos relatórios de billing do Databricks, facilitando a separação de custos do treinamento.
   - Com a descrição, notificações e `timeout_seconds=900`, o job envia e-mail em caso de falha e encerra execuções acima de 15 minutos. A agenda semanal (`0 0 8 ? * TUE *`) roda toda terça às 8h (horário de São Paulo).
   - Os parâmetros (`catalog_name`, `user_id`, `user_name`) possuem valores padrão, mas podem ser sobrescritos a cada execução (`--params`) ou via UI.
   - A variável `performance_target` permite rodar em `STANDARD` (DEV) ou `PERFORMANCE_OPTIMIZED` (PRD) sem duplicar o YAML.
   - Ajuste notificações, agendamentos ou tarefas adicionais conforme a necessidade do time. Utilize as *tags* para classificar o consumo (ex.: `treinamento`, `ambiente`, `area`) e substitua a configuração de fila se desejar um compute diferente.

3. **Validação e Deploy**
   - `databricks bundle validate -t dev`
   - `databricks bundle deploy -t dev`
  - Execute o job pela UI ou CLI: `databricks bundle run blip_dab_treinamento_job -t dev`
   - Repita para PRD validando antes e sobrescrevendo a variável `catalog_name`.

---

## 8. Executando e Validando o Job

1. **Rodar pela CLI (DEV)**
   - Execute `databricks bundle run blip_dab_treinamento_job -t dev` para disparar o job (o comando aguarda a conclusão por padrão).
   - Se preferir executar em background, acrescente `--no-wait` e acompanhe depois com `databricks bundle runs list -t dev` e `databricks bundle runs get <run-id> -t dev` para consultar execuções anteriores ou baixar logs.

2. **Acompanhar pela UI**
   - Acesse o workspace (`Workflows > Jobs > blip_dab_treinamento_job`) e verifique o histórico de runs, métricas e tempo de execução.
   - Abra o notebook vinculado para conferir o output (visualização da tabela `dab_b.users`).

3. **Validar os dados gerados**
   - No workspace, execute `SELECT * FROM dab_dev.dab_b.users ORDER BY id;` para confirmar a escrita dos registros de exemplo.
   - Ajuste o valor do widget `catalog_name` se precisar testar outros catálogos (`dab_prd`, por exemplo).

4. **Reexecutar com parâmetros específicos**
   - Da CLI, sobrescreva os parâmetros do job (ex.: `catalog_name`, `user_id`, `user_name`): `databricks bundle run blip_dab_treinamento_job -t dev --params catalog_name=dab_dev,user_id=4,user_name=Anselmo`.
   - Para produção, combine com o deploy correspondente ajustando os valores, por exemplo: `databricks bundle run blip_dab_treinamento_job -t prod --params catalog_name=dab_prd,user_id=4,user_name=Anselmo`.
   - **Importante:** `databricks bundle run` apenas executa a versão já implantada. Sempre que alterar o YAML ou notebooks, rode `databricks bundle deploy -t <target>` antes de um novo `run` para aplicar as mudanças.

5. **Auditar artefatos do bundle**
   - Confira a pasta `.databricks/bundles/blip_dab_treinamento/<target>` para validar snapshots do deploy e diagnosticar mudanças entre execuções.

---

## 9. Exemplos de Jobs com Asset Bundles

Asset Bundles permitem descrever diferentes tipos de workloads Databricks de forma declarativa. Após estudar o exemplo principal, explore também os cenários abaixo (todos utilizam compute serverless e estão documentados em `docs/examples/README.md`):

- **Notebook Python** – execução de notebooks como no passo 7, com parametrização via widgets.
- **DBT (Lakehouse Monitoring)** – tarefas que orquestram dbt commands via `dbt_task`.
- **SQL** – execução de queries SQL (`sql_task`).
- **SQL Job** – jobs que dependem de um SQL Warehouse dedicado (`warehouse_id`).
- **Pipelines DLT** – implantação de pipelines Delta Live Tables (`pipeline_task`).

Cada exemplo possui:
- Código-fonte/notebook em `examples/<tipo>/src` ou `examples/<tipo>/sql`.
- Definição do job/pipeline em `examples/<tipo>/resources/*.yml`.

Consulte [`docs/examples/README.md`](docs/examples/README.md) para instruções passo a passo e comandos de deploy específicos.

---

## 10. Integração com Azure DevOps (CI/CD)

### 9.1 Preparando a Service Connection

1. Crie uma App Registration dedicada ao Databricks (ex.: `srv_dab_dageneral_prd`) e gere um client secret.
2. Garanta que o service principal tenha papel **Reader** (ou superior) na assinatura correspondente:
   - Azure Portal → *Subscriptions* → selecione a subscription → *Access control (IAM)* → **Add role assignment** → escolha `Reader` (ou `Contributor` conforme a necessidade) → selecione o service principal → **Save**.
3. No Azure DevOps, crie uma **Service Connection** do tipo **Azure Resource Manager** usando **Service principal (manual)**, preenchendo Tenant ID, Client ID e Client Secret.
   - Se preferir, armazene o secret diretamente na conexão (temporariamente). Documente o plano de migrar para o Key Vault.
4. Após a criação, valide a conexão. Se o acesso foi concedido recentemente, pode ser necessário aguardar alguns minutos antes de clicar em **Verify**.
5. (Opcional) Mapeie as credenciais em um Key Vault e vincule-as a um Variable Group no futuro para reforçar a governança.

Estruture um pipeline em YAML para automatizar validação e deploy do bundle.

Pontos-chave:

- Versão o bundle em **Azure Repos**.
- Configure uma **Service Connection** com Service Principal. Em ambientes controlados, é aceitável informar `client id`/`client secret` diretamente na conexão (armazenados pelo Azure DevOps); registre no backlog migrar essas credenciais para o Key Vault assim que possível.
- Utilize **Variable Groups** para separar parâmetros de DEV e PRD. Caso ainda não tenha integrado ao Key Vault, declare os segredos como variáveis secretas do próprio variable group (mais à frente migre para o Key Vault para reforçar a governança).
- Exemplo de pipeline (`azure-pipelines.yml`):

```yaml
parameters:
  - name: environment
    type: string
    default: dev
    values:
      - dev
      - prod

stages:
- stage: DeployToDev
  displayName: Deploy para DEV
  variables:
    - group: Dev-Variables
  jobs:
    - job: DevDeployment
      steps:
        - task: UsePythonVersion@0
          inputs:
            versionSpec: '3.x'
        - script: pip install databricks-cli uv poetry
          displayName: Instalar dependências
        - script: |
            databricks auth login \
              --host $(DatabricksHost) \
              --client-id $(databricks-client-id) \
              --client-secret $(databricks-client-secret) \
              --tenant-id $(databricks-tenant-id)
          displayName: Autenticar CLI (Service Principal)
        - script: databricks bundle validate -t dev
          displayName: Validar Bundle
        - script: databricks bundle deploy -t dev --where catalog_name=$(DevCatalogName)
          displayName: Deploy DEV
        - script: databricks bundle run blip_dab_treinamento_job -t dev
          displayName: Executar Job (DEV)

- stage: DeployToProd
  displayName: Deploy para PRD
  dependsOn: DeployToDev
  condition: and(succeeded(), eq('${{ parameters.environment }}', 'prod'))
  variables:
    - group: Prod-Variables
  jobs:
    - job: ProdDeployment
      steps:
        - task: UsePythonVersion@0
          inputs:
            versionSpec: '3.x'
        - script: pip install databricks-cli uv poetry
          displayName: Instalar dependências
        - script: |
            databricks auth login \
              --host $(DatabricksHost) \
              --client-id $(databricks-client-id) \
              --client-secret $(databricks-client-secret) \
              --tenant-id $(databricks-tenant-id)
          displayName: Autenticar CLI (Service Principal)
        - script: databricks bundle validate -t prod
          displayName: Validar Bundle
        - script: databricks bundle deploy -t prod --where catalog_name=$(ProdCatalogName)
          displayName: Deploy PRD
```

Ajuste triggers (`trigger.branches`) conforme a estratégia (ex.: `develop` para DEV e `main` para PRD) e evite executar jobs automaticamente em PRD salvo acordos específicos.

---

## 11. Guia para Capturas de Tela

- Salve as imagens utilizadas no README em `docs/images/` para manter o repositório organizado.
- Sugerimos capturas como:
  - `job-ui-example.png`: job implantado na UI do Databricks, evidenciando tarefas e parâmetros.
  - `bundle-structure.png`: estrutura de pastas gerada pelo `databricks bundle init`.
- Padronize a largura (~1200px) para facilitar a leitura e mantenha nomes descritivos.
- Faça commit das imagens junto com as alterações correspondentes no README.

---

## 12. Materiais de Referência

- Vídeos:
  - *Databricks - Azure DevOps & Databricks Asset Bundles* – Apostolos Athanasiou.
  - *Databricks Asset Bundle Full Course [2025 JOB READY] | Databricks CI/CD* – Ansh Lamba.
  - *Criando um Databricks Asset Bundle em 5 minutos* – Luan Moreno | Engenharia de Dados Academy.
  - *Lecture 7. Databricks Asset Bundles* – Marvelous MLOps.
  - *Building an End-to-end MLOps Project with Databricks* – Benito Martin.
- Artigos e documentação:
  - *5 tricks to get the most out of Databricks Asset Bundles*.
  - *CI/CD usando Databricks Asset Bundles*.
  - *Databricks Asset Bundles tutorials* (documentação oficial).
  - *Databricks FAQ sobre Asset Bundles*.
  - *O que são Databricks Asset Bundles?*.
  - *Exemplos de configuração de pacote*.
  - *DAB it! Databricks Asset bundles for Machine Learning — MLOps Stacks*.

---

## 13. Próximos Passos Sugeridos

1. Clonar este repositório e executar `databricks bundle init` para gerar sua cópia do laboratório.
2. Configurar perfis `dev` e `prod` na CLI, validar e realizar o primeiro deploy controlado.
3. Adaptar o pipeline de exemplo para o Azure DevOps da Blip, validando tokens e variáveis.
4. Estender o exemplo com testes automatizados (`tests/`) e notebooks adicionais conforme a necessidade do time.

Bom aprendizado! Ajuste e evolua este roteiro conforme novas práticas e necessidades surgirem na Blip.
