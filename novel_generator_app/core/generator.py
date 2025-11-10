import threading
import time
import logging
import json
import os
import datetime
import random
import aiohttp
import asyncio

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('novel_generator')

# 全局变量
API_BASE_URL = "https://api.openai.com/v1/chat/completions"

class NovelGenerator:
    """小说生成器的简化版，适用于移动设备"""
    
    def __init__(self, api_key, model, **kwargs):
        """
        初始化小说生成器
        
        Args:
            api_key (str): OpenAI API密钥
            model (str): 使用的模型名称
            kwargs: 其他参数
        """
        self.api_key = api_key
        self.model = model
        self.novel_type = kwargs.get('novel_type', '玄幻小说')
        self.target_length = kwargs.get('target_length', 20000)
        self.auto_summary = kwargs.get('auto_summary', True)
        self.create_ending = kwargs.get('create_ending', False)
        
        # AI参数
        self.temperature = kwargs.get('temperature', 0.66)
        self.top_p = kwargs.get('top_p', 0.92)
        self.max_tokens = kwargs.get('max_tokens', 8000)
        
        # 状态变量
        self.is_running = False
        self.is_paused = False
        self.current_progress = 0
        self.current_content = ""
        self.current_length = 0
        
        # 输出目录
        self.output_dir = self._create_output_dir()
        
        logger.info(f"初始化生成器: 模型={model}, 小说类型={self.novel_type}, 目标字数={self.target_length}")
    
    def _create_output_dir(self):
        """创建输出目录"""
        timestamp = int(time.time())
        output_dir = f"novel_output_{timestamp}"
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"创建输出目录: {output_dir}")
        
        return output_dir
    
    def start_generation(self, callback=None, progress_callback=None):
        """
        开始生成小说
        
        Args:
            callback: 生成完成后的回调函数
            progress_callback: 进度更新回调函数
        """
        self.is_running = True
        self.current_progress = 0
        self.current_content = ""
        self.current_length = 0
        
        # 创建并启动生成线程
        thread = threading.Thread(
            target=self._generate_novel_thread,
            args=(callback, progress_callback),
            daemon=True
        )
        thread.start()
        
        logger.info("开始生成小说")
    
    def _generate_novel_thread(self, callback, progress_callback):
        """
        生成小说的线程函数
        
        Args:
            callback: 生成完成后的回调函数
            progress_callback: 进度更新回调函数
        """
        try:
            # 设置事件循环策略（Windows需要）
            if os.name == 'nt':
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            
            # 创建新的事件循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 运行异步生成函数
            loop.run_until_complete(
                self._generate_novel_async(progress_callback)
            )
            
            # 关闭事件循环
            loop.close()
            
            # 在完成时保存最终结果
            if self.is_running:  # 如果不是被中途停止的
                self._save_final_output()
                
                if callback:
                    callback()
            
        except Exception as e:
            logger.error(f"生成过程中出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
    
    async def _generate_novel_async(self, progress_callback):
        """
        异步生成小说
        
        Args:
            progress_callback: 进度更新回调函数
        """
        # 生成小说标题和大纲
        title, outline = await self._generate_title_and_outline()
        self.current_content = f"# {title}\n\n## 大纲\n\n{outline}\n\n## 正文\n\n"
        self.current_length = len(self.current_content)
        
        # 更新进度（使用临时变量避免线程问题）
        progress_data = {
            'progress': 5,
            'current_length': self.current_length,
            'target_length': self.target_length,
            'status': 'paused' if self.is_paused else 'generating',
            'content': self.current_content
        }
        if progress_callback:
            progress_callback(progress_data)
        
        # 逐章节生成内容
        chapter_count = random.randint(5, 10)  # 随机章节数
        for i in range(1, chapter_count + 1):
            if not self.is_running:
                break
                
            # 生成章节
            chapter_title, chapter_content = await self._generate_chapter(i, outline)
            
            # 添加到当前内容
            self.current_content += f"\n### 第{i}章 {chapter_title}\n\n{chapter_content}\n\n"
            self.current_length = len(self.current_content)
            
            # 保存当前进度
            self._save_progress()
            
            # 更新进度（使用临时变量避免线程问题）
            progress = int(5 + (i / chapter_count) * 90)
            progress_data = {
                'progress': progress,
                'current_length': self.current_length,
                'target_length': self.target_length,
                'status': 'paused' if self.is_paused else 'generating',
                'content': self.current_content
            }
            if progress_callback:
                progress_callback(progress_data)
            
            # 暂停检查
            while self.is_paused and self.is_running:
                await asyncio.sleep(0.5)
        
        # 生成结局
        if self.create_ending and self.is_running:
            ending = await self._generate_ending(title, outline, self.current_content)
            self.current_content += f"\n## 结局\n\n{ending}\n"
            self.current_length = len(self.current_content)
            
            # 更新进度（使用临时变量避免线程问题）
            progress_data = {
                'progress': 100,
                'current_length': self.current_length,
                'target_length': self.target_length,
                'status': 'paused' if self.is_paused else 'generating',
                'content': self.current_content
            }
            if progress_callback:
                progress_callback(progress_data)
    
    async def _generate_title_and_outline(self):
        """
        生成小说标题和大纲
        
        Returns:
            tuple: (标题, 大纲)
        """
        prompt = f"请为一部{self.novel_type}创作一个吸引人的标题和详细的故事大纲。标题应该简洁有力，大纲应该包括主要人物、故事背景和主要情节发展。"
        
        response = await self._call_openai_api(prompt)
        
        try:
            # 简单解析返回的内容，提取标题和大纲
            text = response.strip()
            lines = text.split('\n')
            
            title = lines[0].strip()
            if title.startswith('标题:') or title.startswith('标题：'):
                title = title[3:].strip()
            
            outline = '\n'.join(lines[1:]).strip()
            
            return title, outline
        except Exception as e:
            logger.error(f"解析标题和大纲时出错: {str(e)}")
            return "未命名小说", "无大纲"
    
    async def _generate_chapter(self, chapter_number, outline):
        """
        生成一个章节
        
        Args:
            chapter_number (int): 章节编号
            outline (str): 小说大纲
            
        Returns:
            tuple: (章节标题, 章节内容)
        """
        prompt = (
            f"基于以下大纲，为{self.novel_type}创作第{chapter_number}章的内容。\n\n"
            f"大纲：{outline}\n\n"
            f"请首先创作一个吸引人的章节标题，然后是章节正文。"
            f"章节内容应该围绕大纲发展，但可以添加细节和对话。"
        )
        
        response = await self._call_openai_api(prompt)
        
        try:
            # 简单解析返回的内容，提取标题和内容
            text = response.strip()
            lines = text.split('\n')
            
            chapter_title = lines[0].strip()
            if chapter_title.startswith('第') and '章' in chapter_title:
                # 删除可能存在的"第X章"前缀
                chapter_title = chapter_title.split('章', 1)[1].strip()
            elif chapter_title.startswith('标题:') or chapter_title.startswith('标题：'):
                chapter_title = chapter_title[3:].strip()
            
            chapter_content = '\n'.join(lines[1:]).strip()
            
            return chapter_title, chapter_content
        except Exception as e:
            logger.error(f"解析章节时出错: {str(e)}")
            return f"第{chapter_number}章", "章节内容生成失败"
    
    async def _generate_ending(self, title, outline, current_content=""):
        """
        生成小说结局
        
        Args:
            title (str): 小说标题
            outline (str): 小说大纲
            current_content (str): 当前已生成的小说内容
            
        Returns:
            str: 结局内容
        """
        prompt = (
            f"为标题为《{title}》的{self.novel_type}创作一个引人入胜的结局。\n\n"
            f"大纲：{outline}\n\n"
        )
        
        # 如果有已生成的内容，添加到提示词中作为上下文
        if current_content:
            # 截取最后部分内容作为上下文（避免超过token限制）
            context_limit = 8000  # 大约8000字符的上下文
            if len(current_content) > context_limit:
                # 从最后部分开始，找到完整段落
                truncated_content = current_content[-context_limit:]
                first_paragraph_start = truncated_content.find('\n\n')
                if first_paragraph_start != -1:
                    truncated_content = truncated_content[first_paragraph_start + 2:]
                prompt += f"已有内容（最近部分）：\n{truncated_content}\n\n"
            else:
                prompt += f"已有内容：\n{current_content}\n\n"
        
        prompt += f"基于以上大纲和已有内容，创作一个令人满意的结局，收束所有主要情节线和人物弧光，对故事中的主要人物命运做出交代。"
        
        response = await self._call_openai_api(prompt)
        return response.strip()
    
    async def _call_openai_api(self, prompt):
        """
        调用OpenAI API
        
        Args:
            prompt (str): 提示内容
            
        Returns:
            str: 返回的内容
        """
        # 在暂停时等待
        while self.is_paused and self.is_running:
            await asyncio.sleep(0.5)
            
        if not self.is_running:
            return ""
            
        try:
            # 构建请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "top_p": self.top_p,
                "max_tokens": self.max_tokens
            }
            
            # 发送请求到新的API服务
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    API_BASE_URL,
                    headers=headers,
                    json=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"API调用失败: {response.status} - {error_text}")
                        return f"API调用失败: {response.status}"
        except Exception as e:
            logger.error(f"调用API时出错: {str(e)}")
            return f"生成错误: {str(e)}"
    
    def _update_progress(self, progress, progress_callback):
        """
        更新进度
        
        Args:
            progress (int): 当前进度（0-100）
            progress_callback: 进度回调函数
        """
        self.current_progress = progress
        
        if progress_callback:
            progress_callback({
                'progress': progress,
                'current_length': self.current_length,
                'target_length': self.target_length,
                'status': 'paused' if self.is_paused else 'generating'
            })
    
    def _save_progress(self):
        """保存当前进度"""
        if not self.is_running:
            return
            
        try:
            # 保存当前内容到文件
            output_file = os.path.join(self.output_dir, "novel_in_progress.md")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(self.current_content)
                
            logger.info(f"已保存进度: {len(self.current_content)}字")
        except Exception as e:
            logger.error(f"保存进度时出错: {str(e)}")
    
    def _save_final_output(self):
        """保存最终输出"""
        try:
            # 提取标题
            lines = self.current_content.split('\n')
            title = lines[0].strip()
            if title.startswith('#'):
                title = title[1:].strip()
            
            # 保存Markdown文件
            output_file = os.path.join(self.output_dir, f"{title}.md")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(self.current_content)
            
            # 保存简单的JSON元数据
            metadata = {
                "title": title,
                "type": self.novel_type,
                "length": len(self.current_content),
                "model": self.model,
                "date_generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            metadata_file = os.path.join(self.output_dir, "metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=4)
                
            logger.info(f"已保存最终输出: {output_file}")
        except Exception as e:
            logger.error(f"保存最终输出时出错: {str(e)}")
    
    def stop_generation(self):
        """停止生成"""
        self.is_running = False
        logger.info("生成已停止")
    
    def pause_generation(self):
        """暂停生成"""
        self.is_paused = True
        logger.info("生成已暂停")
    
    def resume_generation(self):
        """继续生成"""
        self.is_paused = False
        logger.info("生成已继续")
    
    def get_current_content(self):
        """获取当前内容"""
        return self.current_content 