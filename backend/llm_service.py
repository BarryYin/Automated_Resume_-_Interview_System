#!/usr/bin/env python3
"""
LLM服务 - 集成通义千问Max模型
"""

import openai
import json
import PyPDF2
from pathlib import Path
import re
from config import config

class QwenLLMService:
    def __init__(self):
        # 从配置文件加载API配置
        self.client = openai.OpenAI(
            api_key=config.get('llm.api_key'),
            base_url=config.get('llm.base_url')
        )
        self.model = config.get('llm.model', 'qwen-plus')
        self.temperature = config.get('llm.temperature', 0.7)
        self.max_tokens = config.get('llm.max_tokens', 2000)
        
        # 评估维度定义
        self.evaluation_dimensions = {
            "Knowledge": "专业知识，包括学历、专业技术资格、理论基础",
            "Skill": "专业技能，特别是指具体的、实际操作的能力",
            "Ability": "综合素质与能力，特别是指抽象的能力，以及工作经验",
            "Personality": "个性特质，包括自我定位和性格特点",
            "Motivation": "求职动机，包括离职应聘原因和职业目标",
            "Value": "价值观，也包括个人价值观及对企业文化的认同度"
        }

    def extract_text_from_pdf(self, pdf_path):
        """从PDF简历中提取文本"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            print(f"PDF文本提取失败: {e}")
            return ""

    def generate_interview_questions(self, candidate_info, resume_text, job_description):
        """
        基于候选人信息、简历内容和职位描述生成面试问题
        """
        
        prompt = f"""
你是一位专业的HR面试官，需要为候选人生成10个深度面试问题。

候选人信息：
- 姓名：{candidate_info.get('name', '未知')}
- 应聘职位：{candidate_info.get('position', '未知')}
- 邮箱：{candidate_info.get('email', '未知')}

简历内容：
{resume_text[:2000] if resume_text else '简历内容暂无'}

职位描述：
{job_description[:1000] if job_description else '职位描述暂无'}

请基于以下6个评估维度，结合候选人的简历信息，生成10个针对性的面试问题：

1. Knowledge（专业知识）：专业知识，包括学历、专业技术资格、理论基础
2. Skill（专业技能）：专业技能，特别是指具体的、实际操作的能力  
3. Ability（综合素质与能力）：综合素质与能力，特别是指抽象的能力，以及工作经验
4. Personality（个性特质）：个性特质，包括自我定位和性格特点
5. Motivation（求职动机）：求职动机，包括离职应聘原因和职业目标
6. Value（价值观）：价值观，也包括个人价值观及对企业文化的认同度

要求：
- 每个维度至少1-2个问题
- 问题要结合候选人简历中的具体信息进行追问
- 问题要有深度，能够有效评估候选人的能力
- 问题要自然流畅，符合面试场景
- 总共10个问题

