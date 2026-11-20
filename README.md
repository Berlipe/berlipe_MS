```markdown
# berlip_MS
### Monitor de Rede Profissional

Aplicativo desktop para Windows e Linux que monitora a qualidade da sua conexão em tempo real.

**Latência · Jitter · Perda de pacotes · Velocidade · Ferramentas de rede**

<p align="center">
  <img src="docs/screenshots/dashboard.png" width="85%" alt="Dashboard">
</p>

---

## Destaques

- Dashboard ao vivo com gráficos suaves
- Monitoramento contínuo sem travar a interface
- Ping, DNS, traceroute, portas TCP e adaptadores
- Histórico local com exportação CSV/JSON
- Tema dark minimalista

<p align="center">
  <img src="docs/screenshots/monitoring.gif" width="85%" alt="Monitoramento">
</p>

---

## Funcionalidades

| Área | O que faz |
|------|-----------|
| **Dashboard** | Ping, jitter, perda, download/upload e gráficos em tempo real |
| **Monitoramento** | Acompanhamento contínuo com destino e intervalo configuráveis |
| **Ferramentas** | Ping em série, velocidade, DNS, traceroute, portas e adaptadores |
| **Histórico** | SQLite local, filtros por período e exportação CSV/JSON |
| **Configurações** | Tema escuro, PT-BR, limiares e retenção do histórico |

<p align="center">
  <img src="docs/screenshots/tools.png" width="85%" alt="Ferramentas">
</p>

---

## Instalação rápida

```bash
git clone https://github.com/SEU_USUARIO/berlip_MS.git
cd berlip_MS
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
python main.py
```

**Requisitos:** Python 3.12+ · Windows 10/11 ou Linux

---

## Gerar executável

**Windows**
```bat
packaging\windows\build.bat
```

**Linux**
```bash
./packaging/linux/build.sh
```

O binário fica em `dist/`.

---

## Estrutura

```
app/          → núcleo, rede, UI, workers
tests/        → testes automatizados
packaging/    → scripts de build
.github/      → CI (testes e builds)
```

---

## Observações

- O teste de velocidade é uma aproximação (não substitui speedtest.net)
- Ping raw pode precisar de privilégios; há fallback automático para o `ping` do sistema

---

## Licença

MIT © berlip_MS
```
