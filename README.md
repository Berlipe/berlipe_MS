# berlip_MS . Monitor de Rede Profissional

Aplicativo desktop multiplataforma para monitoramento de qualidade de conexão de rede.

**Latência • Jitter • Perda de pacotes • Velocidade • Ferramentas de rede**

---

## Funcionalidades

### Dashboard
- Ping atual e médio
- Jitter e perda de pacotes
- Estimativa de download / upload
- Status da conexão
- Gráfico de latência em tempo real
- Gráfico de velocidade

### Monitoramento
- Monitoramento contínuo em background (não trava a interface)
- Destino configurável (IP ou hostname)
- Intervalo de atualização ajustável
- Tabela das últimas medições
- Persistência automática no SQLite

### Ferramentas
- Teste de ping (série) com estatísticas de jitter e perda
- Teste de velocidade leve (endpoints públicos)
- Consulta DNS (forward e reverse)
- Traceroute
- Verificação de portas TCP
- Informações dos adaptadores de rede e contadores I/O

### Histórico
- Armazenamento local em SQLite
- Filtro por período (24 h / 7 d / 30 d / tudo)
- Exportação CSV e JSON

### Configurações
- Tema escuro
- Idioma: Português (Brasil)
- Intervalo, timeout, destino padrão
- Limiares de notificação
- Retenção e limpeza de histórico

---

## Requisitos

- Python **3.12+**
- Windows 10/11 ou Linux moderno
- Dependências listadas em `requirements.txt`

---

## Instalação (desenvolvimento)

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

---

## Executar testes

```bash
pip install pytest pytest-qt
pytest tests/ -v
```

---

## Gerar executável

### Windows

```bat
packaging\windows\build.bat
```

Ou manualmente:

```bat
pip install pyinstaller
pyinstaller --noconfirm --clean --name berlip_MS --windowed --onefile main.py
```

O executável fica em `dist\berlip_MS.exe`.

### Linux

```bash
chmod +x packaging/linux/build.sh
./packaging/linux/build.sh
```

Binário em `dist/berlip_MS`.

#### AppImage (opcional)

Após gerar o binário com PyInstaller, você pode empacotar com [linuxdeploy](https://github.com/linuxdeploy/linuxdeploy) ou ferramentas similares. Um script completo de AppImage pode ser adicionado conforme a necessidade de distribuição.

#### Arch Linux (PKGBUILD)

Há um `PKGBUILD` de exemplo em `packaging/linux/PKGBUILD`. Ajuste a URL e o checksum antes de usar.

---

## Publicar no GitHub

1. Crie um repositório vazio no GitHub.
2. No diretório do projeto:

```bash
git init
git add .
git commit -m "Initial release of berlip_MS 1.0.0"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/berlip_MS.git
git push -u origin main
```

3. Crie uma tag para release:

```bash
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
```

4. Os workflows em `.github/workflows/` executam testes em push/PR e builds sob tags `v*`.

---

## Arquitetura

```
berlip_MS/
├── app/
│   ├── core/          # Configuração e constantes
│   ├── network/       # Ping, DNS, traceroute, portas, velocidade, adaptadores
│   ├── database/      # SQLite
│   ├── workers/       # QThreads para não bloquear a UI
│   ├── ui/            # Janela principal, páginas e widgets
│   └── utils/         # Formatadores
├── tests/
├── packaging/
├── .github/workflows/
├── main.py
├── requirements.txt
└── pyproject.toml
```

Operações de rede rodam em `QThread` (workers). A interface permanece responsiva.

---

## Limitações conhecidas

- O teste de velocidade é uma **aproximação** (transferência de arquivos pequenos em endpoints públicos). Não substitui speedtest.net / iperf.
- ICMP raw exige privilégios; o app usa o comando `ping` do sistema quando necessário.
- Traceroute depende de `tracert` (Windows) ou `traceroute` (Linux) instalados.

---

## Licença

MIT — veja o arquivo [LICENSE](LICENSE).

---

## Contribuição

Pull requests são bem-vindos. Mantenha o código tipado, testes para a lógica de rede/estatísticas e a interface em português brasileiro.
