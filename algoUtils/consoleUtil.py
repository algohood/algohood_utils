from typing import Callable, List, Optional, Dict
from langchain_core.messages import HumanMessage, AnyMessage
import re

class ConsoleOutput:
    @classmethod
    def console_for_stream(cls, _source_name: str, _msg_generator: Callable, _llm_msg: Optional[List[AnyMessage]]=None):
        content = ""
        print('----------------{}----------------'.format(_source_name))
        print()

        if _llm_msg:
            print('--------llm msg--------')
            for msg in _llm_msg:
                print('{}: {}'.format(msg.name, msg.content))
            print()
        print()

        for chunk in _msg_generator:
            if chunk.content:
                for char in chunk.content:
                    content += char
                    print(char, end='', flush=True)
        print()
        return content

    @classmethod
    def console_for_input(cls, _source_name: str, _invoke_str: str):
        print('----------------{}----------------'.format(_source_name))
        print()
        msg = input(_invoke_str)
        print()
        return HumanMessage(content=msg, name='user')

    @staticmethod
    def extract_python_scripts(content: str) -> str:
        """
        提取Python脚本内容（支持嵌套代码块解析）
        返回第一个匹配的脚本内容字符串
        """
        # 匹配python代码块（支持带文件名版本号模式）
        pattern = re.compile(r'```python:\s*"?(?P<filename>[^"\n]+?_V\d+\.py)"?(?=\s|:|$)')
        
        pos = 0
        while pos < len(content):
            match = pattern.search(content, pos)
            if not match:
                break
            
            filename = match.group('filename').strip()
            content_start = match.end()
            
            # 嵌套代码块处理逻辑
            depth = 1
            content_end = content_start
            last_valid_end = content_start
            
            while depth > 0 and content_end < len(content):
                next_triple = content.find('```', content_end)
                if next_triple == -1:
                    break
                
                # 判断是代码块开始还是结束
                line_end = content.find('\n', next_triple + 3)
                if line_end == -1:
                    line_end = len(content)
                    
                # 检查是否包含语言标识
                has_lang = False
                lang_part = content[next_triple+3 : line_end].strip()
                if lang_part:
                    if ':' in lang_part:
                        has_lang = True
                    else:
                        has_lang = not lang_part.startswith((' ', '\t', '\n', '\r'))
                
                if has_lang:
                    depth += 1
                    content_end = next_triple + 3
                else:
                    depth -= 1
                    last_valid_end = next_triple  # 记录有效结束位置
                    content_end = next_triple + 3

            if depth == 0:
                # 提取原始内容（保留嵌套结构）
                raw_content = content[content_start:last_valid_end]
                
                # 统一缩进处理
                lines = []
                min_indent = float('inf')
                
                # 计算最小缩进（跳过空行）
                for line in raw_content.split('\n'):
                    stripped = line.lstrip()
                    if stripped:
                        indent = len(line) - len(stripped)
                        min_indent = min(min_indent, indent)
                
                # 应用缩进清理
                for line in raw_content.split('\n'):
                    if line.strip():
                        adjusted_line = line[min_indent:] if min_indent != float('inf') else line
                        lines.append(adjusted_line.rstrip())  # 移除行尾空白
                    else:
                        lines.append('')  # 保留空行
                        
                cleaned_content = '\n'.join(lines).strip()
                
                if cleaned_content:
                    return cleaned_content  # 直接返回第一个有效脚本内容
                    
                pos = content_end
            else:
                pos = last_valid_end
        
        return ""  # 没有找到时返回空字符串

    @staticmethod
    def extract_markdown_files(content: str) -> Dict[str, str]:
        """
        改进版：修复嵌套代码块解析问题
        """
        md_files = {}
        # 严格匹配md:前缀的代码块
        pattern = re.compile(r'```md:\s*"?(?P<filename>[^"\n]+?_V\d+\.md)"?(?=\s|:|$)')
        
        pos = 0
        while pos < len(content):
            match = pattern.search(content, pos)
            if not match:
                break
                
            filename = match.group('filename').strip()
            content_start = match.end()
            
            # 改进的嵌套解析逻辑
            depth = 1
            content_end = content_start
            last_valid_end = content_start
            
            while depth > 0 and content_end < len(content):
                next_triple = content.find('```', content_end)
                if next_triple == -1:
                    break
                
                # 判断是代码块开始还是结束
                line_end = content.find('\n', next_triple + 3)
                if line_end == -1:
                    line_end = len(content)
                    
                # 检查```后的内容是否包含语言标识
                has_lang = False
                lang_part = content[next_triple+3 : line_end].strip()
                if lang_part:
                    if ':' in lang_part:
                        has_lang = True
                    else:
                        # 简单语言标识（如math）
                        has_lang = not lang_part.startswith((' ', '\t', '\n', '\r'))
                
                if has_lang:
                    depth += 1
                    # 移动到下一个```之后
                    content_end = next_triple + 3
                else:
                    depth -= 1
                    last_valid_end = next_triple  # 记录有效结束位置
                    content_end = next_triple + 3  # 移动到结束```之后

            if depth == 0:
                # 提取原始内容（包含所有嵌套结构）
                raw_content = content[content_start:last_valid_end]
                
                # 改进的缩进处理
                lines = []
                min_indent = float('inf')
                
                # 计算最小缩进（跳过空行）
                for line in raw_content.split('\n'):
                    stripped = line.lstrip()
                    if stripped:
                        indent = len(line) - len(stripped)
                        min_indent = min(min_indent, indent)
                
                # 应用缩进清理（保留空行原样）
                for line in raw_content.split('\n'):
                    if line.strip():
                        adjusted_line = line[min_indent:] if min_indent != float('inf') else line
                        lines.append(adjusted_line.rstrip())  # 移除行尾空白
                    else:
                        lines.append('')  # 保留空行
                        
                cleaned_content = '\n'.join(lines).strip()
                
                if filename and cleaned_content:
                    md_files[filename] = cleaned_content
                    
                pos = content_end
            else:
                pos = last_valid_end  # 跳过未闭合部分
                
        return md_files
