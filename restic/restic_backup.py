#!/usr/bin/env python3
"""Menu Restic para Python 3.10+, sem dependencias adicionais.
Execute no PowerShell: py -3 restic_backup.py
Documentacao e referencias: opcao 10.
"""
import datetime as dt
import getpass
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

BASE = Path(os.environ.get('LOCALAPPDATA', str(Path.home()))) / 'ResticMenu'
CONFIG = BASE / 'config.json'
DEFAULT = {'source': r'C:\Programas', 'repo': r'D:\Restic-Programas',
           'repo_id': '', 'exclude_file': '', 'restore_parent': r'C:\Programas_bkp'}
HELP = r'''
COMO USAR
Requisitos: Python 3.10 ou posterior e restic no PATH.
No PowerShell: py -3 .\restic_backup.py
Primeira vez? Escolha A: o assistente pergunta o que voce quer fazer.
Para salvar seus projetos: A > 1 (backup guiado).
Para recuperar arquivos na outra maquina: A > 2 (restauracao guiada).
Voce tambem pode escolher diretamente 3 (backup) ou 7 (restauracao).
Se faltar vincular o repositorio, o proprio fluxo orienta essa etapa.
As opcoes numeradas da versao anterior foram preservadas.

ORIGEM = pasta DESTA maquina que sera lida ao FAZER um novo backup.
Ela nao determina qual snapshot sera restaurado; pode nem existir no trabalho.
REPOSITORIO = pasta com os backups criptografados (por exemplo, no HD externo).
DESTINO DA RESTAURACAO = pasta que recebera os arquivos recuperados.
O local onde este script esta salvo nao determina nenhum desses caminhos.
Exemplo casa: origem C:\Programas; repositorio D:\Restic-Programas.
Exemplo trabalho: mesmo repositorio no HD; restaurar em C:\Programas_bkp.
Nunca coloque o destino da restauracao no campo repositorio.
Vincular significa lembrar e conferir o ID do repositorio; nao copia arquivos.

Todos os backups sao incrementais no armazenamento. Cada snapshot representa
o estado da pasta naquela execucao. Os dados sao criptografados, nao uma
copia navegavel da pasta no Explorador. A restauracao recupera os arquivos.
Arquivos ignorados pelo Git e a pasta .git sao incluidos, salvo exclusoes.
O script nao exclui snapshots nem executa limpeza automatica.

Salve os arquivos no editor e evite alteracoes durante o backup. Pare bancos
locais antes da copia ou produza dumps consistentes com a ferramenta do banco.
Dados de volumes Docker fora da origem nao sao incluidos automaticamente.
Snapshot salvo com codigo 3 significa backup incompleto: confira os erros.

INTEGRIDADE
Opcao 5: estrutura, indices e referencias; nao le todo o conteudo.
Opcao 6: estrutura e leitura de todos os dados. Nao repara corrupcao.
Uma restauracao de teste complementa a verificacao. O resultado vale para
a execucao registrada, nao garante a saude futura do HD.

RESTAURACAO
Selecione o snapshot por numero, conferindo data, computador e origem.
Uma subpasta nova sera criada no destino escolhido. A pasta principal pode
ser criada pelo assistente, com sua confirmacao. Nao restaure sobre
C:\Programas. O menu bloqueia sobreposicao com origem e repositorio.
Para recuperar um arquivo, consulte seus caminhos na opcao 8 e informe
o caminho interno na opcao 7. O filtro --include aceita padroes Restic;
revise a simulacao. Sem filtro, restaura o snapshot inteiro.
Links simbolicos e algumas permissoes podem exigir administrador no Windows.

CONFIGURACAO E SENHA
Configuracao e registro de operacoes: %LOCALAPPDATA%\ResticMenu
O registro guarda comando, horario e codigo de saida; a saida detalhada fica
na tela. A senha nao e salva em arquivo: fica na memoria desta sessao e e
passada ao processo Restic por variavel de ambiente. Feche o menu ao terminar.
O ID do repositorio e conferido antes de cada operacao para detectar outro
repositorio na mesma letra de unidade. Mudou a letra? Use a opcao 9 e vincule
novamente, conferindo o HD. Repositorio ausente nunca e recriado automaticamente.

AGENDAMENTO
Esta versao e interativa; nao a agende como tarefa silenciosa. Agendamento
sem supervisao requer um modo separado com credencial protegida, verificacao
do HD e registro de erros. Nenhuma tarefa e instalada por este script.

REFERENCIAS
[1] Backup: https://restic.readthedocs.io/en/stable/040_backup.html
[2] Repositorios: https://restic.readthedocs.io/en/stable/045_working_with_repos.html
[3] Restauracao: https://restic.readthedocs.io/en/stable/050_restore.html
[4] Inicializacao: https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html
'''

