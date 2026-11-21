# ⌬ berlip_MS
### ✦ MONITOR DE REDE PROFISSIONAL

<p align="center">
  ◈ Monitore. Analise. Otimize. ◈
  
  Aplicativo desktop para **Windows e Linux** que monitora a qualidade da sua conexão em tempo real.
  
  `LATÊNCIA`　·　`JITTER`　·　`PERDA DE PACOTES`　·　`VELOCIDADE`
</p>

<p align="center">
  <img src="docs/screenshots/dashboard.gif" width="75%" alt="Dashboard">
</p>

<p align="center">
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
</p>

## ◈ Destaques

> Uma visão completa da sua conexão, com informações em tempo real e ferramentas de diagnóstico.

- ◉ **Dashboard ao vivo** com gráficos suaves e indicadores.
- ◉ **Monitoramento contínuo** sem travar a interface.
- ◉ **Ferramentas de rede** para diagnóstico e análise.
- ◉ **Histórico local** com exportação CSV e JSON.
- ◉ **Interface Dark** minimalista e intuitiva.

<p align="center">
  <img src="docs/screenshots/monitoring.gif" width="75%" alt="Monitoramento">
</p>

---

## ⌘ Funcionalidades

| ◇ Área | ◇ Descrição |
|:---|:---|
| **◈ Dashboard** | Ping, jitter, perda, download/upload e gráficos em tempo real |
| **◈ Monitoramento** | Acompanhamento contínuo com destino e intervalo configuráveis |
| **◈ Ferramentas** | Ping em série, velocidade, DNS, traceroute, portas e adaptadores |
| **◈ Histórico** | SQLite local, filtros por período e exportação CSV/JSON |
| **◈ Configurações** | Tema escuro, PT-BR, limiares e retenção do histórico |

<p align="center">
  <img src="docs/screenshots/tools.jpg" width="75%" alt="Ferramentas">
</p>

---

## ⇩ Instalação

O berlip_MS pode ser instalado no **Windows e Linux**. Siga as instruções correspondentes ao seu sistema operacional.

### ◈ Requisitos

- Python **3.12 ou superior**.
- Git (para clonar o repositório).
- Conexão com a internet durante a instalação das dependências.

### 🪟 Windows

**① Instale o Python**

Baixe o Python 3.12 ou superior pelo site oficial:

https://www.python.org/downloads/windows/

Durante a instalação, habilite a opção **Add Python to PATH**.

**② Baixe o projeto**

Abra o PowerShell e execute:

```powershell
git clone https://github.com/SEU_USUARIO/berlip_MS.git
cd berlip_MS
```

**③ Crie o ambiente virtual**

```powershell
py -3.12 -m venv .venv
```

**④ Instale as dependências**

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements-runtime.txt
```

**⑤ Inicie o aplicativo**

```powershell
.\.venv\Scripts\python.exe main.py
```

**Próximas inicializações:** basta entrar na pasta do projeto e executar:

```powershell
.\.venv\Scripts\python.exe main.py
```

### 🐧 Linux

**① Instale os requisitos do sistema**

Em distribuições baseadas em Debian/Ubuntu:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip git
```

Em Arch Linux:

```bash
sudo pacman -S python python-pip git
```

**② Baixe o projeto**

```bash
git clone https://github.com/SEU_USUARIO/berlip_MS.git
cd berlip_MS
```

**③ Crie o ambiente virtual**

```bash
python3 -m venv .venv
```

**④ Ative o ambiente virtual**

```bash
source .venv/bin/activate
```

**⑤ Instale as dependências**

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements-runtime.txt
```

**⑥ Inicie o aplicativo**

```bash
python main.py
```

**Próximas inicializações:** entre na pasta do projeto, ative o ambiente virtual e execute:

```bash
source .venv/bin/activate
python main.py
```

---

## ◈ Solução de problemas

- **Python não encontrado:** confira se o Python está instalado e disponível no PATH.
- **Erro ao criar o ambiente virtual:** verifique se o pacote `python3-venv` está instalado no Linux.
- **Erro ao instalar dependências:** confira sua conexão com a internet e a versão do Python.
- **Aplicativo não abre:** execute pelo terminal para visualizar a mensagem de erro.

---

<p align="center">
  <sub>⌬ berlip_MS · Desenvolvido por <strong>berlip</strong></sub>
  <br>
  <sub>Monitoramento de rede com simplicidade e precisão.</sub>
</p>
