# 🚀 Guia de Deploy no Streamlit Cloud

## 📋 Pré-requisitos

- Conta no GitHub (você já tem ✓)
- Conta no Streamlit Cloud (vamos criar)
- Repositório já está no GitHub ✓

## 🎯 Passo a Passo Completo

### 1️⃣ Preparar o Repositório

Seu repositório já está quase pronto! Vamos apenas garantir que tudo está correto:

#### ✅ Arquivos Necessários (já existem):
- `dashboard_app.py` - Aplicação principal ✓
- `requirements.txt` - Dependências ✓
- `logo-aguas-do-para.png` - Logo ✓

#### ⚠️ Arquivo de Dados
**IMPORTANTE**: O arquivo `BASE_GERAL_2025_10_25 VS01.xlsx` mencionado no código não está no repositório.

**Opções:**
1. **Upload manual** - Usuários fazem upload via interface
2. **Incluir arquivo de amostra** - Adicionar arquivo exemplo
3. **Usar Google Drive/Dropbox** - Link para arquivo externo

### 2️⃣ Criar Conta no Streamlit Cloud

1. Acesse: https://streamlit.io/cloud
2. Clique em **"Sign up"**
3. Escolha **"Continue with GitHub"**
4. Autorize o Streamlit a acessar seus repositórios

### 3️⃣ Fazer Deploy da Aplicação

1. **No Streamlit Cloud Dashboard:**
   - Clique em **"New app"**

2. **Configurar o Deploy:**
   ```
   Repository: elfabitto/dashboard_project
   Branch: main (ou master)
   Main file path: dashboard_app.py
   ```

3. **App URL (opcional):**
   - Você pode personalizar: `seu-nome-dashboard.streamlit.app`
   - Ou deixar o padrão: `dashboard-project-xxx.streamlit.app`

4. **Clique em "Deploy!"**

### 4️⃣ Aguardar o Deploy

O Streamlit Cloud vai:
- ✓ Clonar seu repositório
- ✓ Instalar dependências do `requirements.txt`
- ✓ Iniciar a aplicação
- ✓ Gerar URL pública

**Tempo estimado:** 2-5 minutos

### 5️⃣ Acessar sua Aplicação

Após o deploy, você receberá uma URL como:
```
https://seu-app.streamlit.app
```

## 🔧 Configurações Adicionais

### Secrets (Dados Sensíveis)

Se precisar de variáveis de ambiente ou senhas:

1. No dashboard do Streamlit Cloud
2. Clique em **"Settings"** → **"Secrets"**
3. Adicione no formato TOML:
```toml
# Exemplo
[database]
host = "seu-host"
password = "sua-senha"
```

### Recursos da Aplicação

**Plano Gratuito:**
- ✓ 1 GB de RAM
- ✓ 1 CPU compartilhado
- ✓ Aplicações públicas ilimitadas
- ✓ SSL/HTTPS automático
- ✓ Domínio personalizado

## 📊 Gerenciar Dados

### Opção 1: Upload Manual (Atual)
Sua aplicação já tem upload de arquivos implementado! ✓
```python
uploaded_file = st.sidebar.file_uploader(...)
```

### Opção 2: Arquivo no Repositório
Se quiser incluir dados padrão:

1. Adicione o arquivo Excel ao repositório
2. Faça commit e push:
```bash
git add seu_arquivo.xlsx
git commit -m "Adicionar dados padrão"
git push origin main
```

3. O Streamlit Cloud atualizará automaticamente

### Opção 3: Google Drive/Dropbox
Para arquivos grandes, use links externos:
```python
# Exemplo com Google Drive
import gdown
url = 'https://drive.google.com/uc?id=SEU_ID'
gdown.download(url, 'dados.xlsx', quiet=False)
```

## 🔄 Atualizações Automáticas

**Toda vez que você fizer push no GitHub:**
- O Streamlit Cloud detecta automaticamente
- Faz redeploy da aplicação
- Sem necessidade de configuração manual!

```bash
# Fluxo de atualização
git add .
git commit -m "Atualização do dashboard"
git push origin main
# Streamlit Cloud atualiza automaticamente! 🎉
```

## 🐛 Solução de Problemas

### Erro: "Module not found"
**Solução:** Adicione o módulo ao `requirements.txt`
```bash
# Exemplo
pandas==2.1.0
plotly==5.17.0
```

### Erro: "File not found"
**Solução:** Verifique os caminhos dos arquivos
```python
# Use caminhos relativos
logo_path = Path("logo-aguas-do-para.png")
```

### Aplicação Lenta
**Soluções:**
1. Use `@st.cache_data` para cache (já implementado ✓)
2. Reduza tamanho dos dados
3. Otimize queries e processamento

### Erro de Memória
**Soluções:**
1. Reduza tamanho do DataFrame
2. Use amostragem de dados
3. Considere upgrade para plano pago

## 📱 Compartilhar Aplicação

Após o deploy, compartilhe a URL:
```
https://seu-dashboard.streamlit.app
```

**Recursos:**
- ✓ Acesso público (sem login necessário)
- ✓ HTTPS automático (seguro)
- ✓ Responsivo (funciona em mobile)
- ✓ Sem limite de visitantes

## 🎨 Personalização de Domínio

**Plano Gratuito:**
- Subdomínio: `seu-app.streamlit.app`

**Plano Pago ($20/mês):**
- Domínio customizado: `dashboard.suaempresa.com`
- Mais recursos (CPU, RAM)
- Aplicações privadas

## 📈 Monitoramento

No dashboard do Streamlit Cloud você pode ver:
- 📊 Número de visitantes
- ⏱️ Tempo de resposta
- 💾 Uso de memória
- 🔄 Status do deploy
- 📝 Logs da aplicação

## 🔐 Segurança

### Tornar Aplicação Privada (Plano Pago)
1. Settings → Privacy
2. Escolha "Private"
3. Adicione emails autorizados

### Proteger Dados Sensíveis
```python
# Use st.secrets para dados sensíveis
import streamlit as st

# Não faça isso:
senha = "minha_senha_123"  # ❌

# Faça isso:
senha = st.secrets["database"]["password"]  # ✓
```

## 📚 Recursos Úteis

- 📖 [Documentação Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud)
- 💬 [Fórum da Comunidade](https://discuss.streamlit.io/)
- 🎓 [Tutoriais](https://docs.streamlit.io/library/get-started)
- 🐛 [Reportar Bugs](https://github.com/streamlit/streamlit/issues)

## ✅ Checklist Final

Antes de fazer deploy, verifique:

- [ ] `requirements.txt` está atualizado
- [ ] Código está funcionando localmente
- [ ] Arquivos necessários estão no repositório
- [ ] Caminhos de arquivos estão corretos
- [ ] Dados sensíveis estão em secrets (se houver)
- [ ] README.md está atualizado (opcional)

## 🎉 Pronto!

Sua aplicação estará disponível em:
```
https://[seu-app].streamlit.app
```

**Vantagens do Streamlit Cloud:**
- ✓ 100% Gratuito para uso público
- ✓ Deploy em minutos
- ✓ Atualizações automáticas
- ✓ SSL/HTTPS incluído
- ✓ Sem configuração de servidor
- ✓ Escalável automaticamente

---

## 🆘 Precisa de Ajuda?

Se encontrar problemas:
1. Verifique os logs no dashboard do Streamlit Cloud
2. Consulte a documentação oficial
3. Pergunte no fórum da comunidade
4. Revise este guia

**Boa sorte com seu deploy! 🚀**
