# file, directoryのパス取得用関数
import re
import os

# 指定したディレクトリの下流のすべてのディレクトリのパスを取得
# 下る階層数を指定することも可能
def getAllSubDirectories(path, depth=None):
    dirs_sub = [dirpath.replace("\\", "/") for dirpath, dirnames, filenames in os.walk(path)] # \\ -> /
    if type(depth) == int:
        sep_num = len(path.rsplit("/")) # 基準となるフォルダの階層数
        sep_thresh = sep_num + depth
        dirs_sub = [dirpath for dirpath in dirs_sub if len(dirpath.rsplit("/")) <= sep_thresh]
    return dirs_sub

# 指定したディレクトリの下流のすべてのファイルのパスを取得
def getAllSubFiles(path, depth=None):
    paths_sub = []
    sep_num = len(path.rsplit("/")) # 基準となるフォルダの階層数
    for root, dirs, files in os.walk(path):
        for file in files:
            path = os.path.join(root, file).replace("\\", "/")
            if type(depth) == int:
                sep_thresh = sep_num + depth
                if len(path.rsplit("/")) <= sep_thresh:
                    paths_sub.append(path)
            else:
                paths_sub.append(path)
    return paths_sub

# 指定したフォルダのサブディレクトリリストから正規表現を用いてプロジェクトディレクトリのみを選択
def getProjectDirectories(path, depth=None):
    dirs_sub = getAllSubDirectories(path, depth)
    dirs_project = []
    for dir_sub in dirs_sub:
        # パスを分割
        dir_split = dir_sub.split("/")[-4:]
        if len(dir_split) != 4:
            continue
        dir1, dir2, dir3, dir4 = dir_split
        # 条件を確認 database, database_MultiMod, 230224, IM07,
        if re.match("^\d{6}$", dir4) and re.match("^[a-zA-Z]{2}\d{2}$", dir3) and dir2.startswith("database_") and dir1=="database":
            dirs_project.append(dir_sub)
    return dirs_project

# リストのすべての文字列を含む(and)、あるいは1つでも含む(or)パスのみを選択
# 除外検索も可能
# case_sensitive=Trueで大文字小文字を区別する
# 拡張子が .nd2 のファイルを取得するパターン
# list_str_include = [r"\.nd2$"]
def getMatchedPaths(list_path, list_str_include=None, list_str_exclude=None, match_include="and", match_exclude="or", case_sensitive=True):
    if list_str_include is None:
        list_str_include = []
    if list_str_exclude is None:
        list_str_exclude = []

    # case_sensitiveがTrueの場合、大文字小文字を区別する
    re_flags = 0 if case_sensitive else re.IGNORECASE
    list_str_include = [re.compile(s, re_flags) for s in list_str_include]
    list_str_exclude = [re.compile(s, re_flags) for s in list_str_exclude]

    list_match_path = []
    for path in list_path:
        # case_sensitiveがFalseの場合のみ、パスを小文字に変換
        path_lower = path.lower() if not case_sensitive else path

        if match_include == "and":
            include_condition = all(pattern.search(path_lower) for pattern in list_str_include) if list_str_include else True
        elif match_include == "or":
            include_condition = any(pattern.search(path_lower) for pattern in list_str_include) if list_str_include else False

        if match_exclude == "and":
            exclude_condition = all(pattern.search(path_lower) for pattern in list_str_exclude) if list_str_exclude else False
        elif match_exclude == "or":
            exclude_condition = any(pattern.search(path_lower) for pattern in list_str_exclude) if list_str_exclude else False

        if include_condition and not exclude_condition:
            list_match_path.append(path)

    return list_match_path