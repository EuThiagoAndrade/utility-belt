# Política de Segurança — Utility Belt

A segurança dos usuários e a integridade das operações do **Utility Belt** são prioridades fundamentais.

---

## Versões com Suporte a Atualizações de Segurança

Apenas a versão mais recente publicada na branch `main` recebe correções de segurança ativas:

| Versão | Com Suporte |
| :-- | :-- |
| `>= 0.5.x` (`main`) | :white_check_mark: Sim |
| `< 0.5.0` | :x: Não |

Recomendamos que todos os usuários mantenham o pacote atualizado globalmente através de:

```bash
uv tool upgrade utility-belt
```

---

## Reportando Vulnerabilidades

Se você identificar uma falha de segurança ou vulnerabilidade em potencial no `utility-belt`, **NÃO abra uma issue pública**.

### Procedimento Recomendado

1. Utilize o canal nativo e confidencial do GitHub através de **Private Vulnerability Reporting**:
   - Acesse: [Report a Vulnerability](https://github.com/EuThiagoAndrade/utility-belt/security/advisories/new)
2. Descreva os detalhes da vulnerabilidade, passos exatos para reprodução e versão afetada.
3. Se desejar, inclua uma proposta de correção (patch) ou mitigação temporária.

### Canal Alternativo

Caso não possua conta no GitHub ou não consiga utilizar a interface de advisories, entre em contato diretamente pelo e-mail do mantenedor:
`contato@euthiagoandrade.com.br`

---

## Processo de Triagem e Resposta

1. **Confirmação de recebimento**: responderemos ao seu reporte confidencial em até 48 horas úteis.
2. **Análise e Validação**: investigaremos a severidade e o escopo do problema no ambiente afetado.
3. **Desenvolvimento da Correção**: criaremos uma branch privada e testes automatizados dedicados.
4. **Divulgação Coordenada**: após a publicação da release corrigida na branch `main`, publicaremos um Security Advisory com o devido crédito ao pesquisador/relator (salvo solicitação de anonimato).
