# Usuários e níveis de acesso

## Arquivo de usuários

O arquivo ativo é `backend_python/users.json`. Ele é local, ignorado pelo Git e lido sempre que alguém faz login. O formato é uma lista:

```json
[
  {
    "username": "usuario",
    "password_hash": "HASH_GERADO_PELO_SCRIPT",
    "access_level": "spy_car"
  }
]
```

Valores permitidos para `access_level`:

| Valor | Acesso |
| --- | --- |
| `spy_car` | Campanhas e CRM da Spy car |
| `g_system` | Campanhas e CRM da G-System |
| `diretoria` | Acesso completo às campanhas e ao CRM das duas empresas |

As senhas não devem ser gravadas em texto puro. No diretório `backend_python`, execute `python scripts/generate_password_hash.py`, informe e confirme a senha, e copie o valor impresso para `password_hash`. Adicione ou remova usuários editando `users.json`; não é necessário reiniciar o backend para que alterações sejam usadas no próximo login.

`backend_python/users.example.json` é somente um modelo. O arquivo ativo começa vazio; cadastre pelo menos um usuário antes de entrar no sistema.

## Chave de sessão

Configure `AUTH_SECRET` no `backend_python/.env` com uma chave aleatória longa. Para gerar uma, execute:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Mantenha o valor em segredo e não o envie no chat. Reinicie o backend após configurar a chave. As sessões expiram após 12 horas.

## Escopo dos dados

Campanhas novas criadas por usuários Spy car ou G-System pertencem automaticamente à empresa do usuário. A Diretoria escolhe a empresa no formulário de nova campanha. Os leads gerados herdam a empresa da campanha; as listas, consultas, exportações e métricas do CRM respeitam esse escopo.

Os registros que já existiam quando o isolamento foi implantado foram atribuídos à G-System, conforme definido para esta instalação. Usuários da Diretoria podem consultar, alterar e excluir campanhas/CRM de ambas as empresas. As configurações globais e a migração do banco também são restritas à Diretoria.

O endpoint de pré-visualização de landing pages permanece público para permitir o compartilhamento dos sites gerados; os demais endpoints de campanhas e leads exigem sessão autenticada.
