# Guia Completo de Governança e Automação Databricks (DEV e PRD)

Este guia apresenta o passo a passo para provisionar, configurar e governar ambientes Databricks DEV e PRD na Azure, utilizando automação via CLI e Unity Catalog.

## 1. Provisionamento dos recursos Azure

### 1.1 Resource Groups
- `rg_rescue_dev` (desenvolvimento)
- `rg_rescue_prd` (produção)

### 1.2 Storage Accounts
- `sarescuedev` (DEV)
- `sarescueprd` (PRD)

### 1.3 Containers
- staging, bronze, silver, gold (em ambos storages)

### 1.4 Access Connector
- Criar apenas um Access Connector: `srv_unity` (no DEV)

## 2. Permissões para o Access Connector

Obtenha o principalId do Access Connector:
```bash
az resource show --ids /subscriptions/<subscription_id>/resourceGroups/rg_rescue_dev/providers/Microsoft.Databricks/accessConnectors/srv_unity --query "identity.principalId" -o tsv
# Exemplo: 64b1e885-a2e8-413b-bc6a-39b3c9c938ff
```
Atribua as permissões nos storages e containers de DEV e PRD:
```bash
# Storage Account
az role assignment create --assignee <principalId> --role "Storage Blob Data Contributor" --scope /subscriptions/<subscription_id>/resourceGroups/rg_rescue_dev/providers/Microsoft.Storage/storageAccounts/sarescuedev
az role assignment create --assignee <principalId> --role "Storage Blob Data Contributor" --scope /subscriptions/<subscription_id>/resourceGroups/rg_rescue_prd/providers/Microsoft.Storage/storageAccounts/sarescueprd
# Containers DEV
az role assignment create --assignee <principalId> --role "Storage Blob Data Contributor" --scope /subscriptions/<subscription_id>/resourceGroups/rg_rescue_dev/providers/Microsoft.Storage/storageAccounts/sarescuedev/blobServices/default/containers/staging
az role assignment create --assignee <principalId> --role "Storage Blob Data Contributor" --scope /subscriptions/<subscription_id>/resourceGroups/rg_rescue_dev/providers/Microsoft.Storage/storageAccounts/sarescuedev/blobServices/default/containers/bronze
az role assignment create --assignee <principalId> --role "Storage Blob Data Contributor" --scope /subscriptions/<subscription_id>/resourceGroups/rg_rescue_dev/providers/Microsoft.Storage/storageAccounts/sarescuedev/blobServices/default/containers/silver
az role assignment create --assignee <principalId> --role "Storage Blob Data Contributor" --scope /subscriptions/<subscription_id>/resourceGroups/rg_rescue_dev/providers/Microsoft.Storage/storageAccounts/sarescuedev/blobServices/default/containers/gold
# Containers PRD
az role assignment create --assignee <principalId> --role "Storage Blob Data Contributor" --scope /subscriptions/<subscription_id>/resourceGroups/rg_rescue_prd/providers/Microsoft.Storage/storageAccounts/sarescueprd/blobServices/default/containers/staging
az role assignment create --assignee <principalId> --role "Storage Blob Data Contributor" --scope /subscriptions/<subscription_id>/resourceGroups/rg_rescue_prd/providers/Microsoft.Storage/storageAccounts/sarescueprd/blobServices/default/containers/bronze
az role assignment create --assignee <principalId> --role "Storage Blob Data Contributor" --scope /subscriptions/<subscription_id>/resourceGroups/rg_rescue_prd/providers/Microsoft.Storage/storageAccounts/sarescueprd/blobServices/default/containers/silver
az role assignment create --assignee <principalId> --role "Storage Blob Data Contributor" --scope /subscriptions/<subscription_id>/resourceGroups/rg_rescue_prd/providers/Microsoft.Storage/storageAccounts/sarescueprd/blobServices/default/containers/gold
```

## 3. Criação dos External Storages no Unity Catalog

