# ⚡ Comandos Rápidos para Deploy

## 🚀 Deploy Inicial

### 1. Fazer commit das alterações
```bash
git add .
git commit -m "Preparar projeto para deploy no Streamlit Cloud"
git push origin main
```

### 2. Acessar Streamlit Cloud
```
https://streamlit.io/cloud
```

### 3. Configuração do Deploy
```
Repository: elfabitto/dashboard_project
Branch: main
Main file: dashboard_app.py
```

---

## 🔄 Atualizar Aplicação

Sempre que fizer alterações:

```bash
# 1. Adicionar arquivos modificados
git add .

# 2. Fazer commit com mensagem descritiva
git commit -m "Descrição da alteração"

# 3. Enviar para GitHub
git push origin main

# 4. Streamlit Cloud atualiza automaticamente! ✓
```

---

## 🧪 Testar Localmente Antes do Deploy

```bash
# Ativar ambiente virtual (se tiver)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Executar aplicação
streamlit run dashboard_app.py

# Acessar no navegador
# http://localhost:8501
```

---

## 📦 Adicionar Nova Dependência

```bash
# 1. Instalar o pacote
pip install nome-do-pacote

# 2. Atualizar requirements.txt
pip freeze > requirements.txt

# 3. Fazer commit
git add requirements.txt
git commit -m "Adicionar dependência: nome-do-pacote"
git push origin main
```

---

## 🗂️ Adicionar Arquivo de Dados

```bash
# 1. Adicionar arquivo ao repositório
git add seu_arquivo.xlsx

# 2. Fazer commit
git commit -m "Adicionar arquivo de dados"

# 3. Enviar para GitHub
git push origin main
```

---

## 🔍 Verificar Status do Git

```bash
# Ver arquivos modificados
git status

# Ver histórico de commits
git log --oneline

# Ver diferenças
git diff
```

---

## 🌿 Trabalhar com Branches (Opcional)

```bash
# Criar nova branch para desenvolvimento
git checkout -b desenvolvimento

# Fazer alterações e commit
git add .
git commit -m "Nova funcionalidade"

# Voltar para main
git checkout main

# Fazer merge da branch
git merge desenvolvimento

# Enviar para GitHub
git push origin main
```

---

## 🆘 Comandos de Emergência

### Desfazer último commit (mantém alterações)
```bash
git reset --soft HEAD~1
```

### Descartar todas as alterações locais
```bash
git reset --hard HEAD
```

### Atualizar repositório local
```bash
git pull origin main
```

### Ver URL do repositório remoto
```bash
git remote -v
```

---

## 📊 Verificar Logs do Streamlit Cloud

1. Acesse: https://streamlit.io/cloud
2. Clique na sua aplicação
3. Clique em "Manage app" → "Logs"
4. Veja erros e mensagens em tempo real

---

## ✅ Checklist Rápido

Antes de cada deploy:

```bash
# 1. Testar localmente
streamlit run dashboard_app.py

# 2. Verificar alterações
git status

# 3. Adicionar arquivos
git add .

# 4. Fazer commit
git commit -m "Descrição clara"

# 5. Enviar para GitHub
git push origin main

# 6. Verificar deploy no Streamlit Cloud
# (abre automaticamente em ~2 minutos)
```

---

## 🎯 URLs Importantes

- **Repositório GitHub**: https://github.com/elfabitto/dashboard_project
- **Streamlit Cloud**: https://streamlit.io/cloud
- **Documentação**: https://docs.streamlit.io

---

## 💡 Dicas

1. **Sempre teste localmente antes de fazer push**
2. **Use mensagens de commit descritivas**
3. **Faça commits pequenos e frequentes**
4. **Verifique os logs se algo der errado**
5. **Mantenha o requirements.txt atualizado**

---

## 🎉 Pronto!

Seu workflow de deploy está configurado!

```bash
# Fluxo completo em 3 comandos:
git add .
git commit -m "Sua mensagem"
git push origin main
```

**Deploy automático em ~2 minutos! 🚀**
