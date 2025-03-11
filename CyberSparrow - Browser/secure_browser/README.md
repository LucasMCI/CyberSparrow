# CyberSparrow

Um navegador web seguro desenvolvido em Python para profissionais de cibersegurança.

## Funcionalidades

### 1. Navegação Segura
- Bloqueio de scripts maliciosos
- Proteção contra rastreadores
- Modo de navegação anônima
- DNS sobre HTTPS (DoH)

### 2. Ferramentas Red Team
- WHOIS - Consulta informações de domínios
- Enumeração DNS - Busca registros DNS
- Scanner de Portas - Varredura de portas TCP
- Busca de Subdomínios
- Crawler Web
- Detecção de WAF
- Análise de Headers de Segurança
- Verificação de CORS

### 3. Análise de Tráfego
- Captura de pacotes em tempo real
- Inspeção de conexões
- Estatísticas de tráfego
- Detecção de anomalias

### 4. Privacidade
- Bloqueio de fingerprinting
- Sem histórico persistente
- Proteção contra vazamento de DNS
- Cookies temporários

### 5. Interface
- Design moderno e intuitivo
- Suporte a múltiplas abas
- Barra de ferramentas personalizável
- Atalhos de teclado

## Requisitos

- Python 3.6+
- PyQt6
- PyQt6-WebEngine
- Outras dependências listadas em requirements.txt

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/LucasMCI/CyberSparrow.git
cd CyberSparrow
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Execute o navegador:
```bash
python src/main.py
```

## Atalhos de Teclado

- `Ctrl+T` - Nova aba
- `Ctrl+H` - Histórico
- `Ctrl+R` - Ferramentas Red Team
- `Ctrl+Q` - Sair

## Contribuição

Sinta-se à vontade para contribuir com o projeto através de pull requests.

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Autor

Criado por Lucas MCI.
[@LucasMCI](https://github.com/LucasMCI) 