### DEV
```bash
databricks external-locations create staging_dev abfss://staging@sarescuedev.dfs.core.windows.net/ srv_unity --comment "External Storage Staging DEV" --profile DEV
databricks external-locations create bronze_dev abfss://bronze@sarescuedev.dfs.core.windows.net/ srv_unity --comment "External Storage Bronze DEV" --profile DEV
databricks external-locations create silver_dev abfss://silver@sarescuedev.dfs.core.windows.net/ srv_unity --comment "External Storage Silver DEV" --profile DEV
databricks external-locations create gold_dev abfss://gold@sarescuedev.dfs.core.windows.net/ srv_unity --comment "External Storage Gold DEV" --profile DEV
```

### PRD
```bash
databricks external-locations create staging_prd abfss://staging@sarescueprd.dfs.core.windows.net/ srv_unity --comment "External Storage Staging PRD" --profile PRD
databricks external-locations create bronze_prd abfss://bronze@sarescueprd.dfs.core.windows.net/ srv_unity --comment "External Storage Bronze PRD" --profile PRD
databricks external-locations create silver_prd abfss://silver@sarescueprd.dfs.core.windows.net/ srv_unity --comment "External Storage Silver PRD" --profile PRD
databricks external-locations create gold_prd abfss://gold@sarescueprd.dfs.core.windows.net/ srv_unity --comment "External Storage Gold PRD" --profile PRD
```

## 4. Catálogos e Schemas no Unity Catalog

### DEV
```bash
databricks catalogs create rescue_dev --comment "Catálogo DEV" --profile DEV
databricks schemas create rescue_b rescue_dev --storage-root "abfss://bronze@sarescuedev.dfs.core.windows.net/" --comment "Schema Bronze DEV" --profile DEV
databricks schemas create rescue_s rescue_dev --storage-root "abfss://silver@sarescuedev.dfs.core.windows.net/" --comment "Schema Silver DEV" --profile DEV
databricks schemas create rescue_g rescue_dev --storage-root "abfss://gold@sarescuedev.dfs.core.windows.net/" --comment "Schema Gold DEV" --profile DEV
```

### PRD
```bash
databricks catalogs create rescue_prd --comment "Catálogo PRD" --profile PRD
databricks schemas create rescue_b rescue_prd --storage-root "abfss://bronze@sarescueprd.dfs.core.windows.net/" --comment "Schema Bronze PRD" --profile PRD
databricks schemas create rescue_s rescue_prd --storage-root "abfss://silver@sarescueprd.dfs.core.windows.net/" --comment "Schema Silver PRD" --profile PRD
databricks schemas create rescue_g rescue_prd --storage-root "abfss://gold@sarescueprd.dfs.core.windows.net/" --comment "Schema Gold PRD" --profile PRD
```

## 5. Volumes para área de staging

### DEV
```bash
databricks volumes create rescue_dev rescue_b vol_stg EXTERNAL --storage-location "abfss://staging@sarescuedev.dfs.core.windows.net/" --comment "Volume Staging DEV" --profile DEV
```

### PRD
```bash
databricks volumes create rescue_prd rescue_b vol_stg EXTERNAL --storage-location "abfss://staging@sarescueprd.dfs.core.windows.net/" --comment "Volume Staging PRD" --profile PRD
```

---
Todos os comandos acima garantem governança, isolamento e automação dos ambientes Databricks DEV e PRD, utilizando o mesmo Access Connector e credencial para todos os external storages.
### Criação dos External Storages, Catálogo e Schemas em PRD via Databricks CLI

#### External Storages
```bash
databricks external-locations create bronze_prd abfss://bronze@sarescueprd.dfs.core.windows.net/ srv_unity --comment "External Storage Bronze PRD" --profile PRD
databricks external-locations create silver_prd abfss://silver@sarescueprd.dfs.core.windows.net/ srv_unity --comment "External Storage Silver PRD" --profile PRD
databricks external-locations create gold_prd abfss://gold@sarescueprd.dfs.core.windows.net/ srv_unity --comment "External Storage Gold PRD" --profile PRD
```

