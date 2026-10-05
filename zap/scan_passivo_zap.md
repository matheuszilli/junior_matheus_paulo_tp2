# Análise do scan passivo OWASP ZAP

## Informações da execução

- Ferramenta: OWASP ZAP Baseline Scan
- Tipo: spider seguido apenas por regras passivas
- Alvo: `http://host.docker.internal:8000/docs`
- Data da validação final: 05/10/2026
- Relatório HTML: `zap/relatorio_zap.html`

O primeiro scan encontrou quatro findings de severidade Medium na página da documentação. Depois das correções, o scan foi repetido. O relatório final não possui findings Medium ou High.

## Finding 1 — CSP sem diretiva `form-action`

1. **Finding:** CSP: Failure to Define Directive with No Fallback (`10055`).
2. **Severidade:** Medium.
3. **Confiança:** High.
4. **URL afetada:** `http://host.docker.internal:8000/docs`.
5. **O que foi detectado:** a política CSP não definia `form-action`, uma diretiva que não utiliza `default-src` como fallback.
6. **Por que é um problema:** sem a diretiva, formulários poderiam enviar dados para destinos não autorizados caso algum conteúdo fosse injetado na página.
7. **Correção realizada:** foram adicionadas `form-action 'none'`, `base-uri 'none'` e `object-src 'none'` à CSP.
8. **Validação:** a regra CSP (`10055`) apareceu como `PASS` no scan final.
9. **Risco aceito:** nenhum; o finding foi corrigido.

## Finding 2 — `unsafe-inline` em `script-src`

1. **Finding:** CSP: script-src unsafe-inline (`10055`).
2. **Severidade:** Medium.
3. **Confiança:** High.
4. **URL afetada:** `http://host.docker.internal:8000/docs`.
5. **O que foi detectado:** a CSP permitia a execução geral de scripts inline.
6. **Por que é um problema:** `unsafe-inline` reduz a proteção da CSP contra injeção de JavaScript e XSS.
7. **Correção realizada:** `unsafe-inline` foi removido. A inicialização do Swagger passou a usar um nonce aleatório gerado a cada resposta.
8. **Validação:** a regra CSP (`10055`) apareceu como `PASS` no scan final.
9. **Risco aceito:** nenhum; o finding foi corrigido.

## Finding 3 — `unsafe-inline` em `style-src`

1. **Finding:** CSP: style-src unsafe-inline (`10055`).
2. **Severidade:** Medium.
3. **Confiança:** High.
4. **URL afetada:** `http://host.docker.internal:8000/docs`.
5. **O que foi detectado:** a CSP aceitava estilos inline sem restrição.
6. **Por que é um problema:** estilos injetados podem ser utilizados para modificar ou ocultar elementos da interface e facilitar ataques de engenharia social.
7. **Correção realizada:** `unsafe-inline` foi removido de `style-src`; somente a origem específica do arquivo CSS do Swagger foi mantida.
8. **Validação:** a regra CSP (`10055`) apareceu como `PASS` no scan final.
9. **Risco aceito:** nenhum; o finding foi corrigido.

## Finding 4 — Subresource Integrity ausente

1. **Finding:** Sub Resource Integrity Attribute Missing (`90003`).
2. **Severidade:** Medium.
3. **Confiança:** High.
4. **URL afetada:** `http://host.docker.internal:8000/docs`.
5. **O que foi detectado:** os arquivos JavaScript e CSS do Swagger eram carregados de um CDN sem atributo `integrity`.
6. **Por que é um problema:** uma alteração indevida no arquivo hospedado externamente poderia fazer o navegador executar conteúdo diferente do esperado.
7. **Correção realizada:** a versão do Swagger foi fixada em `5.33.1`; os elementos `script` e `link` receberam hashes SHA-384 e `crossorigin="anonymous"`.
8. **Validação:** a regra Subresource Integrity (`90003`) apareceu como `PASS` no scan final.
9. **Risco aceito:** nenhum; o finding foi corrigido.

## Resultado final

O scan final registrou:

- 0 findings High;
- 0 findings Medium;
- 0 findings Low;
- 2 observações Informational;
- 65 regras com resultado `PASS`.

As duas observações restantes foram:

- `Non-Storable Content`: consequência intencional do header `Cache-Control: no-store`, usado para impedir armazenamento de respostas sensíveis;
- `Modern Web Application`: classificação informativa da página Swagger, sem vulnerabilidade associada.

Também foram validados como `PASS` os headers CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Permissions-Policy, os atributos de Subresource Integrity e os headers de isolamento entre origens.