请按以下JSON格式返回：
{{
    "questions": [
        {{
            "id": 1,
            "dimension": "Knowledge",
            "question": "具体问题内容",
            "follow_up": "可能的追问方向"
        }},
        ...
    ],
    "interview_strategy": "整体面试策略建议"
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位经验丰富的HR面试专家，擅长根据候选人背景设计深度面试问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # 尝试解析JSON响应
            try:
                # 提取JSON部分
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return result
                else:
                    # 如果没有找到JSON，返回默认结构
                    return self._parse_text_response(content)
            except json.JSONDecodeError:
                return self._parse_text_response(content)
                
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return self._generate_fallback_questions(candidate_info)

    def _parse_text_response(self, content):
        """解析文本响应为结构化数据"""
        questions = []
        lines = content.split('\n')
        
        current_question = None
        question_id = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 检测问题行
            if any(keyword in line.lower() for keyword in ['问题', 'question', '？', '?']):
                if current_question:
                    questions.append(current_question)
                
                # 确定维度
                dimension = "Knowledge"  # 默认维度
                for dim in self.evaluation_dimensions.keys():
                    if dim.lower() in line.lower() or self.evaluation_dimensions[dim][:2] in line:
                        dimension = dim
                        break
                
                current_question = {
                    "id": question_id,
                    "dimension": dimension,
                    "question": line,
                    "follow_up": ""
                }
                question_id += 1
        
        if current_question:
            questions.append(current_question)
        
        # 确保有10个问题
        while len(questions) < 10:
            questions.append({
                "id": len(questions) + 1,
                "dimension": "Knowledge",
                "question": f"请谈谈您在专业领域的理解和经验。",
                "follow_up": "可以具体举例说明"
            })
        
        return {
            "questions": questions[:10],
            "interview_strategy": "基于候选人背景进行深度交流，重点关注专业能力和文化匹配度。"
        }

    def regenerate_questions_with_feedback(self, candidate_info, resume_text, job_description, feedback):
        """根据管理员反馈重新生成面试问题"""
        
        prompt = f"""
你是一位专业的HR面试官，需要根据管理员的反馈意见，为候选人重新生成10个深度面试问题。

候选人信息：
- 姓名：{candidate_info.get('name', '未知')}
- 应聘职位：{candidate_info.get('position', '未知')}
- 邮箱：{candidate_info.get('email', '未知')}

简历内容：
{resume_text[:2000] if resume_text else '简历内容暂无'}

职位描述：
{job_description[:1000] if job_description else '职位描述暂无'}

管理员反馈意见：
{feedback}

请基于以下6个评估维度，结合候选人的简历信息和管理员的反馈意见，重新生成10个针对性的面试问题：

1. Knowledge（专业知识）：专业知识，包括学历、专业技术资格、理论基础
2. Skill（专业技能）：专业技能，特别是指具体的、实际操作的能力  
3. Ability（综合素质与能力）：综合素质与能力，特别是指抽象的能力，以及工作经验
4. Personality（个性特质）：个性特质，包括自我定位和性格特点
5. Motivation（求职动机）：求职动机，包括离职应聘原因和职业目标
6. Value（价值观）：价值观，也包括个人价值观及对企业文化的认同度

要求：
- 每个维度至少1-2个问题
- 问题要结合候选人简历中的具体信息进行追问
- 问题要有深度，能够有效评估候选人的能力
- 问题要自然流畅，符合面试场景
- 特别注意管理员的反馈意见，针对性地调整问题
- 总共10个问题

请按以下JSON格式返回：
{{
    "questions": [
        {{
            "id": 1,
            "dimension": "Knowledge",
            "question": "具体问题内容",
            "follow_up": "可能的追问方向"
        }},
        ...
    ],
    "interview_strategy": "整体面试策略建议"
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位经验丰富的HR面试专家，擅长根据候选人背景和反馈意见设计深度面试问题。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # 尝试解析JSON响应
            try:
                # 提取JSON部分
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return result
                else:
                    # 如果没有找到JSON，返回默认结构
                    return self._parse_text_response(content)
            except json.JSONDecodeError:
                return self._parse_text_response(content)
                
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return self._generate_fallback_questions(candidate_info)

    def _generate_fallback_questions(self, candidate_info):
        """生成备用问题"""
        position = candidate_info.get('position', '该职位')
        
        fallback_questions = [
            {
                "id": 1,
                "dimension": "Knowledge",
                "question": f"请介绍一下您在{position}相关领域的专业知识背景。",
                "follow_up": "可以具体谈谈您的学习经历和专业认证"
            },
            {
                "id": 2,
                "dimension": "Skill",
                "question": f"请描述一个您在{position}工作中解决的具体技术问题。",
                "follow_up": "当时是如何分析和解决这个问题的？"
            },
            {
                "id": 3,
                "dimension": "Ability",
                "question": "请谈谈您在团队协作中的经验和收获。",
                "follow_up": "遇到团队冲突时您是如何处理的？"
            },
            {
                "id": 4,
                "dimension": "Personality",
                "question": "您认为自己最大的优势和需要改进的地方是什么？",
                "follow_up": "能举个具体例子说明吗？"
            },
            {
                "id": 5,
                "dimension": "Motivation",
                "question": f"是什么促使您选择应聘{position}这个职位？",
                "follow_up": "您的职业规划是怎样的？"
            },
            {
                "id": 6,
                "dimension": "Value",
                "question": "您理想的工作环境和企业文化是什么样的？",
                "follow_up": "您如何看待工作与生活的平衡？"
            },
            {
                "id": 7,
                "dimension": "Knowledge",
                "question": "请谈谈您对行业发展趋势的看法。",
                "follow_up": "您是如何保持专业知识更新的？"
            },
            {
                "id": 8,
                "dimension": "Skill",
                "question": "请描述一个您最有成就感的项目经历。",
                "follow_up": "在这个项目中您承担了什么角色？"
            },
            {
                "id": 9,
                "dimension": "Ability",
                "question": "面对压力和挑战时，您通常如何应对？",
                "follow_up": "能分享一个具体的例子吗？"
            },
            {
                "id": 10,
                "dimension": "Motivation",
                "question": "您希望在我们公司获得什么样的发展机会？",
                "follow_up": "您认为自己能为公司带来什么价值？"
            }
        ]
        
        return {
            "questions": fallback_questions,
            "interview_strategy": "通过多维度问题全面了解候选人的专业能力、个人特质和发展潜力。"
        }

    def evaluate_answer(self, question, answer, dimension):
        """
        评估候选人回答并给出分数
        """
        
        prompt = f"""
请作为专业的HR评估专家，对候选人的面试回答进行评分。

评估维度：{dimension} - {self.evaluation_dimensions.get(dimension, '')}

面试问题：{question}

候选人回答：{answer}

请从以下几个方面进行评估：
1. 回答的完整性和逻辑性
2. 专业知识的深度和准确性
3. 表达能力和沟通技巧
4. 与岗位要求的匹配度
5. 回答的真实性和可信度

请给出0-100分的评分，并提供简要的评估理由。

请按以下JSON格式返回：
{{
    "score": 85,
    "feedback": "评估理由和建议",
    "strengths": ["优势点1", "优势点2"],
    "improvements": ["改进建议1", "改进建议2"]
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一位专业的HR评估专家，能够客观公正地评估候选人的面试表现。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            # 尝试解析JSON响应
            try:
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                    return result
            except json.JSONDecodeError:
                pass
            
            # 如果解析失败，返回默认评分
            return {
                "score": 75,
                "feedback": "回答基本符合要求，表达清晰。",
                "strengths": ["表达清晰"],
                "improvements": ["可以更加具体"]
            }
                
        except Exception as e:
            print(f"评估回答时出错: {e}")
            return {
                "score": 70,
                "feedback": "系统评估异常，建议人工复核。",
                "strengths": [],
                "improvements": []
            }

# 创建全局LLM服务实例
llm_service = QwenLLMService()