#### Catálogo e Schemas
```bash
# Catálogo (se não existir)
databricks catalogs create rescue_prd --comment "Catálogo PRD" --profile PRD
# Schemas
databricks schemas create rescue_b rescue_prd --storage-root "abfss://bronze@sarescueprd.dfs.core.windows.net/" --comment "Schema Bronze PRD" --profile PRD
databricks schemas create rescue_s rescue_prd --storage-root "abfss://silver@sarescueprd.dfs.core.windows.net/" --comment "Schema Silver PRD" --profile PRD
databricks schemas create rescue_g rescue_prd --storage-root "abfss://gold@sarescueprd.dfs.core.windows.net/" --comment "Schema Gold PRD" --profile PRD
```

Cada schema aponta para o external storage correspondente, garantindo governança e isolamento dos dados em produção.
### Permissões para uso do mesmo Access Connector (srv_unity) em DEV e PRD

Para utilizar o Access Connector `srv_unity` (criado em DEV) para acessar os storages de DEV e PRD, atribua o principalId do connector como "Storage Blob Data Contributor" nos containers e storage account de produção:

1. Obtenha o principalId do Access Connector:
```bash
az resource show --ids /subscriptions/eef39a8e-5a31-408a-87e8-a8b61faae822/resourceGroups/rg_rescue_dev/providers/Microsoft.Databricks/accessConnectors/srv_unity --query "identity.principalId" -o tsv
# Exemplo de retorno: 64b1e885-a2e8-413b-bc6a-39b3c9c938ff
```
2. Atribua as permissões em PRD:
```bash
az role assignment create --assignee 64b1e885-a2e8-413b-bc6a-39b3c9c938ff --role "Storage Blob Data Contributor" --scope /subscriptions/eef39a8e-5a31-408a-87e8-a8b61faae822/resourceGroups/rg_rescue_prd/providers/Microsoft.Storage/storageAccounts/sarescueprd
az role assignment create --assignee 64b1e885-a2e8-413b-bc6a-39b3c9c938ff --role "Storage Blob Data Contributor" --scope /subscriptions/eef39a8e-5a31-408a-87e8-a8b61faae822/resourceGroups/rg_rescue_prd/providers/Microsoft.Storage/storageAccounts/sarescueprd/blobServices/default/containers/bronze
az role assignment create --assignee 64b1e885-a2e8-413b-bc6a-39b3c9c938ff --role "Storage Blob Data Contributor" --scope /subscriptions/eef39a8e-5a31-408a-87e8-a8b61faae822/resourceGroups/rg_rescue_prd/providers/Microsoft.Storage/storageAccounts/sarescueprd/blobServices/default/containers/silver
az role assignment create --assignee 64b1e885-a2e8-413b-bc6a-39b3c9c938ff --role "Storage Blob Data Contributor" --scope /subscriptions/eef39a8e-5a31-408a-87e8-a8b61faae822/resourceGroups/rg_rescue_prd/providers/Microsoft.Storage/storageAccounts/sarescueprd/blobServices/default/containers/gold
```

Assim, o mesmo Access Connector pode ser usado para todos os external storages do Databricks, tanto em DEV quanto em PRD.
#### Associação do catálogo ao workspace

> **Importante:** A associação do catálogo ao workspace deve ser feita via interface web do Databricks (UI):
> 1. Acesse Unity Catalog > Catálogos > rescue_dev.
> 2. Clique em "Assign workspaces" e selecione o workspace de desenvolvimento (ID: 1293581597272291).
> 3. Salve as alterações.

#### Criação do volume vol_stg no schema rescue_b

Após associar o catálogo, execute o comando abaixo para criar o volume:

```bash
databricks volumes create rescue_dev rescue_b vol_stg EXTERNAL --storage-location "abfss://staging@sarescuedev.dfs.core.windows.net/" --comment "Volume Staging DEV" --profile DEV
```
### Criação dos Catálogos e Schemas no Unity Catalog

