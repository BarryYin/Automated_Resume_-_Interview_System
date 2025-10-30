import os
import json
import re
from pathlib import Path
from typing import Dict, Optional
import pdfplumber
import docx
from llm_service import llm_service

class ResumeParser:
    def __init__(self):
        self.upload_dir = Path("uploads/resumes")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """从PDF文件提取文本"""
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            print(f"PDF解析失败: {e}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """从Word文档提取文本"""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Word文档解析失败: {e}")
            return ""
    
    def extract_text_from_file(self, file_path: str) -> str:
        """根据文件类型提取文本"""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            return self.extract_text_from_docx(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")
    
    def parse_resume_with_ai(self, resume_text: str) -> Dict:
        """使用AI解析简历内容"""
        prompt = f"""
请分析以下简历内容，提取关键信息并以JSON格式返回。请严格按照以下格式返回，如果某个字段无法确定，请返回空字符串：

{{
    "name": "姓名",
    "email": "邮箱地址", 
    "phone": "电话号码",
    "education": "最高学历（如：本科、硕士、博士）",
    "experience": "工作经验年限（如：3年、5年经验）",
    "skills": "主要技能（用逗号分隔）",
    "current_position": "当前或最近职位",
    "expected_salary": "期望薪资（如果有提到）",
    "summary": "个人简介或亮点总结（1-2句话）"
}}

简历内容：
{resume_text}

请只返回JSON格式的结果，不要包含其他说明文字。
"""
        
        try:
            # 调用AI服务
            response = llm_service.chat(prompt)
            
            # 尝试解析JSON
            # 清理响应文本，移除可能的markdown标记
            clean_response = response.strip()
            if clean_response.startswith('```json'):
                clean_response = clean_response[7:]
            if clean_response.endswith('```'):
                clean_response = clean_response[:-3]
            clean_response = clean_response.strip()
            
            parsed_data = json.loads(clean_response)
            
            # 验证和清理数据
            return self.validate_parsed_data(parsed_data)
            
        except json.JSONDecodeError as e:
            print(f"AI返回的JSON格式错误: {e}")
            print(f"原始响应: {response}")
            return self.get_empty_candidate_data()
        except Exception as e:
            print(f"AI解析失败: {e}")
            return self.get_empty_candidate_data()
    
    def validate_parsed_data(self, data: Dict) -> Dict:
        """验证和清理解析的数据"""
        # 定义默认结构
        default_data = self.get_empty_candidate_data()
        
        # 合并数据，确保所有字段都存在
        for key in default_data.keys():
            if key in data and data[key]:
                default_data[key] = str(data[key]).strip()
        
        # 特殊处理邮箱格式
        if default_data['email']:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            email_match = re.search(email_pattern, default_data['email'])
            if email_match:
                default_data['email'] = email_match.group()
            else:
                default_data['email'] = ""
        
        # 特殊处理电话号码
        if default_data['phone']:
            phone_pattern = r'1[3-9]\d{9}'
            phone_match = re.search(phone_pattern, default_data['phone'])
            if phone_match:
                default_data['phone'] = phone_match.group()
        
        return default_data
    
    def get_empty_candidate_data(self) -> Dict:
        """返回空的候选人数据结构"""
        return {
            "name": "",
            "email": "",
            "phone": "",
            "education": "",
            "experience": "",
            "skills": "",
            "current_position": "",
            "expected_salary": "",
            "summary": ""
        }
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """保存上传的文件"""
        # 生成唯一文件名
        import uuid
        file_ext = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = self.upload_dir / unique_filename
        
        # 保存文件
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return str(file_path)
    
    def parse_resume_file(self, file_content: bytes, filename: str) -> Dict:
        """解析简历文件的完整流程"""
        try:
            # 1. 保存文件
            file_path = self.save_uploaded_file(file_content, filename)
            
            # 2. 提取文本
            resume_text = self.extract_text_from_file(file_path)
            
            if not resume_text.strip():
                return {
                    "success": False,
                    "message": "无法从文件中提取文本内容",
                    "data": self.get_empty_candidate_data()
                }
            
            # 3. AI解析
            parsed_data = self.parse_resume_with_ai(resume_text)
            
            # 4. 添加文件路径
            parsed_data["resume_file_path"] = file_path
            
            return {
                "success": True,
                "message": "简历解析成功",
                "data": parsed_data,
                "extracted_text": resume_text[:500] + "..." if len(resume_text) > 500 else resume_text
            }
            
        except Exception as e:
            print(f"简历解析失败: {e}")
            return {
                "success": False,
                "message": f"简历解析失败: {str(e)}",
                "data": self.get_empty_candidate_data()
            }

# 创建全局实例
resume_parser = ResumeParser()