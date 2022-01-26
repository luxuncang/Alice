import inspect
import requests
from typing import Callable, Iterable
from github import Github

from ...internaltype import config

class GithubParse:
    g = Github(config['Github']['token'])

    @classmethod
    def get_user(cls, username, obj: bool = False):
        try:
            u = cls.g.get_user(username)
            if obj:
                return u
            res = f'''
                姓名: {u.name}
                邮箱: {u.email}
                简介: {u.bio}
                链接: {u.html_url}
                关注: {u.following}
                粉丝: {u.followers}
                创建: {u.created_at}
                更新: {u.updated_at}
                仓库: {' '.join([i.name for i in u.get_repos(type='owner')])}
                头像: {u.avatar_url}
                贡献: {u.contributions}
            '''
            return '\n'.join([i.strip() for i in res.splitlines()])
        except Exception as e:
            print(e)
            return f'用户 {username} 不存在'

    @classmethod
    def get_repo(cls, repo, obj: bool = False):
        try:
            r = cls.g.get_repo(repo)
            if obj:
                return r
            res = f'''
                仓库名: {r.name}
                所有者: {r.owner.login}
                仓库描述: {r.description}
                仓库链接: {r.html_url}
                仓库创建: {r.created_at}
                仓库更新: {r.updated_at}
                仓库语言: {r.language}
                仓库大小: {r.size}
                仓库Star: {r.stargazers_count}
                仓库Watch: {r.watchers_count}
                仓库Fork: {r.forks_count}
                仓库issue: {r.open_issues_count}
            '''
            return '\n'.join([i.strip() for i in res.splitlines()])
        except Exception as e:
            return f'仓库 {repo} 不存在'

    @classmethod
    def get_organization(cls, name, obj: bool = False):
        try:
            org = cls.g.get_organization(name)
            if obj:
                return org
            res = f'''
                组织名: {org.login}
                组织描述: {org.description}
                组织链接: {org.html_url}
                组织创建: {org.created_at}
                组织更新: {org.updated_at}
                组织成员: {' '.join([i.login for i in org.get_members()][::-1])}
                组织仓库: {' '.join([i.name for i in org.get_repos()])}
            '''
            return '\n'.join([i.strip() for i in res.splitlines()])
        except:
            return f'组织 {name} 不存在'

    @classmethod
    def get_doc(cls, obj, obj_name: bool = False):
        funclist = [i for i in dir(obj) if not i.startswith('_')]
        if obj_name:
            return funclist
        return '\n'.join([f"命令: {i}\n文档: {inspect.getdoc(getattr(obj, i))}\n" for i in funclist])

    @classmethod
    def user(cls, parse: list):
        if parse[0] in ('-h', '-help'):
            return {'Plain': cls.get_doc(cls.g.get_user('luxuncang'), obj_name=True)}
        elif len(parse) == 1:
            return {'Plain': cls.get_user(parse[0])}
        elif len(parse) >= 3 and parse[1] == '-f':
            u = cls.g.get_user(parse[0])
            if isinstance(u, str):
                return {'Plain': u}
            res = getattr(u, parse[2])
            return cls.res_text(res, parse[3:], u)
        return {'Plain': '命令解析错误!'}

    @classmethod
    def org(cls, parse: list):
        if parse[0] in ('-h', '-help'):
            return {'Plain': cls.get_doc(cls.g.get_organization('GraiaProject'), obj_name=True)}
        elif len(parse) == 1:
            return {'Plain': cls.get_organization(parse[0])}
        elif len(parse) >= 3 and parse[1] == '-f':
            u = cls.g.get_organization(parse[0])
            if isinstance(u, str):
                return {'Plain': u}
            res = getattr(u, parse[2])
            return cls.res_text(res, parse[3:], u)
        return {'Plain': '命令解析错误!'}

    @classmethod
    def repo(cls, parse: list):
        if parse[0] in ('-h', '-help'):
            return {'Plain': cls.get_doc(cls.g.get_repo('luxuncang/lupro'), obj_name=True)}
        elif len(parse) == 1:
            return {'Plain': cls.get_repo(parse[0])}
        elif len(parse) >= 3 and parse[1] == '-f':
            u = cls.g.get_repo(parse[0])
            if isinstance(u, str):
                return {'Plain': u}
            res = getattr(u, parse[2])
            return cls.res_text(res, parse[3:], u)

    @staticmethod
    def res_text(res, parse, obj):
        if isinstance(res, Callable):
            if len(parse) == 0:
                if res.__name__ == 'get_contents':
                    res = res("")
                else:
                    res = res()
            else:
                if res.__name__ == 'get_archive_link' and parse[0] == '-D':
                    url = res("zipball")
                    return {'file': (requests.get(url).content, f'{obj.name}.zip'), 'Plain': f'上传中...'}
                res = res(*parse)
        if isinstance(res, str):
            return {'Plain': '\n'.join([i.strip() for i in res.splitlines()])}
        elif isinstance(res, Iterable):
            return {'Plain': '\n'.join([f'{repr(i)}' for i in res])}
        print(res)
        return {'Plain': repr(res)}

    @classmethod
    def parse_action(cls, parse: str):
        parse = parse.split()
        if parse[0] == 'user':
            return cls.user(parse[1:])
        elif parse[0] == 'org':
            return cls.org(parse[1:])
        elif parse[0] == 'repo':
            return cls.repo(parse[1:])
        elif parse[0] == 'commit':
            return cls.commit(parse[1:])
        elif parse[0] == 'issue':
            return cls.issue(parse[1:])
        return '命令解析错误!'