#### Catálogo DEV

Crie o catálogo `rescue_dev`:
```bash
databricks catalogs create --name rescue_dev --comment "Catálogo DEV" --profile DEV
```

Dentro do catálogo, crie os schemas:

- **rescue_b** (bronze)
```bash
databricks schemas create --catalog-name rescue_dev --name rescue_b --storage-location "abfss://bronze@sarescuedev.dfs.core.windows.net/" --comment "Schema Bronze DEV" --profile DEV
```

- **rescue_s** (silver)
```bash
databricks schemas create --catalog-name rescue_dev --name rescue_s --storage-location "abfss://silver@sarescuedev.dfs.core.windows.net/" --comment "Schema Silver DEV" --profile DEV
```

- **rescue_g** (gold)
```bash
databricks schemas create --catalog-name rescue_dev --name rescue_g --storage-location "abfss://gold@sarescuedev.dfs.core.windows.net/" --comment "Schema Gold DEV" --profile DEV
```

Repita o processo para o catálogo de produção (`rescue_prd`) e seus respectivos schemas, ajustando o storage account e perfil conforme necessário.
### Criação dos External Storages DEV via Databricks CLI

Para criar external storages no Unity Catalog via Databricks CLI, é necessário que o usuário tenha o privilégio **CREATE EXTERNAL LOCATION** no metastore (ser Metastore Admin ou ter permissão específica).

**Passos:**
1. No portal Databricks, acesse Unity Catalog > Metastore > Permissions e atribua o privilégio ao seu usuário.
2. Execute os comandos abaixo para criar os external storages DEV:

```bash
databricks external-locations create staging_dev abfss://staging@sarescuedev.dfs.core.windows.net/ srv_unity --comment "External Storage Staging DEV" --profile DEV
databricks external-locations create bronze_dev abfss://bronze@sarescuedev.dfs.core.windows.net/ srv_unity --comment "External Storage Bronze DEV" --profile DEV
databricks external-locations create silver_dev abfss://silver@sarescuedev.dfs.core.windows.net/ srv_unity --comment "External Storage Silver DEV" --profile DEV
databricks external-locations create gold_dev abfss://gold@sarescuedev.dfs.core.windows.net/ srv_unity --comment "External Storage Gold DEV" --profile DEV
```

**Resultado esperado:**
Os external storages serão criados e listados no Unity Catalog, cada um apontando para seu respectivo container no storage account `sarescuedev`.
### Criação dos External Storages para DEV

Serão criados quatro external storages no Unity Catalog, cada um apontando para seu respectivo container no storage account:

- **staging_dev** → `abfss://staging@<storage_account>.dfs.core.windows.net/`
- **bronze_dev**  → `abfss://bronze@<storage_account>.dfs.core.windows.net/`
- **silver_dev**  → `abfss://silver@<storage_account>.dfs.core.windows.net/`
- **gold_dev**    → `abfss://gold@<storage_account>.dfs.core.windows.net/`

Exemplo de comando para criar um external storage via Databricks CLI:

```bash
databricks unity-catalog external-locations create \
	--name staging_dev \
	--url abfss://staging@<storage_account>.dfs.core.windows.net/ \
	--credential-name <nome_credential> \
	--comment "External Storage Staging DEV" \
	--profile DEV
```

Repita o comando para bronze_dev, silver_dev e gold_dev, ajustando o nome e o container conforme necessário.
### Teste de autenticação e acesso ao workspace PRD via Databricks CLI

Após configurar o arquivo `~/.databrickscfg` com o perfil PRD e o token OAuth, execute o comando abaixo para validar o acesso:

```bash
databricks workspace list / --profile PRD
```

Exemplo de saída esperada:

```
ID                Type       Language  Path
1511173645813477  DIRECTORY            /Users
1511173645813478  DIRECTORY            /Shared
1511173645813481  DIRECTORY            /Repos
```

Se o comando retornar os diretórios principais do workspace, a autenticação está correta!
### Teste de autenticação e acesso ao workspace DEV via Databricks CLI