def overlaps(a, b):
    a, b = Path(a).resolve(), Path(b).resolve()
    return a == b or a in b.parents or b in a.parents

def yes(question):
    while True:
        answer = input(question + ' [s/N]: ').strip().lower()
        if answer in ('s', 'sim'):
            return True
        if answer in ('', 'n', 'nao', 'não'):
            return False
        print('Digite S para sim ou N para nao.')

def absolute(value):
    p = Path(value.strip().strip('"')).expanduser()
    if not p.is_absolute():
        raise ValueError('Informe um caminho absoluto, como C:\\Programas.')
    return str(p.resolve())

class Menu:
    def __init__(self):
        BASE.mkdir(parents=True, exist_ok=True)
        self.cfg = DEFAULT.copy()
        if CONFIG.exists():
            loaded = json.loads(CONFIG.read_text(encoding='utf-8'))
            if not isinstance(loaded, dict) or any(not isinstance(v, str) for k, v in loaded.items() if k in DEFAULT):
                raise ValueError(f'Configuracao invalida em {CONFIG}. Preserve o arquivo para revisao.')
            self.cfg.update({k: v for k, v in loaded.items() if k in DEFAULT})
        self.password = None
        self.exe = shutil.which('restic')
        if not self.exe:
            raise ValueError('Restic nao encontrado no PATH. Reabra o PowerShell apos instalar.')

    def save(self):
        temp = CONFIG.with_suffix('.tmp')
        temp.write_text(json.dumps(self.cfg, indent=2), encoding='utf-8')
        temp.replace(CONFIG)

    def run(self, args, capture=False):
        if self.password is None:
            self.password = getpass.getpass('Senha do repositorio (nao sera salva): ')
        env = {k: v for k, v in os.environ.items() if not k.startswith('RESTIC_')}
        env['RESTIC_PASSWORD'] = self.password
        cmd = [self.exe, '-r', self.cfg['repo']] + args
        log = BASE / 'operacoes.jsonl'
        def record(event, **extra):
            with log.open('a', encoding='utf-8') as f:
                f.write(json.dumps({'time': dt.datetime.now().isoformat(),
                                    'event': event, 'command': cmd, **extra}) + '\n')
        record('inicio')
        try:
            result = subprocess.run(cmd, env=env, shell=False,
                                    stdout=subprocess.PIPE if capture else None,
                                    encoding='utf-8', errors='replace')
        except KeyboardInterrupt:
            record('interrompido')
            raise
        record('fim', code=result.returncode)
        if result.returncode:
            self.password = None
            if args[0] == 'backup' and result.returncode == 3:
                raise ValueError('BACKUP INCOMPLETO: alguns arquivos nao puderam ser lidos. Veja os erros acima.')
            raise ValueError(f'Operacao falhou (codigo {result.returncode}). Veja a mensagem do Restic acima.')
        return result.stdout if capture else ''

    def repo_config(self):
        if not (Path(self.cfg['repo']) / 'config').is_file():
            raise ValueError('Repositorio ausente. Confira o HD e o caminho; use opcao 1 se necessario.')
        return json.loads(self.run(['cat', 'config'], capture=True))

    def guard(self):
        if not self.cfg['repo_id'] or not (Path(self.cfg['repo']) / 'config').is_file():
            print('\nAntes de continuar, vamos localizar o backup existente.')
            if not self.connect(existing_only=True):
                raise ValueError('Nenhuma operacao realizada. Voce pode tentar novamente pelo mesmo menu.')
        if self.repo_config()['id'] != self.cfg['repo_id']:
            raise ValueError('ID diferente! Operacao bloqueada. Confira o HD e o repositorio.')

    def connect(self, existing_only=False):
        print('\nLOCALIZAR O REPOSITORIO (pasta onde o Restic guarda os backups)')
        print('Exemplo: D:\\Restic-Programas. Nao informe a pasta que recebera a restauracao.')
        print('Vincular nao move nem restaura arquivos. Digite 0 para cancelar.')
        value = input(f'Caminho do repositorio [{self.cfg["repo"]}] (Enter mantem): ').strip()
        if value == '0':
            return False
        proposed = absolute(value or self.cfg['repo'])
        if proposed != self.cfg['repo']:
            self.password = None
            self.cfg['repo'], self.cfg['repo_id'] = proposed, ''
            self.save()
        repo = Path(absolute(self.cfg['repo']))
        if overlaps(repo, self.cfg['source']):
            raise ValueError('Origem e repositorio nao podem se sobrepor.')
        if not (repo / 'config').is_file():
            if existing_only:
                raise ValueError('Backup nao encontrado nesse caminho. Confira a letra do HD e escolha a pasta que contem o arquivo config do Restic. Nenhum repositorio novo foi criado.')
            if not repo.parent.is_dir():
                raise ValueError('Pasta pai indisponivel. Confira se o HD esta conectado.')
            if repo.exists() and (not repo.is_dir() or any(repo.iterdir())):
                raise ValueError('Destino ocupado; escolha uma pasta vazia para inicializar.')
            if input(f'Criar repositorio em {repo}? Digite CRIAR: ') != 'CRIAR':
                return False
            first = getpass.getpass('Nova senha: ')
            if not first or first != getpass.getpass('Repita a senha: '):
                raise ValueError('Senhas vazias ou diferentes.')
            self.password = first
            self.run(['init'])
        identity = self.repo_config()['id']
        print('Repositorio:', repo, '\nID:', identity)
        if self.cfg['repo_id'] and identity != self.cfg['repo_id']:
            raise ValueError('Este caminho agora contem outro repositorio. Confira o HD antes de alterar a configuracao pela opcao 9.')
        if input('Confirma que este e seu repositorio? Digite VINCULAR: ').strip().upper() == 'VINCULAR':
            self.cfg['repo_id'] = identity
            self.save()
            print('Repositorio vinculado.')
            return True
        return False

    def backup(self, dry, confirmed=False):
        self.guard()
        src = Path(self.cfg['source'])
        if not src.is_dir() or overlaps(src, self.cfg['repo']):
            raise ValueError('Origem ausente ou sobreposta ao repositorio.')
        args = ['backup', str(src), '--verbose']
        if self.cfg['exclude_file']:
            if not Path(self.cfg['exclude_file']).is_file():
                raise ValueError('Arquivo de exclusoes nao encontrado.')
            args += ['--exclude-file', self.cfg['exclude_file']]
        if dry:
            args += ['--dry-run']
        print('Origem:', src, '\nRepositorio:', self.cfg['repo'])
        print('Exclusoes:', self.cfg['exclude_file'] or 'nenhuma: inclui .git e arquivos ignorados pelo Git')
        if not dry and not confirmed and not yes('Salvar agora os arquivos desta maquina no repositorio?'):
            return
        self.run(args)
        print('Simulacao concluida.' if dry else 'Backup concluido sem erros reportados pelo Restic.')
        print('Proximo passo: 3 para gravar.' if dry else 'Proximo passo: 4 para consultar; 6 para verificar os dados; 7 para testar uma restauracao.')

    def snapshots(self):
        self.guard()
        items = json.loads(self.run(['snapshots', '--json'], capture=True)) or []
        items.sort(key=lambda x: x['time'], reverse=True)
        for n, s in enumerate(items, 1):
            when = dt.datetime.fromisoformat(s['time'].replace('Z', '+00:00')).astimezone().strftime('%d/%m/%Y %H:%M:%S %z')
            print(f"\n{n}. {when} | Computador: {s.get('hostname', '?')} | ID: {s['id'][:8]}")
            print('   Pastas salvas:', ', '.join(s.get('paths', [])))
        if not items:
            print('Nenhum snapshot encontrado.')
        return items

    def select(self):
        items = self.snapshots()
        if not items:
            return None
        print('\nMais recentes primeiro. Confira o COMPUTADOR: o numero 1 pode ser de outra maquina.')
        while True:
            value = input('Numero do snapshot (0 cancela): ').strip()
            if value == '0':
                return None
            if value.isdigit() and 1 <= int(value) <= len(items):
                n = int(value)
                break
            print('Digite um dos numeros exibidos.')
        print('Snapshot selecionado:', items[n-1]['id'][:8], '|', items[n-1].get('hostname'), '|', items[n-1]['time'])
        return items[n-1]['id']

    def restore(self):
        print('\nRESTAURAR - 1/4: escolha o backup salvo no repositorio.')
        print('A origem configurada nao sera lida. Voce escolhera o destino a seguir.')
        sid = self.select()
        if not sid:
            return
        print('\nRESTAURAR - 2/4: onde colocar os arquivos recuperados?')
        print('Exemplo: C:\\Programas_bkp. O repositorio permanece no HD.')
        value = input(f'Pasta de destino [{self.cfg["restore_parent"]}] (Enter aceita; 0 cancela): ').strip()
        if value == '0':
            return
        parent = Path(absolute(value or self.cfg['restore_parent']))
        target = parent / ('Restauracao_' + dt.datetime.now().strftime('%Y%m%d_%H%M%S') + '_' + uuid.uuid4().hex[:8])
        if overlaps(target, self.cfg['source']) or overlaps(target, self.cfg['repo']):
            raise ValueError('Restauracao sobreposta a origem ou ao repositorio.')
        if not parent.exists():
            if not yes(f'A pasta {parent} nao existe. Criar?'):
                return
            parent.mkdir(parents=True, exist_ok=False)
        if not parent.is_dir():
            raise ValueError('O destino precisa ser uma pasta.')
        self.cfg['restore_parent'] = str(parent)
        self.save()
        print('\nRESTAURAR - 3/4: quais arquivos?')
        print('Enter recupera tudo. Digite VER para consultar os caminhos antes de filtrar.')
        pattern = input('Caminho interno/filtro --include (Enter = tudo; veja opcao 8): ').strip()
        if pattern.upper() == 'VER':
            self.run(['ls', sid])
            pattern = input('Cole o caminho interno ou pressione Enter para tudo: ').strip()
        args = ['restore', sid, '--target', str(target), '--overwrite', 'never']
        if pattern:
            args += ['--include', pattern]
        print('\nRESTAURAR - 4/4: confira a simulacao.')
        print('Lendo de:', self.cfg['repo'], '\nGravacao prevista em:', target)
        print('A estrutura interna do snapshot sera preservada dentro dessa pasta.')
        self.run(args + ['--dry-run', '--verbose=2'])
        print('Destino novo:', target)
        if input('Revise a simulacao. Digite RESTAURAR para continuar (Enter cancela): ').strip().upper() != 'RESTAURAR':
            return
        target.mkdir(exist_ok=False)
        self.run(args + ['--verify'])
        print('Restauracao concluida e verificada em:', target)
        if os.name == 'nt' and yes('Abrir a pasta restaurada no Explorador?'):
            os.startfile(str(target))

    def configure(self):
        print('\nORIGEM: arquivos desta maquina para NOVOS backups. Nao e o destino do restore.')
        print('REPOSITORIO: backups criptografados que serao lidos ou gravados.')
        print('DESTINO DE RESTAURACAO: sugestao para receber arquivos; confirmado na opcao 7.')
        updated = self.cfg.copy()
        for key, label in [('source', 'Arquivos a salvar (origem)'), ('repo', 'Local dos backups (repositorio)'), ('restore_parent', 'Destino sugerido da restauracao')]:
            value = input(f'{label} [{updated[key]}] (Enter mantem): ').strip()
            if value:
                updated[key] = absolute(value)
        if overlaps(updated['source'], updated['repo']):
            raise ValueError('Origem e repositorio nao podem se sobrepor.')
        value = input('Arquivo de exclusoes: Enter mantem; - remove; ou caminho completo: ').strip()
        if value:
            updated['exclude_file'] = '' if value == '-' else absolute(value)
        if updated['repo'] != self.cfg['repo']:
            updated['repo_id'] = ''
            self.password = None
        self.cfg = updated
        self.save()
        print('Configuracao salva. Exclusoes:', self.cfg['exclude_file'] or 'nenhuma')

    def check(self, full):
        self.guard()
        self.run(['check'] + (['--read-data'] if full else []))
        print('Verificacao concluida sem erros nesta execucao.')
        print('Todos os dados foram lidos.' if full else 'Somente estrutura verificada. Para ler o conteudo armazenado, escolha 6.')

    def assistant(self):
        print('\nO QUE VOCE QUER FAZER AGORA?')
        print('1 Salvar arquivos desta maquina (backup guiado)')
        print('2 Recuperar arquivos de um backup existente (restauracao guiada)')
        print('0 Voltar')
        choice = input('Escolha: ').strip()
        if choice == '2':
            self.restore()
        elif choice == '1':
            print('\nBACKUP - 1/3: escolha os arquivos desta maquina.')
            value = input(f'Pasta a salvar [{self.cfg["source"]}] (Enter mantem): ').strip()
            src = absolute(value or self.cfg['source'])
            if not Path(src).is_dir():
                raise ValueError('A pasta de origem nao existe nesta maquina.')
            self.cfg['source'] = src
            self.save()
            print('\nBACKUP - 2/3: escolha onde guardar o backup.')
            if not self.connect():
                return
            print('\nBACKUP - 3/3: simulacao e gravacao.')
            self.backup(True)
            if yes('Simulacao concluida. Fazer o backup agora?'):
                self.backup(False, confirmed=True)
        elif choice != '0':
            print('Opcao invalida. Escolha A novamente para abrir o assistente.')

    def logs(self):
        print('Configuracao e registros:', BASE)
        print('Registro: operacoes.jsonl (inicio, fim e codigo de saida; detalhes na tela).')
        if os.name == 'nt' and yes('Abrir a pasta de registros?'):
            os.startfile(str(BASE))

    def browse(self):
        sid = self.select()
        if sid:
            self.run(['ls', sid])

    def menu(self):
        actions = {'1': self.connect, '2': lambda: self.backup(True),
                   '3': lambda: self.backup(False), '4': self.snapshots,
                   '5': lambda: self.check(False), '6': lambda: self.check(True),
                   '7': self.restore, '8': self.browse, '9': self.configure,
                   '10': lambda: print(HELP), '11': self.logs, 'a': self.assistant}
        while True:
            print('\nRESTIC BACKUP - MENU GUIADO')
            print('Arquivos a SALVAR (origem):', self.cfg['source'])
            print('Local dos BACKUPS (repositorio):', self.cfg['repo'])
            print('Destino sugerido para RECUPERAR:', self.cfg['restore_parent'])
            print('O destino sera confirmado ao restaurar. A pasta do script nao define estes caminhos.')
            available = (Path(self.cfg['repo']) / 'config').is_file()
            print('Estado:', 'vinculado; senha e ID conferidos ao operar' if available and self.cfg['repo_id'] else
                  'precisa localizar/vincular o repositorio; o assistente orientara voce')
            print('\nPRIMEIRA VEZ? A - Assistente passo a passo (backup ou restauracao)')
            print('\nSALVAR:       2 Simular backup | 3 Fazer backup')
            print('RECUPERAR:    7 Restaurar | 4 Listar snapshots | 8 Ver arquivos')
            print('VERIFICAR:    5 Estrutura (rapido) | 6 Todos os dados (completo)')
            print('CONFIGURAR:   1 Localizar/vincular/criar repositorio | 9 Caminhos e exclusoes')
            print('AJUDA:        10 Explicacoes e exemplos | 11 Registros | 0 Sair')
            try:
                choice = input('Opcao [A abre o assistente]: ').strip().lower() or 'a'
                if choice == '0':
                    self.password = None
                    return
                if choice not in actions:
                    print('Opcao invalida.')
                    continue
                actions[choice]()
            except (ValueError, OSError, KeyError) as exc:
                print('ATENCAO:', exc)
            except KeyboardInterrupt:
                print('\nOperacao interrompida. Confira a mensagem do Restic antes de tentar novamente.')
            input('\nEnter para voltar ao menu...')

if __name__ == '__main__':
    try:
        if '--help' in sys.argv:
            print(HELP)
        else:
            Menu().menu()
    except (ValueError, OSError) as exc:
        print('Erro:', exc)
        sys.exit(1)
    except (EOFError, KeyboardInterrupt):
        print('\nMenu encerrado.')
