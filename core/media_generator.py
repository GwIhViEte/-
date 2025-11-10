import http.client
import json
import time
import os
import urllib.request
from typing import Dict, Any, List, Optional


class MediaGenerator:
    """媒体生成器：处理封面图片和音乐生成"""
    
    def __init__(self, api_key: str, status_callback=None):
        self.api_key = api_key
        "api.openai.com"
        self.status_callback = status_callback
        
    def update_status(self, message: str):
        """更新状态信息"""
        if self.status_callback:
            self.status_callback(message)
        else:
            print(message)
    
    def generate_cover_images(self, novel_setup: Dict[str, Any], num_images: int = 1) -> List[Dict[str, Any]]:
        """
        生成封面图片
        
        Args:
            novel_setup: 小说设置信息
            num_images: 生成图片数量
            
        Returns:
            List[Dict[str, Any]]: 生成的图片结果列表
        """
        try:
            # 根据小说信息生成封面提示词
            prompt = self._generate_cover_prompt(novel_setup)
            self.update_status(f"正在生成封面图片，提示词：{prompt}")
            
            image_results = []
            
            for i in range(num_images):
                self.update_status(f"正在生成第 {i+1}/{num_images} 张封面图片...")
                
                # 调用MidJourney API生成图片
                conn = http.client.HTTPSConnection(self.base_url)
                payload = json.dumps({
                    "prompt": prompt,
                    "base64": False
                })
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                try:
                    conn.request("POST", "/mj/submit/imagine", payload, headers)
                    res = conn.getresponse()
                    data = res.read()
                    response = json.loads(data.decode("utf-8"))
                    conn.close()
                    
                    self.update_status(f"MidJourney API响应: {response}")
                    
                    # 修正API响应判断逻辑：MidJourney返回code=1表示成功
                    if response.get("code") == 1 and response.get("result"):
                        task_id = response["result"]
                        self.update_status(f"封面图片 {i+1} 任务提交成功，任务ID: {task_id}")
                        
                        # 等待任务完成（10分钟）
                        result = self.wait_for_image_completion(task_id, timeout=600)  # 10分钟
                        if result:
                            image_results.append(result)
                            self.update_status(f"封面图片 {i+1} 生成成功")
                        else:
                            self.update_status(f"封面图片 {i+1} 等待超时，请稍后手动查询任务状态 (任务ID: {task_id})")
                    else:
                        error_msg = response.get("description", response.get("error", "API调用失败"))
                        self.update_status(f"封面图片 {i+1} 生成失败：{error_msg}")
                        
                except Exception as e:
                    self.update_status(f"封面图片 {i+1} 生成失败：{str(e)}")
                    continue
                    
            return image_results
            
        except Exception as e:
            self.update_status(f"生成封面图片时出错: {str(e)}")
            return []
    
    def generate_music(self, novel_setup: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        生成音乐
        
        Args:
            novel_setup: 小说设置信息
            
        Returns:
            Optional[Dict[str, Any]]: 生成的音乐结果
        """
        try:
            # 根据小说信息生成音乐提示词
            prompt = self._generate_music_prompt(novel_setup)
            self.update_status(f"正在生成音乐，提示词：{prompt}")
            
            # 调用Suno API生成音乐
            conn = http.client.HTTPSConnection(self.base_url)
            payload = json.dumps({
                "prompt": prompt,
                "make_instrumental": False,
                "wait_audio": False
            })
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            conn.request("POST", "/suno/submit/music", payload, headers)
            res = conn.getresponse()
            data = res.read()
            response = json.loads(data.decode("utf-8"))
            conn.close()
            
            self.update_status(f"Suno API响应: {response}")
            
            # 修正API响应判断逻辑：Suno返回code='success'表示成功，任务ID在data字段
            if response.get("code") == "success" and response.get("data"):
                task_id = response["data"]  # Suno直接返回任务ID字符串
                self.update_status(f"音乐任务提交成功，任务ID: {task_id}")
                
                # 等待任务完成（10分钟）
                result = self.wait_for_music_completion(task_id, timeout=600)  # 10分钟
                if result:
                    self.update_status("音乐生成成功")
                    return result
                else:
                    self.update_status(f"音乐等待超时，请稍后手动查询任务状态 (任务ID: {task_id})")
                    return None
            else:
                error_msg = response.get("message", response.get("error", "API调用失败"))
                self.update_status(f"音乐生成失败：{error_msg}")
                return None
                
        except Exception as e:
            self.update_status(f"生成音乐时出错: {str(e)}")
            return None
    
    def wait_for_image_completion(self, task_id: str, timeout: int = 600) -> Optional[Dict[str, Any]]:
        """
        等待图片生成完成
        
        Args:
            task_id: 任务ID
            timeout: 超时时间（秒）
            
        Returns:
            Optional[Dict[str, Any]]: 完成的任务结果
        """
        start_time = time.time()
        check_interval = 10  # 每10秒检查一次
        
        self.update_status(f"等待图片任务完成: {task_id}，最长等待10分钟")
        
        while time.time() - start_time < timeout:
            try:
                # 使用批量查询接口检查任务状态
                conn = http.client.HTTPSConnection(self.base_url)
                payload = json.dumps({
                    "ids": [task_id]
                })
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                conn.request("POST", "/mj/task/list-by-condition", payload, headers)
                res = conn.getresponse()
                data = res.read()
                response = json.loads(data.decode("utf-8"))
                conn.close()
                
                # 修正响应解析：根据API文档，返回的是任务列表
                task_info = None
                if isinstance(response, list) and len(response) > 0:
                    task_info = response[0]
                elif isinstance(response, dict) and "data" in response:
                    # 如果返回格式是 {"data": [...]}
                    data_list = response.get("data", [])
                    if isinstance(data_list, list) and len(data_list) > 0:
                        task_info = data_list[0]
                
                if task_info:
                    status = task_info.get("status")
                    progress = task_info.get("progress", "0%")
                    elapsed_time = int(time.time() - start_time)
                    remaining_time = timeout - elapsed_time
                    
                    self.update_status(f"图片任务进度: {progress}, 状态: {status}, 已等待: {elapsed_time}秒, 剩余: {remaining_time}秒")
                    
                    if status == "SUCCESS":
                        self.update_status(f"图片任务 {task_id} 完成！耗时: {elapsed_time}秒")
                        # 自动下载图片
                        downloaded_path = self.download_image(task_info)
                        if downloaded_path:
                            self.update_status(f"图片下载成功: {downloaded_path}")
                            task_info["local_path"] = downloaded_path
                        return task_info
                    elif status == "FAILURE":
                        failure_reason = task_info.get("failReason", "未知原因")
                        self.update_status(f"图片任务 {task_id} 失败: {failure_reason}")
                        return None
                    elif status in ["IN_PROGRESS", "SUBMITTED"]:
                        # 任务还在进行中，继续等待
                        pass
                    else:
                        self.update_status(f"图片任务状态未知: {status}")
                else:
                    self.update_status(f"图片任务查询响应格式异常: {response}")
                
            except Exception as e:
                self.update_status(f"检查图片任务状态时出错: {str(e)}")
            
            # 等待一段时间再检查
            time.sleep(check_interval)
        
        self.update_status(f"图片任务 {task_id} 超时")
        return None
    
    def wait_for_music_completion(self, task_id: str, timeout: int = 600) -> Optional[Dict[str, Any]]:
        """
        等待音乐生成完成
        
        Args:
            task_id: 任务ID
            timeout: 超时时间（秒）
            
        Returns:
            Optional[Dict[str, Any]]: 完成的任务结果
        """
        start_time = time.time()
        check_interval = 10  # 每10秒检查一次
        
        self.update_status(f"等待音乐任务完成: {task_id}，最长等待10分钟")
        
        while time.time() - start_time < timeout:
            try:
                # 使用单个任务查询接口
                conn = http.client.HTTPSConnection(self.base_url)
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'Authorization': f'Bearer {self.api_key}'
                }
                
                conn.request("GET", f"/suno/fetch/{task_id}", "", headers)
                res = conn.getresponse()
                data = res.read()
                response = json.loads(data.decode("utf-8"))
                conn.close()
                
                # 解析音乐任务响应
                if response.get("code") == "success" and response.get("data"):
                    task_data = response["data"]
                    
                    # 添加调试信息
                    self.update_status(f"音乐API响应数据类型: {type(task_data)}, 内容: {str(task_data)[:200]}...")
                    
                    # 如果data是字符串，说明任务还在处理中
                    if isinstance(task_data, str):
                        elapsed_time = int(time.time() - start_time)
                        remaining_time = timeout - elapsed_time
                        self.update_status(f"音乐任务进度: 处理中, 状态: IN_PROGRESS, 已等待: {elapsed_time}秒, 剩余: {remaining_time}秒")
                    elif isinstance(task_data, dict):
                        # 如果data是字典，说明任务完成
                        status = task_data.get("status", "UNKNOWN")
                        elapsed_time = int(time.time() - start_time)
                        remaining_time = timeout - elapsed_time
                        
                        self.update_status(f"音乐任务进度: 100%, 状态: {status}, 已等待: {elapsed_time}秒, 剩余: {remaining_time}秒")
                        
                        # 检查是否有data数组包含音乐链接
                        data_array = task_data.get("data", [])
                        has_audio_url = False
                        audio_url = None
                        
                        if isinstance(data_array, list) and len(data_array) > 0:
                            # 检查第一个音乐文件
                            first_music = data_array[0]
                            if isinstance(first_music, dict) and "audio_url" in first_music:
                                has_audio_url = True
                                audio_url = first_music["audio_url"]
                        
                        self.update_status(f"任务数据包含audio_url: {has_audio_url}")
                        if has_audio_url:
                            self.update_status(f"找到音乐下载链接: {audio_url}")
                        
                        if status in ["complete", "SUCCESS"] and has_audio_url:
                            self.update_status(f"音乐任务 {task_id} 完成！耗时: {elapsed_time}秒")
                            # 自动下载音乐 - 传递第一个音乐文件的数据
                            downloaded_path = self.download_music(data_array[0])
                            if downloaded_path:
                                self.update_status(f"音乐下载成功: {downloaded_path}")
                                task_data["local_path"] = downloaded_path
                            return task_data
                        elif status in ["complete", "SUCCESS"]:
                            self.update_status(f"音乐任务 {task_id} 完成！耗时: {elapsed_time}秒")
                            self.update_status("未找到音乐下载链接")
                            return task_data
                        elif status in ["failed", "FAILURE"]:
                            self.update_status(f"音乐任务 {task_id} 失败")
                            return None
                    elif isinstance(task_data, list) and len(task_data) > 0:
                        # 如果data是列表，取第一个元素
                        first_item = task_data[0]
                        self.update_status(f"音乐任务返回列表，第一个元素类型: {type(first_item)}")
                        if isinstance(first_item, dict):
                            status = first_item.get("status", "UNKNOWN")
                            has_audio_url = "audio_url" in first_item
                            self.update_status(f"列表第一个元素状态: {status}, 包含audio_url: {has_audio_url}")
                            
                            if has_audio_url or status in ["complete", "SUCCESS"]:
                                elapsed_time = int(time.time() - start_time)
                                self.update_status(f"音乐任务 {task_id} 完成！耗时: {elapsed_time}秒")
                                # 自动下载音乐
                                downloaded_path = self.download_music(first_item)
                                if downloaded_path:
                                    self.update_status(f"音乐下载成功: {downloaded_path}")
                                    first_item["local_path"] = downloaded_path
                                return first_item
                
            except Exception as e:
                self.update_status(f"检查音乐任务状态时出错: {str(e)}")
            
            # 等待一段时间再检查
            time.sleep(check_interval)
        
        self.update_status(f"音乐任务 {task_id} 超时")
        return None
    
    def download_image(self, task_info: Dict[str, Any]) -> Optional[str]:
        """
        下载图片到本地
        
        Args:
            task_info: 任务信息，包含imageUrl
            
        Returns:
            Optional[str]: 下载的本地文件路径
        """
        try:
            image_url = task_info.get("imageUrl")
            if not image_url:
                self.update_status("未找到图片下载链接")
                return None
            
            # 创建下载目录
            download_dir = "downloads/images"
            os.makedirs(download_dir, exist_ok=True)
            
            # 生成文件名
            task_id = task_info.get("id", "unknown")
            file_extension = ".png"
            if ".jpg" in image_url or ".jpeg" in image_url:
                file_extension = ".jpg"
            elif ".webp" in image_url:
                file_extension = ".webp"
            
            filename = f"cover_{task_id}{file_extension}"
            local_path = os.path.join(download_dir, filename)
            
            # 下载文件
            self.update_status(f"正在下载图片: {image_url}")
            urllib.request.urlretrieve(image_url, local_path)
            
            return local_path
            
        except Exception as e:
            self.update_status(f"下载图片失败: {str(e)}")
            return None
    
    def download_music(self, task_data: Dict[str, Any]) -> Optional[str]:
        """
        下载音乐到本地
        
        Args:
            task_data: 任务数据，包含audio_url
            
        Returns:
            Optional[str]: 下载的本地文件路径
        """
        try:
            audio_url = task_data.get("audio_url")
            if not audio_url:
                self.update_status("未找到音乐下载链接")
                return None
            
            # 创建下载目录
            download_dir = "downloads/music"
            os.makedirs(download_dir, exist_ok=True)
            
            # 生成文件名
            task_id = task_data.get("id", "unknown")
            title = task_data.get("title", "music")
            # 清理文件名中的非法字符
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_title}_{task_id}.mp3"
            local_path = os.path.join(download_dir, filename)
            
            # 下载文件
            self.update_status(f"正在下载音乐: {audio_url}")
            urllib.request.urlretrieve(audio_url, local_path)
            
            return local_path
            
        except Exception as e:
            self.update_status(f"下载音乐失败: {str(e)}")
            return None
    
    def _generate_cover_prompt(self, novel_setup: Dict[str, Any]) -> str:
        """
        根据小说设置生成封面提示词
        
        Args:
            novel_setup: 小说设置信息
            
        Returns:
            str: 生成的提示词
        """
        novel_type = novel_setup.get("novel_type", "玄幻修真")
        protagonist_name = novel_setup.get("protagonist_name", "主角")
        protagonist_age = novel_setup.get("protagonist_age", 25)
        background = novel_setup.get("background", "神秘的世界")
        
        # 根据小说类型生成不同风格的提示词
        type_styles = {
            "奇幻冒险": "fantasy adventure, magical world, epic landscape",
            "都市言情": "modern romance, city skyline, elegant atmosphere",
            "玄幻修真": "xianxia fantasy, cultivation world, mystical mountains",
            "系统流": "fantasy adventure, magical world, epic landscape",
            "科幻未来": "sci-fi futuristic, cyberpunk cityscape, neon lights",
            "悬疑推理": "mystery thriller, dark atmosphere, noir style",
            "历史穿越": "historical fantasy, ancient architecture, time travel",
            "武侠江湖": "wuxia martial arts, ancient China, sword fighting"
        }
        
        style = type_styles.get(novel_type, "fantasy adventure, magical world")
        
        # 根据主角年龄调整描述
        age_desc = "young man" if protagonist_age < 30 else "mature man"
        if protagonist_age < 20:
            age_desc = "teenager"
        
        prompt = f"{style}, handsome {age_desc}, {protagonist_age}, background: {background}, book cover design, high quality, detailed illustration, cinematic lighting, 4K resolution"
        
        return prompt
    
    def _generate_music_prompt(self, novel_setup: Dict[str, Any]) -> str:
        """
        根据小说设置生成音乐提示词
        
        Args:
            novel_setup: 小说设置信息
            
        Returns:
            str: 生成的音乐提示词
        """
        novel_type = novel_setup.get("novel_type", "玄幻修真")
        
        # 根据小说类型生成不同风格的音乐
        type_music = {
            "奇幻冒险": "Epic orchestral music with magical elements, adventure theme",
            "都市言情": "Romantic piano melody with soft strings, modern love theme",
            "玄幻修真": "Ancient Chinese instrumental music with ethereal atmosphere",
            "系统流": "Epic orchestral music",
            "科幻未来": "Electronic synthwave music with futuristic sounds",
            "悬疑推理": "Dark ambient music with mysterious piano notes",
            "历史穿越": "Traditional orchestral music with historical elements",
            "武侠江湖": "Traditional Chinese music with guqin and flute"
        }
        
        return type_music.get(novel_type, "Epic orchestral music")
    
    def save_media_info(self, output_dir: str, novel_setup: Dict[str, Any], 
                       image_results: List[Dict[str, Any]], music_result: Optional[Dict[str, Any]]):
        """
        保存媒体信息到JSON文件
        
        Args:
            output_dir: 输出目录
            novel_setup: 小说设置信息
            image_results: 图片生成结果
            music_result: 音乐生成结果
        """
        try:
            media_info = {
                "novel_info": {
                    "type": novel_setup.get("novel_type", ""),
                    "protagonist": novel_setup.get("protagonist_name", ""),
                    "background": novel_setup.get("background", "")
                },
                "images": [],
                "music": None,
                "generation_time": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 添加图片信息
            for i, img_result in enumerate(image_results):
                image_info = {
                    "index": i + 1,
                    "task_id": img_result.get("id"),
                    "status": img_result.get("status"),
                    "image_url": img_result.get("imageUrl"),
                    "local_path": img_result.get("local_path"),
                    "prompt": img_result.get("prompt"),
                    "progress": img_result.get("progress")
                }
                media_info["images"].append(image_info)
            
            # 添加音乐信息
            if music_result:
                music_info = {
                    "task_id": music_result.get("id"),
                    "title": music_result.get("title"),
                    "audio_url": music_result.get("audio_url"),
                    "local_path": music_result.get("local_path"),
                    "duration": music_result.get("duration")
                }
                media_info["music"] = music_info
            
            # 保存到文件
            media_file_path = os.path.join(output_dir, "media_info.json")
            with open(media_file_path, 'w', encoding='utf-8') as f:
                json.dump(media_info, f, ensure_ascii=False, indent=2)
            
            self.update_status(f"媒体信息已保存到: {media_file_path}")
            
        except Exception as e:
            self.update_status(f"保存媒体信息失败: {str(e)}") 