Após configurar o arquivo `~/.databrickscfg` com o perfil DEV e o token OAuth, execute o comando abaixo para validar o acesso:

```bash
databricks workspace list / --profile DEV
```

Exemplo de saída esperada:

```
ID                Type       Language  Path
3179726924317356  DIRECTORY            /Users
3179726924317357  DIRECTORY            /Shared
3179726924317362  DIRECTORY            /Repos
```

Se o comando retornar os diretórios principais do workspace, a autenticação está correta!


# dab
Material sobre o uso de Databricks Asset Bundles

## Sobre este Repositório

Este repositório contém materiais de testes e referências técnicas sobre o uso de Databricks Asset Bundles (DAB). O objetivo é fornecer exemplos práticos, configurações e documentação para auxiliar no desenvolvimento e implantação de projetos utilizando esta ferramenta.

## Conteúdo

O repositório incluirá:

- 📚 Materiais de referência técnica
- 🧪 Exemplos e casos de teste
- 📝 Documentação e guias de configuração
- 🎥 Links para vídeos tutoriais

## Vídeos

Serão criados vídeos explicativos sobre o uso de Databricks Asset Bundles. 

---

## Passo a passo: Criando recursos na Azure para testes

### 1. Instalar o Azure CLI
```bash
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### 2. Fazer login no Azure
```bash
az login
```

### 3. Criar um Resource Group na região mais barata dos EUA (eastus)
```bash
az group create --name rg_rescue_dev --location eastus
```

### 4. Criar uma Storage Account com ADLS Gen2 ativado e configurações de custo mínimo
```bash
az storage account create --name sarescuedev --resource-group rg_rescue_dev --location eastus --sku Standard_LRS --kind StorageV2 --hierarchical-namespace true --access-tier Cool
```

> **Observação:** O parâmetro `--hierarchical-namespace true` ativa o Data Lake Storage Gen2. O SKU `Standard_LRS` e o tier `Cool` são as opções mais econômicas para testes.

### 5. Criar os containers staging, bronze, silver e gold
```bash
az storage container create --name staging --account-name sarescuedev --resource-group rg_rescue_dev --public-access off
az storage container create --name bronze --account-name sarescuedev --resource-group rg_rescue_dev --public-access off
az storage container create --name silver --account-name sarescuedev --resource-group rg_rescue_dev --public-access off
az storage container create --name gold --account-name sarescuedev --resource-group rg_rescue_dev --public-access off
```



### 10. Criar um Azure Data Factory
```bash
az datafactory create --resource-group rg_rescue_dev --factory-name adfrescuedev --location eastus
```

> **Observação:** É necessário instalar a extensão do Azure CLI para Data Factory na primeira execução. O comando registra automaticamente o provedor de recursos se necessário.

### 11. Criar um Azure Key Vault
```bash
az provider register --namespace Microsoft.KeyVault
az keyvault create --name kvrescuedev --resource-group rg_rescue_dev --location eastus --sku standard
```



### 12. Criar e atualizar o Azure Databricks para Premium
```bash
# Criação do workspace
az databricks workspace create --name dbrrescuedev --resource-group rg_rescue_dev --location eastus --sku standard --public-network-access Enabled

# Atualização do SKU para Premium (necessário para Unity Catalog)
az databricks workspace update --name dbrrescuedev --resource-group rg_rescue_dev --sku premium
```

O link de acesso ao workspace Databricks será exibido ao final do comando, por exemplo:
```
https://adb-1293581597272291.11.azuredatabricks.net
```

### Instalar o Databricks CLI moderno (recomendado para Unity Catalog)
```bash
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sudo bash
```

> **Observação:** Instale apenas pelo método acima. Não use `pip install databricks-cli`, pois instala a versão legacy (antiga), incompatível com Unity Catalog e OAuth.

### 13. Criar Access Connector para Databricks e atribuir permissões
```bash
az databricks access-connector create --name srv_unity --resource-group rg_rescue_dev --location eastus
az databricks access-connector update --name srv_unity --resource-group rg_rescue_dev --set identity.type=SystemAssigned
```

Obtenha o principalId da identidade gerenciada:
```bash
az databricks access-connector show --name srv_unity --resource-group rg_rescue_dev --query "identity.principalId" -o tsv
```

Com o principalId, atribua o papel Storage Blob Data Contributor ao storage account e aos containers:
```bash
# Storage Account
az role assignment create --assignee <principalId> --role "Storage Blob Data Contributor" --scope /subscriptions/<subscriptionId>/resourceGroups/rg_rescue_dev/providers/Microsoft.Storage/storageAccounts/sarescuedev

