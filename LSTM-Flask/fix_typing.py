"""
修复 Python 3.9.0 typing.py 模块的 TensorFlow 兼容性问题
"""
import os
import sys
import shutil

typing_path = os.path.join(sys.prefix, 'lib', 'typing.py')
backup_path = typing_path + '.backup'

print(f"Python 路径: {sys.prefix}")
print(f"typing.py 位置: {typing_path}")

# 备份原文件
if not os.path.exists(backup_path):
    shutil.copy2(typing_path, backup_path)
    print(f"✓ 已备份到: {backup_path}")
else:
    print(f"✓ 备份已存在: {backup_path}")

# 读取文件
with open(typing_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找并替换有问题的代码
old_code = """def _remove_dups_flatten(parameters):
    \"\"\"Internal helper for Union creation and substitution: flatten Unions
    among parameters, then remove duplicates and strict subclasses.
    \"\"\"
    # Flatten out Union[Union[...], ...].
    params = []
    for p in parameters:
        if isinstance(p, _UnionGenericAlias):
            params.extend(p.__args__)
        elif isinstance(p, tuple) and len(p) > 0 and p[0] is Union:
            params.extend(p[1:])
        else:
            params.append(p)
    # Weed out strict duplicates, preserving the first of each occurrence.
    all_params = set(params)"""

new_code = """def _remove_dups_flatten(parameters):
    \"\"\"Internal helper for Union creation and substitution: flatten Unions
    among parameters, then remove duplicates and strict subclasses.
    \"\"\"
    # Flatten out Union[Union[...], ...].
    params = []
    for p in parameters:
        if isinstance(p, _UnionGenericAlias):
            params.extend(p.__args__)
        elif isinstance(p, tuple) and len(p) > 0 and p[0] is Union:
            params.extend(p[1:])
        else:
            params.append(p)
    # Weed out strict duplicates, preserving the first of each occurrence.
    # 修复: 使用 tuple 转换来避免 unhashable type 错误
    all_params = set()
    for p in params:
        try:
            all_params.add(p)
        except TypeError:
            # 如果参数不可哈希(如list),将其转换为tuple
            if isinstance(p, list):
                all_params.add(tuple(p))
            else:
                all_params.add(p)"""

if old_code in content:
    content = content.replace(old_code, new_code)
    
    # 写回文件
    with open(typing_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✓ 修复成功!")
    print("  已修改 _remove_dups_flatten 函数以兼容 TensorFlow")
    print("\n如需恢复原文件,运行:")
    print(f"  copy {backup_path} {typing_path}")
else:
    print("\n⚠ 未找到需要修复的代码模式")
    print("  可能:")
    print("  1. 文件已被修改")
    print("  2. Python 版本不匹配")
    print("  3. 已经修复过")