# Containers
az role assignment create --assignee <principalId> --role "Storage Blob Data Contributor" --scope /subscriptions/<subscriptionId>/resourceGroups/rg_rescue_dev/providers/Microsoft.Storage/storageAccounts/sarescuedev/blobServices/default/containers/staging
az role assignment create --assignee <principalId> --role "Storage Blob Data Contributor" --scope /subscriptions/<subscriptionId>/resourceGroups/rg_rescue_dev/providers/Microsoft.Storage/storageAccounts/sarescuedev/blobServices/default/containers/bronze
az role assignment create --assignee <principalId> --role "Storage Blob Data Contributor" --scope /subscriptions/<subscriptionId>/resourceGroups/rg_rescue_dev/providers/Microsoft.Storage/storageAccounts/sarescuedev/blobServices/default/containers/silver
az role assignment create --assignee <principalId> --role "Storage Blob Data Contributor" --scope /subscriptions/<subscriptionId>/resourceGroups/rg_rescue_dev/providers/Microsoft.Storage/storageAccounts/sarescuedev/blobServices/default/containers/gold
az role assignment create --assignee <principalId> --role "Storage Blob Data Contributor" --scope /subscriptions/<subscriptionId>/resourceGroups/rg_rescue_dev/providers/Microsoft.Storage/storageAccounts/sarescuedev/blobServices/default/containers/$web
```

---

## Ambiente Produtivo

### 1. Criar o resource group produtivo
```bash
az group create --name rg_rescue_prd --location eastus
```

### 2. Criar Storage Account com ADLS Gen2 ativado
```bash
az storage account create --name sarescueprd --resource-group rg_rescue_prd --location eastus --sku Standard_LRS --kind StorageV2 --hierarchical-namespace true --access-tier Cool
```

### 3. Criar os containers staging, bronze, silver e gold
```bash
az storage container create --name staging --account-name sarescueprd --resource-group rg_rescue_prd --public-access off
az storage container create --name bronze --account-name sarescueprd --resource-group rg_rescue_prd --public-access off
az storage container create --name silver --account-name sarescueprd --resource-group rg_rescue_prd --public-access off
az storage container create --name gold --account-name sarescueprd --resource-group rg_rescue_prd --public-access off
```

### 4. Ativar o serviço de static website
```bash
az storage blob service-properties update --account-name sarescueprd --static-website --index-document portal_prd.html --404-document portal_prd.html
```

### 5. Criar o arquivo portal_prd.html
```html
<!DOCTYPE html>
<html lang="pt-br">
<head>
	<meta charset="UTF-8">
	<title>Portal Produtivo</title>
</head>
<body>
	<h1>Bem-vindo ao Portal Produtivo!</h1>
	<p>Esta é a página inicial do static website configurado no Azure Storage para produção.</p>
</body>
</html>
```

### 6. Fazer upload do portal_prd.html para o container $web
```bash
az storage blob upload --account-name sarescueprd --account-key <SUA_ACCOUNT_KEY> --container-name '$web' --name portal_prd.html --file portal_prd.html
```

### 7. Criar Azure Data Factory
```bash
az datafactory create --resource-group rg_rescue_prd --factory-name adfrescueprd --location eastus
```

### 8. Criar Azure Key Vault
```bash
az keyvault create --name kvrescueprd --resource-group rg_rescue_prd --location eastus --sku standard
```


### 9. Criar e atualizar o Azure Databricks para Premium
```bash
# Criação do workspace
az databricks workspace create --name dbrrescueprd --resource-group rg_rescue_prd --location eastus --sku standard --public-network-access Enabled

# Atualização do SKU para Premium (necessário para Unity Catalog)
az databricks workspace update --name dbrrescueprd --resource-group rg_rescue_prd --sku premium
```

> **Observação:** O Access Connector srv_unity criado no ambiente de desenvolvimento será reutilizado no ambiente produtivo.

### 10. Configurar o metastore do Unity Catalog

#### Pré-requisitos
- Storage Account: `sametarescue`
- Container: `meta`
- Resource ID: `/subscriptions/eef39a8e-5a31-408a-87e8-a8b61faae822/resourceGroups/rg_rescue_prd/providers/Microsoft.Storage/storageAccounts/sametarescue`
- Subscription ID: `eef39a8e-5a31-408a-87e8-a8b61faae822`
- Resource Group: `rg_rescue_prd`
- Workspace URL: `adb-2533506717590470.10.azuredatabricks.net`


### 1. Autentique o Databricks CLI
```bash
databricks auth login --host https://adb-2533506717590470.10.azuredatabricks.net
```

### 1. Autentique o Databricks CLI
#### Opção recomendada para ambientes remotos (Codespaces)
1. Realize o login no Databricks CLI em uma máquina local:
	```bash
	databricks auth login --host https://adb-2533506717590470.10.azuredatabricks.net
	```
2. Copie o arquivo de configuração gerado (`~/.databrickscfg`) para o Codespaces (por SCP, SFTP ou manualmente).
3. O arquivo deve ser colocado em `/home/codespace/.databrickscfg`.

Exemplo de conteúdo do arquivo:
```ini
[DEFAULT]
host = https://adb-2533506717590470.10.azuredatabricks.net
token = dapiXXXXXXXXXXXXXXXXXXXXXXXX
```

> **Observação:** O token é gerado durante o login OAuth ou pode ser criado manualmente no portal Databricks.

> **Atenção:** Desde julho de 2024, o Azure alterou o fluxo de login para contas pessoais e administradores globais. Agora, o acesso ao console e ao Databricks deve ser feito usando o usuário externo criado automaticamente pelo Azure, que contém `#EXT#` no nome (exemplo: `anselmoborges_gmail.com#EXT#@anselmoborgesgmail.onmicrosoft.com`).
> Esse usuário externo possui as permissões de Global Administrator e Databricks Account Admin. O login com a conta original (ex: seuemail@outlook.com) pode gerar erro de permissão.

> Recomenda-se configurar o Databricks CLI para usar o usuário externo com `#EXT#` para garantir acesso total aos recursos.


#### 2. Crie e atribua o metastore do Unity Catalog via interface web (UI)

1. Acesse o portal Databricks (https://accounts.azuredatabricks.net) com o usuário externo (`#EXT#`).
2. No menu lateral, vá em "Unity Catalog" > "Metastores".
3. Clique em "Create Metastore" e preencha:
	 - Nome: `metastore-rescue`
	 - Storage root: `abfss://meta@sametarescue.dfs.core.windows.net/`
	 - Região: `eastus`
4. Após criar, associe o metastore aos dois workspaces criados (dev e prd).

> **Observação:** Esse procedimento garante que o metastore seja criado corretamente e atribuído aos workspaces, mesmo se houver problemas com o CLI.

---
Esses comandos configuram o metastore do Unity Catalog apontando para o storage e container corretos, garantindo governança centralizada de dados.

### Primeiro Vídeo: Configuração do VSCode

O primeiro vídeo da série abordará como configurar o Visual Studio Code para trabalhar com:

- Databricks
- Databricks SQL
- Databricks CLI

Este vídeo fornecerá um guia passo a passo para preparar seu ambiente de desenvolvimento local.
